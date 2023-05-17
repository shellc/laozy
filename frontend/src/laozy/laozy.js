import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';

import { Layout, Menu, theme } from 'antd'
import {

} from '@ant-design/icons';

import { useState } from 'react'

import { Developer } from './developer.js'

const { Sider, Content } = Layout

const LaozyApp = () => {
    const [collapsed, setCollapsed] = useState(false);
    const [content, setContent] = useState(false);

    const {
        token: { colorBgContainer },
    } = theme.useToken();

    const onClick = (e) => {
        loadComponent(e.key);
    }

    const loadComponent = (key) => {
        switch (key) {
            case 'developer': setContent(<Developer />); break;
            default:
                setContent(`Unkonw component: ${key}`);
        }
    }

    useEffect(() => {
        loadComponent('developer');
    }, [])

    return (
        <Layout
            hasSider
            style={{
                minHeight: '100vh',
            }}
        >
            <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)} breakpoint="lg"
                style={{
                    overflow: 'auto',
                    height: '100vh',
                }}
            >
                <div className="logo">

                </div>
                <Menu
                    onClick={onClick}
                    theme="dark"
                    mode="inline"
                    defaultSelectedKeys={['developer']}
                    items={[
                        {
                            key: 'dashboard',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-gauge-high"></i></span>,
                            label: '首页',
                        },
                        {
                            key: 'developer',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-bolt-lightning"></i></span>,
                            label: '调试助手',
                        },
                        {
                            key: 'review',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-comments"></i></span>,
                            label: '消息评审',
                        },
                        {
                            key: '3',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-brain" /></span>,
                            label: '知识库',
                        },
                        {
                            key: '7',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-plug"></i></span>,
                            label: '消息接口',
                        },
                        {
                            key: '4',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-tower-broadcast"></i></span>,
                            label: '频道',
                        },
                        {
                            key: '6',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-robot"></i></span>,
                            label: '机器人',
                        },
                        {
                            key: '5',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-square-root-variable"></i></span>,
                            label: '机器人模板',
                        },
                        {
                            key: '8',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-gear"></i></span>,
                            label: '设置',
                        },
                    ]}
                />
            </Sider>
            <Layout
                id="content"
                style={{
                    
                }}
            >
                {content}
            </Layout>
        </Layout>
    );
}

const createLaozy = (elementId) => {
    const root = ReactDOM.createRoot(document.getElementById(elementId));
    root.render(
        <React.StrictMode>
            <LaozyApp />
        </React.StrictMode>
    );
}

export default { createLaozy };