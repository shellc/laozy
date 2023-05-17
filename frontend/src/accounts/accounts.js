import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';
import {
    Form
} from 'antd';

import { encode_base64 } from '../uitils/image';
import { sha256 } from '../uitils/crypto'

import Cookies from 'js-cookie'

const autoRefreshToken = () => {
    let token = Cookies.get('token');
    let expires_at = Cookies.get('expires_at');
    let now = Math.round(new Date().getTime() / 1000);

    if (token && expires_at && expires_at - now < 7200 - 60) {
        let req = {
            token: token,
        };

        fetch("/api/users/tokens", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(req),
        }).then(r => {
            if (r.status == 200) {
                return r.json();
            } else {
                window.location.href = '/accounts/login?next=' + window.location.href;
            }
        }).then(data => {
            Cookies.set('userid', data.userid);
            Cookies.set('username', data.username);
            Cookies.set('token', data.token);

            let now = Math.round(new Date().getTime() / 1000);
            Cookies.set('created', now);
            Cookies.set('expires_at', now + (data.expires_at - data.created));
            
            setTimeout(autoRefreshToken, 30);
        }).catch(e => {
            window.location.href = '/accounts/login?next=' + window.location.href;
        });
    } else {
        window.location.href = '/accounts/login?next=' + window.location.href;
    }
}

const LoginForm = (props) => {
    const [captchaSignature, setCaptchaSignature] = useState('');
    const [captchaData, setCaptchaData] = useState();
    const [error, setError] = useState();

    const reloadCaptcha = () => {
        fetch("/api/captcha").then(r => {
            setCaptchaSignature(r.headers.get('X-Captcha-Signature'));
            return r.arrayBuffer();
        }).then(data => {
            setCaptchaData("data:image/png;base64," + encode_base64(data));
        });
    }

    const login = (e) => {
        e.preventDefault();

        let req = {
            username: e.target.username.value,
            password: e.target.password.value,
            captcha: e.target.captcha.value,
            captcha_signature: captchaSignature,
        };
        sha256(req.password).then(password_sha256 => {
            req.password = password_sha256;

            fetch("/api/users/tokens", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(req),
            }).then(r => {
                if (r.status == 200) {
                    return r.json();
                } else {
                    setError("登录失败，请检查用户名、密码和验证码是否正确。")
                }
            }).then(data => {
                Cookies.set('userid', data.userid);
                Cookies.set('username', data.username);
                Cookies.set('token', data.token);
                Cookies.set('created', data.created);
                Cookies.set('expires_at', data.expires_at);
                window.location.href = props.next ? props.next : '/';
            })
                .catch(e => {
                    console.log(e);
                    setError("发生未知错误！");
                });
        });
    }

    useEffect(() => {
        reloadCaptcha();
    }, []);

    return (
        <form onSubmit={login} className='needs-validation'>
            {error ? (
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            ) : null}
            <div>
                <div className="mb-4">
                    <input type="text" className="form-control" id="username" name="username" placeholder="用户名" required></input>
                </div>
                <div className="mb-4">
                    <input type="password" className="form-control" name="password" placeholder="密码" required></input>
                </div>
                <div className="input-group mb-4">
                    <input type="captcha" className="form-control" name="captcha" placeholder="验证码" required></input>
                    <span className='input-group-text p-0'><img src={captchaData} style={{ height: '30px' }} onClick={reloadCaptcha} /></span>
                </div>
                <input type='hidden' name='captcha_signature' value={captchaSignature} />
                <button type="submit" className="btn btn-primary w-100">登录</button>
            </div>
        </form>
    )
}

const RegisterForm = (props) => {
    const [captchaSignature, setCaptchaSignature] = useState('');
    const [captchaData, setCaptchaData] = useState();
    const [error, setError] = useState();

    const reloadCaptcha = () => {
        fetch("/api/captcha").then(r => {
            setCaptchaSignature(r.headers.get('X-Captcha-Signature'));
            return r.arrayBuffer();
        }).then(data => {
            setCaptchaData("data:image/png;base64," + encode_base64(data));
        });
    }

    const register = (e) => {
        e.preventDefault();

        let password = e.target.password.value;
        if (password != e.target.password_confirm.value) {
            setError("两次输入的密码必须相同。");

        }

        let req = {
            username: e.target.username.value,
            password: e.target.password.value,
            captcha: e.target.captcha.value,
            captcha_signature: captchaSignature,
            invitation_code: e.target.invitation_code.value,
        };
        sha256(password).then(password_sha256 => {
            req.password = password_sha256;

            fetch("/api/users", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(req),
            }).then(r => {
                if (r.status == 201) {
                    window.location.href = props.next ? props.next : '/accounts/login';
                } else if (r.status == '409') {
                    setError("用户已存在。");
                } else {
                    setError("发生错误，请检查您的输入！");
                }
            })
                .catch(e => {
                    console.log(e);
                    setError("发生未知错误！");
                });
        });
    }

    useEffect(() => {
        reloadCaptcha();
    }, []);

    return (
        <form onSubmit={register} className='needs-validation'>
            {error ? (
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            ) : null}

            <div>
                <div className="mb-4">
                    <input type="text" className="form-control" id="username" name="username" placeholder="用户名" required></input>
                </div>
                <div className="mb-4">
                    <input type="password" className="form-control" name="password" placeholder="密码" required></input>
                </div>
                <div className="mb-4">
                    <input type="password" className="form-control" name="password_confirm" placeholder="确认密码" required></input>
                </div>
                <div className="input-group mb-4">
                    <input type="captcha" className="form-control" name="captcha" placeholder="验证码" required></input>
                    <span className='input-group-text p-0'><img src={captchaData} style={{ height: '30px' }} onClick={reloadCaptcha} /></span>
                </div>
                <div className="mb-4">
                    <input type="text" className="form-control" name="invitation_code" placeholder="邀请码" required></input>
                </div>
                <input type='hidden' name='captcha_signature' value={captchaSignature} />
                <button type="submit" className="btn btn-primary w-100">注册</button>
            </div>
        </form>
    )
}

const AccountComponent = (props) => {
    const [register, setRegister] = useState(props.register);

    return (<div>
        {register ? (
            <div>
                <h1 className='mb-4 text-center fs-5 fw-normal'><i className="fa-solid fa-user-plus"></i> 注册新用户</h1>
                <RegisterForm next={props.next} />
                <div className='mt-3'>
                    已经有账号了，<a href="#" onClick={() => setRegister(false)}>点这里登录</a>。
                </div>
            </div>
        ) : (
            <div>
                <h1 className='mb-4 text-center fs-5 fw-normal'><i className="fa-solid fa-user"></i> 登录</h1>
                <LoginForm next={props.next} />
                <div className='mt-3'>
                    还没有账号，<a href="#" onClick={() => setRegister(true)}>点这里注册</a>。
                </div>
            </div>
        )}
    </div>);
}
const createAccountComponent = (elementId) => {
    const root = ReactDOM.createRoot(document.getElementById(elementId));
    root.render(
        <React.StrictMode>
            <AccountComponent />
        </React.StrictMode>
    );
}

export default { createAccountComponent, autoRefreshToken };