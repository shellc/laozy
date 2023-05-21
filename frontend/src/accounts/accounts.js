import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';

import { encode_base64 } from '../uitils/image';
import { sha256 } from '../uitils/crypto'

import Cookies from 'js-cookie'

const autoRefreshToken = () => {
    let token = Cookies.get('token');
    let expires_at = Cookies.get('expires_at');
    let now = Math.round(new Date().getTime() / 1000);

    if (!token) {
        window.location.href = '/accounts/login?next=' + window.location.href;
    }

    if (token && expires_at && expires_at - now < 60) {
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
            if (r.status === 200) {
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
        }).catch(e => {
            window.location.href = '/accounts/login?next=' + window.location.href;
        });
    }

    setTimeout(autoRefreshToken, 30);
}

const LoginForm = (props) => {
    const [captchaSignature, setCaptchaSignature] = useState('');
    const [captchaData, setCaptchaData] = useState();
    const [error, setError] = useState();

    const reloadCaptcha = () => {
        let form = document.getElementById('signin-form');

        sha256(form.password.value).then(pwd => {
            sha256(form.username.value + pwd).then(signature => {
                fetch(`/api/captcha?signature=${signature}`).then(r => {
                    setCaptchaSignature(r.headers.get('X-Captcha-Signature'));
                    return r.arrayBuffer();
                }).then(data => {
                    setCaptchaData("data:image/png;base64," + encode_base64(data));
                });
            });
        });
    }

    const onChange = (e) => {
        reloadCaptcha();
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
                if (r.status === 200) {
                    return r.json();
                } else {
                    setError("Login failed, please check if the username, password, and verification code are correct.")
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
                    setError("An unknown error has occurred!");
                });
        });
    }

    useEffect(() => {
        reloadCaptcha();
    }, []);

    return (
        <form id='signin-form' onSubmit={login} className='needs-validation'>
            {error ? (
                <div className="alert alert-danger" role="alert">
                    {error}
                </div>
            ) : null}
            <div>
                <div className="mb-4">
                    <i className="fa-solid fa-circle-user position-absolute ps-2 text-secondary" style={{lineHeight: '2.5rem'}}></i>
                    <input type="text" className="form-control ps-4" id="username" name="username" placeholder="Username" required onBlur={onChange}></input>
                </div>
                <div className="mb-4">
                    <i className="fa-solid fa-key position-absolute ps-2 text-secondary" style={{lineHeight: '2.5rem'}}></i>
                    <input type="password" className="form-control ps-4" name="password" placeholder="Password" required onBlur={onChange}></input>
                </div>
                <div className="input-group mb-4">
                    <input type="captcha" className="form-control" name="captcha" placeholder="CAPTCHA" required></input>
                    <span className='input-group-text p-0'><img alt="" src={captchaData} style={{ height: '30px' }} onClick={onChange} /></span>
                </div>
                <input type='hidden' name='captcha_signature' value={captchaSignature} />
                <button type="submit" className="btn btn-primary w-100">Sign in</button>
            </div>
        </form>
    )
}

const RegisterForm = (props) => {
    const [captchaSignature, setCaptchaSignature] = useState('');
    const [captchaData, setCaptchaData] = useState();
    const [error, setError] = useState();
    const [formData, setFormData] = useState({});

    const reloadCaptcha = (signature = '') => {
        fetch(`/api/captcha?signature=${signature}`).then(r => {
            setCaptchaSignature(r.headers.get('X-Captcha-Signature'));
            return r.arrayBuffer();
        }).then(data => {
            setCaptchaData("data:image/png;base64," + encode_base64(data));
        });
    }

    const onChange = (e) => {
        formData[e.target.name] = e.target.value;
        sha256(formData['password']).then(pwd => {
            sha256(formData['username'] + pwd).then(s => reloadCaptcha(s));
        });
    }

    const register = (e) => {
        e.preventDefault();

        let password = e.target.password.value;
        if (password !== e.target.password_confirm.value) {
            setError("The passwords entered twice must be the same.");

        }

        let req = {
            username: e.target.username.value,
            password: e.target.password.value,
            captcha: e.target.captcha.value,
            captcha_signature: captchaSignature,
            invitation_code: e.target.invitation_code ? e.target.invitation_code.value : null,
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
                if (r.status === 201) {
                    window.location.href = props.next ? props.next : '/accounts/login';
                } else if (r.status === '409') {
                    setError("The user already exists.");
                } else {
                    setError("An error has occurred, please check your input!");
                }
            })
                .catch(e => {
                    console.log(e);
                    setError("An unknown error has occurred!");
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
                    <input type="text" className="form-control" id="username" name="username" placeholder="Username" required onBlur={onChange}></input>
                </div>
                <div className="mb-4">
                    <input type="password" className="form-control" name="password" placeholder="Password" required onBlur={onChange}></input>
                </div>
                <div className="mb-4">
                    <input type="password" className="form-control" name="password_confirm" placeholder="Confirm your password" required></input>
                </div>
                <div className="input-group mb-4">
                    <input type="captcha" className="form-control" name="captcha" placeholder="CAPTACHA" required></input>
                    <span className='input-group-text p-0'><img alt='' src={captchaData} style={{ height: '30px' }} onClick={onChange} /></span>
                </div>
                {props.invitation_required ? (
                    <div className="mb-4">
                        <input type="text" className="form-control" name="invitation_code" placeholder="Invitaion Code" required></input>
                    </div>
                ) : null}

                <input type='hidden' name='captcha_signature' value={captchaSignature} />
                <button type="submit" className="btn btn-primary w-100">Sign up</button>
            </div>
        </form>
    )
}

const AccountComponent = (props) => {
    const [register, setRegister] = useState(props.default_view === 'register');

    return (<div>
        {register ? (
            <div>
                <h1 className='mb-4 text-center fs-5 fw-normal'><i className="fa-solid fa-user-plus"></i> Sign up</h1>
                <RegisterForm next={props.next} invitation_required={props.invitation_required} />
                <div className='mt-3'>
                    Already have an account, <a href="#" onClick={() => setRegister(false)}>Sign in</a>.
                </div>
            </div>
        ) : (
            <div>
                <h1 className='mb-4 text-center fs-5 fw-normal'><i className="fa-solid fa-user"></i> Sign in</h1>
                <LoginForm next={props.next} />
                <div className='mt-3'>
                    Don't have an account yet, <a href="#" onClick={() => setRegister(true)}>Sign up</a>.
                </div>
            </div>
        )}
    </div>);
}
const createAccountComponent = (elementId, default_view = 'register', invitation_required = false, next = null) => {
    const root = ReactDOM.createRoot(document.getElementById(elementId));
    root.render(
        <React.StrictMode>
            <AccountComponent default_view={default_view} invitation_required={invitation_required} next={next} />
        </React.StrictMode>
    );
}

export default { createAccountComponent, autoRefreshToken };