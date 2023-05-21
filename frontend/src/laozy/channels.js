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

//const { TextArea } = Input;

export const ChannelListAndEditView = () => {
    const loadChannels = (setState) => {
        fetch('/api/channels').then(r => r.json()).then(data => setState(data));
    }

    const deleteItem = (i) => {
        return fetch(`/api/channels/${i.id}`, { method: 'DELETE' });
    }

    let parent = ListAndEditView({
        'load': loadChannels,
        'delete': deleteItem,
        'editor': ChannelEditor,
        'label': 'Channel'
    });
    return parent;
}

const ChannelEditor = (props) => {
    const [instance, setInstance] = useState(props.instance);
    const [robotSelecteOptions, setRobotSelecteOptions] = useState();

    const [msg, messagePlaceholder] = message.useMessage();
    const openMessage = (t, m) => {
        msg.open({
            type: t,
            content: m,
        });
    }

    const loadRobots = () => {
        fetch('/api/robots').then(r => r.json()).then(data => {
            let options = [];
            for (let i = 0 ; i < data.length ; i ++) {
                options.push({
                    label: data[i].name,
                    value: data[i].id
                });
            }
            setRobotSelecteOptions(options);
        });
    }

    const update = (values) => {
        let method = 'POST';
        let url = "/api/channels";
        if (instance.id) {
            url = url + '/' + instance.id;
            method = 'PUT';
        }

        let body = {
            name: values['name'],
            robot_id: values['robot_id']
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
        loadRobots();
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
                    className='col-lg-6'
                >
                    <Input />
                </Form.Item>

                <Form.Item
                    label="Robot"
                    name="robot_id"
                    rules={[
                        {
                            required: true,
                            message: "Robot is required."
                        },
                    ]}
                    initialValue={instance.robot_id}
                    className='col-lg-6'
                >
                    <Select
                        options={robotSelecteOptions}
                    />
                </Form.Item>

                <Button type='primary' htmlType='submit' className='mt-3'>Save</Button>
            </Form>
        </div>
    );
}