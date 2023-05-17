import time
import random
from typing import Union
from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, AuthenticationError, SimpleUser
)
import base64
import binascii

from starlette.authentication import requires
from fastapi import Request, Response, status, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from captcha.image import ImageCaptcha

from .. import settings, utils
from .. import api
from ..db import users, invitations, tokens
from ..utils import uuid, sha256

# Generate a CAPTCHA
# async def get_captcha(rqeust: Request):
#    pass

secrect_key = settings.get('SECRECT_KEY')


@api.entry.get("/captcha")
async def genereate_captcha():
    chars = []
    for i in range(4):
        chars.append(chr(random.randint(65, 90)))

    img = ImageCaptcha(width=180, height=60, font_sizes=[48])
    data = img.generate(chars=chars)

    headers = {
        'Content-Type': 'image/png',
        'X-Captcha-Signature': utils.captcha_sign(secrect_key, ''.join(chars))
    }
    print(''.join(chars), headers)
    return StreamingResponse(content=data, headers=headers)


class RegisterModel(BaseModel):
    username: str
    is_mobile: Union[str, None] = False
    password: str
    invitation_code: Union[str, None] = None
    captcha: str
    captcha_signature: str


@api.entry.post('/users', status_code=status.HTTP_201_CREATED)
async def create_user(register: RegisterModel):
    bad_request = HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    # Validate CAPTCHA
    captcha_sign = utils.captcha_sign(secrect_key, register.captcha)
    if captcha_sign != register.captcha_signature:
        print(register.captcha, captcha_sign, register.captcha_signature)
        raise bad_request

    # Validate invitation code
    if not register.invitation_code:
        raise bad_request
    invit = await invitations.get(register.invitation_code)
    if not invit or invit.invalid:
        raise bad_request

    # Check inputs
    username = register.username
    if not utils.validate_username(username) or not register.password or not register.captcha:
        raise bad_request

    # Check username
    user = await users.getbyusername(username)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    salt = uuid()
    password = utils.password(salt, register.password)
    await users.create(id=uuid(), username=username, salt=salt, password=password, created_time=int(time.time()))

    # Invalid invitation code
    await invitations.invalid(invit.id)


class UserModel(BaseModel):
    id: str
    username: str


@api.entry.get('/users/{userid}')
async def get_user(userid: str):
    u = await users.get(userid)
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return UserModel(id=u.id, username=u.username)


class Credential(BaseModel):
    username: Union[str, None] = None
    is_mobile: Union[bool, None] = False
    password: Union[str, None] = None
    captcha: Union[str, None] = None
    captcha_signature: Union[str, None] = None
    token: Union[str, None] = None

@api.entry.post('/users/tokens')
# @requires('authenticated')
async def create_token(credential: Union[Credential, None] = None):
    err = HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if credential:
        username = None

        # Validate token
        if credential.token:
            token = tokens.get(credential.token)
            if not token or token.expires_at > int(time.time()):
                raise err
            username = token.username
        else:
            username = credential.username
            # Validate username and password
            captcha_sign = utils.captcha_sign(secrect_key, credential.captcha)
            if captcha_sign != credential.captcha_signature:
                raise err
        
        if not username:
            raise err
        
        user = await users.getbyusername(username)
        if user:
            password = utils.password(user.salt, credential.password)
            if user.password == password:
                token = uuid()
                created = int(time.time())
                expires_at = created + 7200
                await tokens.create(id=token, userid=user.id, created_time=created, expires_at=expires_at)
                return {
                    "userid": user.id,
                    "username": user.username,
                    "token": token,
                    "created": created,
                    "expires_at": expires_at
                }

    raise err

class AuthenticatedUser(SimpleUser):
    def __init__(self, id:str, username: str = None) -> None:
        super().__init__(username)
        self.id = id

    @property
    def userid(self):
        return self.id

class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        token = None
        if "Authorization" in request.headers:
            auth = request.headers["Authorization"]
           
            scheme, credentials = auth.split()
            if scheme.lower() == 'Bearer':
                token = credentials
        else:
            token = request.cookies.get('token')

        if token:
            t = await tokens.get(token)
            if t and t.expires_at > int(time.time()):
                return AuthCredentials(["authenticated"]), AuthenticatedUser(t.userid)
