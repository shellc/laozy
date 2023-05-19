import React, { useEffect } from 'react';
import ReactDOM from 'react-dom/client';

import { Layout, Menu, theme } from 'antd'
import {

} from '@ant-design/icons';

import { useState } from 'react'

import { Developer } from './developer.js'
import { PromptTemplateListAndEditView } from './prompts.js';
import { RobotListAndEditView } from './robots.js';
import { ChannelListAndEditView } from './channels.js';
import { RouteListAndEditView } from './routes.js';
const { Sider, Content } = Layout

const LaozyApp = () => {
    const [collapsed, setCollapsed] = useState(false);
    const [activated, setActivated] = useState(null);
    const [content, setContent] = useState(false);

    const {
        token: { colorBgContainer },
    } = theme.useToken();

    const onClick = (e) => {
        loadComponent(e.key);
    }

    const loadComponent = (key) => {
        setActivated(key);
        switch (key) {
            case 'developer': setContent(<Developer />); break;
            case 'prompts': setContent(<PromptTemplateListAndEditView />); break;
            case 'robots': setContent(<RobotListAndEditView />); break;
            case 'channels': setContent(<ChannelListAndEditView />); break;
            case 'routes': setContent(<RouteListAndEditView />); break;
            default:
                setContent(
                    <div className='p-5'>The feature has not been implemented yet..</div>
                );
        }
        localStorage.setItem('laozy_activated_component_key', key);
    }

    useEffect(() => {
        let key = localStorage.getItem('laozy_activated_component_key');
        loadComponent(key ? key : 'dashboard');
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
                    //defaultSelectedKeys={['dashboard']}
                    selectedKeys={[activated,]}
                    items={[
                        {
                            key: 'dashboard',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-gauge-high"></i></span>,
                            label: 'Home',
                        },
                        {
                            key: 'developer',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-bolt-lightning"></i></span>,
                            label: 'Developer',
                        },
                        {
                            key: 'review',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-comments"></i></span>,
                            label: 'Review',
                        },
                        {
                            key: '3',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-brain" /></span>,
                            label: 'Knowledges',
                        },
                        {
                            key: 'channels_group',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-tower-broadcast"></i></span>,
                            label: 'Channels',
                            children: [
                                {
                                    key: 'routes',
                                    icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-plug"></i></span>,
                                    label: 'Connectors',
                                },
                                {
                                    key: 'channels',
                                    icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-tower-broadcast"></i></span>,
                                    label: 'Channels',
                                },
                            ]
                        },
                        
                        {
                            key: 'robots_group',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-robot"></i></span>,
                            label: 'Rotots',
                            children: [
                                {
                                    key: 'robots',
                                    icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-robot"></i></span>,
                                    label: 'Rotots',
                                },
                                {
                                    key: 'prompts',
                                    icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-square-root-variable"></i></span>,
                                    label: 'Prompts',
                                },
                            ]
                        },
                        {
                            key: '8',
                            icon: <span className="ant-menu-item-icon"><i className="fa-solid fa-gear"></i></span>,
                            label: 'Settings',
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