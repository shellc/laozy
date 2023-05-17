import uuid as _uuid
import hashlib
import re

namespace = _uuid.uuid1()


def uuid():
    return _uuid.uuid5(namespace, _uuid.uuid1().hex).hex


def sha1(s: str):
    m = hashlib.sha1()
    m.update(s.encode())
    return m.hexdigest()


def sha256(s: str):
    m = hashlib.sha256()
    m.update(s.encode())
    return m.hexdigest()


def captcha_sign(key, captcha):
    return sha256("%s%s" % (key, captcha))


def password(salt, password):
    return sha256("%s:%s" % (salt, password))


username_regex = re.compile("^[a-zA-Z0-9_]*$")


def validate_username(username):
    return username_regex.match(username)
