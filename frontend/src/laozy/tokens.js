import React, { useEffect } from 'react'
//import { useState } from 'react'

import {
    Button,
    Modal,
    Alert
} from 'antd'
import Cookies from 'js-cookie';

export const TokenList = () => {
    
    const create_token = () => {
        let req = {
            token: Cookies.get('token'),
            expires_at: Math.round(new Date().getTime() / 1000) + 365 * 10 * 86400
        };

        fetch("/api/users/tokens", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(req),
        }).then(r => r.json()).then(token => {
            Modal.info({
                title: 'Your token, remember it:',
                content: (
                    <Alert message={token.token} type="success" />
                ),
                onOk() { },
            })
        })

    }
    return (
        <div>
            <div className='mt-4 ps-4'>
                <Button type='dashed' onClick={create_token}>
                    <i className="fa-solid fa-circle-plus me-2"></i> Create token
                </Button>
            </div>
        </div>
    );
}