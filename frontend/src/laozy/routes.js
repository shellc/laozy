import React, { useEffect } from 'react'
import { useState } from 'react'

import {
    message,
    Form,
    Input,
    Button,
    Select
} from 'antd'

import { ListAndEditView } from './list_edit_view';

const { TextArea } = Input;

export const RouteListAndEditView = () => {
    const loadRoutes = (setState) => {
        fetch('/api/routes').then(r => r.json()).then(data => setState(data));
    }

    const deleteItem = (i) => {
        return fetch(`/api/routes/${i.connector}/${i.connector_id}`, {method: 'DELETE'});
    }

    let parent = ListAndEditView({
        'load': loadRoutes,
        'delete': deleteItem,
        'editor': RouteEditor,
    });
    return parent;
}

const RouteEditor = (props) => {
    const [instance, setInstance] = useState(props.instance);
    const [channelSelecteOptions, setChannelSelecteOptions] = useState();

    const [msg, messagePlaceholder] = message.useMessage();
    const openMessage = (t, m) => {
        msg.open({
            type: t,
            content: m,
        });
    }

    const loadChannels = () => {
        fetch('/api/channels').then(r => r.json()).then(data => {
            let options = [];
            for (let i = 0 ; i < data.length ; i ++) {
                options.push({
                    label: data[i].name,
                    value: data[i].id
                });
            }
            setChannelSelecteOptions(options);
        });
    }

    const update = (values) => {
        let method = 'POST';
        let url = "/api/routes";
        if (instance.connector_id) {
            url = url + '/' + instance.connector + '/' + instance.connector_id;
            method = 'PUT';
        }

        let body = {
            name: values['name'],
            connector: values['connector'],
            connector_id: values['connector_id'],
            channel_id: values['channel_id']
        }
        
        fetch(url, {
            method: method,
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        }).then(r => {
            if (r.status >= 200 && r.status < 400) {
                openMessage('success', 'Success.');
                return r.json();
            } else {
                openMessage('error', 'Error.')
            }
        })
        .then(data => {
            setInstance(data);
        })
        .catch(e => {
            openMessage('error', 'Error: ' + e);
        });
    }

    useEffect(() => {
        loadChannels();
    }, []);

    return (
        <div>
            {messagePlaceholder}
            <Form
                onFinish={update}
            >
                <Form.Item
                    label="Name"
                    name="name"
                    rules={[
                        {
                            required: true,
                            message: "Name is required."
                        },
                    ]}
                    initialValue={instance.name}
                    style={{ width: '500px' }}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    label="Connector"
                    name="connector"
                    rules={[
                        {
                            required: true,
                            message: "Connector is required."
                        },
                    ]}
                    initialValue={instance.connector}
                    style={{ width: '500px' }}
                >
                    <Select
                        options={[
                            {
                                label: 'Web',
                                value: 'web'
                            },
                            {
                                label: 'WeChat Customer Service',
                                value: 'wxkf'
                            }
                        ]}
                    />
                </Form.Item>

                <Form.Item
                    label="Connector ID"
                    name="connector_id"
                    rules={[
                        {
                            required: true,
                            message: "Connector ID is required."
                        },
                    ]}
                    initialValue={instance.connector_id}
                    style={{ width: '500px' }}
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    label="Channel"
                    name="channel_id"
                    rules={[
                        {
                            required: true,
                            message: "Channel is required."
                        },
                    ]}
                    initialValue={instance.channel_id}
                    style={{ width: '500px' }}
                >
                    <Select
                        options={channelSelecteOptions}
                    />
                </Form.Item>

                <Button type='primary' htmlType='submit' className='mt-3'>Submit</Button>
            </Form>
        </div>
    );
}