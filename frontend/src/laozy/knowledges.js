import React, { useEffect } from 'react'
import { useState } from 'react'

import {
    message,
    Form,
    Input,
    Button,
    List,
    Tag
} from 'antd'

import { ListAndEditView } from './list_edit_view';

const { TextArea } = Input;

export const KnowledgeListAndEditView = () => {
    const loadKnowledges = (setState) => {
        fetch('/api/knowledges').then(r => r.json()).then(data => setState(data));
    }

    const deleteItem = (i) => {
        return fetch(`/api/knowledges/${i.id}`, { method: 'DELETE' });
    }

    let parent = ListAndEditView({
        'load': loadKnowledges,
        'delete': deleteItem,
        'editor': KnowledgeEditor,
        'label': 'Knowledge Base'
    });
    return parent;
}

const KnowledgeEditor = (props) => {
    const [instance, setInstance] = useState(props.instance);
    const [msg, messagePlaceholder] = message.useMessage();

    const openMessage = (t, m) => {
        msg.open({
            type: t,
            content: m,
        });
    }

    const update = (values) => {
        let method = 'POST';
        let url = "/api/knowledges";
        if (instance.id) {
            url = url + '/' + instance.id;
            method = 'PUT';
        }

        let body = {
            name: values['name']
        }

        fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        }).then(r => {
            if (r.status >= 200 && r.status < 400) {
                openMessage('success', 'Success.');
                return r.json();
            } else {
                openMessage('error', 'Error.')
            }
        }).then(data => {
            setInstance(data);
        }).catch(e => {
            openMessage('error', 'Error: ' + e);
        });
    }

    return (
        <div>
            {messagePlaceholder}
            <Form
                onFinish={update}
                layout="inline"
                className='col-12 col-lg-6'
            >
                <Button type='none' className=''>Name</Button>
                <Form.Item
                    name="name"
                    rules={[
                        {
                            required: true,
                            message: "Name is required."
                        },
                    ]}
                    initialValue={instance.name}
                    className='flex-grow-1'
                >
                    <Input />
                </Form.Item>
                <Button type='primary' shape="circle" htmlType='submit'><i className="fa-solid fa-check"></i></Button>
            </Form>

            {instance.id ? (
                <div className="mt-5"><KnowledgeManager id={instance.id} /></div>
            ) : null}
        </div>
    );
}

const KnowledgeManager = (props) => {
    const [form] = Form.useForm();
    const [data, setData] = useState();
    const [loading, setLoading] = useState(false);
    const [msg, messagePlaceholder] = message.useMessage();

    const openMessage = (t, m) => {
        msg.open({
            type: t,
            content: m,
        });
    }

    const save = () => {
        let values = form.getFieldsValue();

        let body = [{
            content: values['content'],
            metadata: { 'tag': values['tag'] }
        }];

        setLoading(true);
        fetch(`/api/knowledges/${props.id}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body)
        }).then(r => {
            if (r.status >= 200 && r.status < 400) {
                openMessage('success', 'Success.');
                retrieve();
                form.resetFields();
                return r.json();
            } else {
                openMessage('error', 'Error.')
            }
        }).catch(e => {
            openMessage('error', 'Error: ' + e);
        }).finally(e => setLoading(false));
    }

    const retrieve = () => {
        setLoading(true);
        let values = form.getFieldsValue();
        let tag = values['tag'] ? values['tag'] : '';
        fetch(`/api/knowledges/${props.id}?content=${values['content'] ? encodeURI(values['content']) : ''}&tag=${tag}`)
            .then(r => r.json())
            .then(data => {
                setData(data);
            })
            .finally(e => setLoading(false));
    }

    const deleteKnowledge = (index) => {
        console.log(index);
        let id = data[index].id;

        setLoading(true);
        fetch(`/api/knowledges/${props.id}/${id}`, {
            method: 'DELETE'
        }).then(r => {
            if (r.status === 204) {
                delete data[index];
                setData([...data.filter((i) => i != null)]);
            } else {
                openMessage('error', 'Error.')
            }
        }).finally(e => setLoading(false));
    }

    useEffect(() => {
        retrieve();
    }, []);

    return (
        <div>
            {messagePlaceholder}
            <Form form={form} layout='inline'>
                <Form.Item
                    name='content'
                    className='flex-grow-1'
                >
                    <TextArea placeholder='Content' autoSize />
                </Form.Item>
                <Form.Item
                    name='tag'
                    className='col-2 '
                >
                    <Input placeholder='Tag' />
                </Form.Item>
                <Button type='primary' title='Search' onClick={retrieve}><i className="fa-brands fa-searchengin"></i></Button>
                <Button type='primary' title='Save' className='ms-3' onClick={save}><i className="fa-solid fa-cloud-arrow-up"></i></Button>
            </Form>
            {data ? (
                <List
                    itemLayout="horizontal"
                    dataSource={data}
                    renderItem={(item, index) => (
                        <List.Item
                            actions={[<a href="#" onClick={() => deleteKnowledge(index)}><i className="fa-solid fa-trash-can"></i></a>]}
                        >
                            <div>
                                <div>{item.content}</div>
                                <div className='mt-2'>
                                    <Tag>D:{Number.parseFloat(item.distance).toFixed(2)}</Tag>
                                    {Object.keys(item.metadata).map((v, i) => (
                                        <Tag key={'k_' + i}>{v} : {item.metadata[v]}</Tag>
                                    ))}
                                </div>
                            </div>
                        </List.Item>
                    )}
                    style={{ backgroundColor: '#fff' }}
                    className='mt-3 p-3'
                    loading={loading}
                />
            ) : null}

        </div>
    );
}