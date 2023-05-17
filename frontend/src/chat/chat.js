import React, { useEffect } from 'react';

import { useState } from 'react'

import {
    Layout,
    Form,
    Input,
    Button,
    Row,
    Col,
    Avatar,
    Alert,
    Typography,
} from 'antd';

import { fetchEventSource } from '@microsoft/fetch-event-source'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const { TextArea } = Input;

let abortController = null;

export const Chat = (props) => {

    const [form] = Form.useForm();
    const [error, setError] = useState(null);
    const [generating, setGenerating] = useState(false);
    const [currentReply, setCurrentReply] = useState(null);
    const [history, setHistory] = useState([]);

    const onKeyDown = (e) => {
        if (e.keyCode === 13/*enter*/ && (e.ctrlKey || e.metaKey)) {
            onSubmit();
        }
    }

    const setHistoryScroll = () => {
        let history_div = document.getElementById('history');
        if (history_div) {
            setTimeout(() => {
                history_div.scrollTop = history_div.scrollHeight;
            }, 0);
        }
    }

    const onSubmit = () => {
        setError(null);
        setGenerating(true);
        abortController = new AbortController();

        let values = form.getFieldsValue();
        if (!values.prompt) {
            //setError("Prompt required!");
            setGenerating(false);
            return;
        }
        let req = {
            "connector_id": props.connector_id,
            "content": values.prompt
        }
        history.push({ role: 'human', message: values.prompt });
        setHistoryScroll();
        form.setFieldValue('prompt', '');
        getReply(req);
    }

    const loadHistory = () => {
        let connector_id = props.connector_id;
        fetch(`/api/connectors/messages?connector_id=${connector_id}`)
            .then(r => r.json())
            .then(messages => {
                let t_history = [];
                for (let i = messages.length; i > 0; i--) {
                    let msg = messages[i - 1];
                    t_history.push({
                        role: msg.direction === 0 ? 'human' : 'ai',
                        message: msg.content
                    });
                }
                setHistory(t_history);

                setHistoryScroll();
            });
    }

    const getReply = (req) => {
        let reply = '';

        fetchEventSource("/api/connectors/messages?sse=true", {
            method: 'POST',
            body: JSON.stringify(req),
            headers: { 'Content-Type': 'application/json' },
            signal: abortController.signal,
            onopen(response) {
                if (response.ok /*&& response.headers.get('content-type') === EventStreamContentType*/) {
                    return; // everything's good
                } else if (response.status >= 400 && response.status < 500 && response.status !== 429) {
                    // client-side errors are usually non-retriable:
                    setError('Something wrong! Error code: ' + response.status);
                    abortController.abort();
                    setGenerating(false);
                    //throw new FatalError();
                } else {
                    abortController.abort();// don't retry
                    setGenerating(false);
                    //throw new RetriableError();
                }
            },
            onmessage(msg) {
                let j = JSON.parse(msg.data);
                if (msg.event === 'error') {
                    let e = j['e'];
                    setError(e);
                    setGenerating(false);
                } else {
                    let c = j['c'];
                    if (c) {
                        reply = reply + c;
                        setCurrentReply(reply + "▁");
                        setHistoryScroll();
                    }
                }
            },
            onerror(err) {
                setGenerating(false);
                throw err;
            },
            onclose() {
                history.push({ role: 'ai', message: reply });
                setCurrentReply(null);
                setGenerating(false);
            }
        });
    };

    const abort = () => {
        abortController.abort();
        setGenerating(false);
    };

    useEffect(() => {
        loadHistory();
    }, [props.connector_id]);

    return (
        <Layout
            style={{
                height: props.height ? props.height : '600px',
            }}
            className="p-3"
        >
            <div id="history" className='mb-auto overflow-scroll'>
                <MessageHistory history={history} />
                <div>
                    {currentReply ? (
                        <Message role='ai' message={currentReply} />
                    ) : null}
                    {generating ? (
                        <div className="text-center mt-2 mb-3">
                            <Button onClick={abort}><i className="fa-solid fa-stop me-2"></i> 停止</Button>
                        </div>
                    ) : null}
                </div>

                {error ? (
                    <Alert message={error} type="error" showIcon style={{ marginTop: '10px' }} />
                ) : null}
            </div>
            <Form
                form={form}
                layout='horizontal'
                onFinish={onSubmit}
                style={{
                }}
                className='mb-0 pt-3 border-top'
            >
                <Row wrap={false} align="bottom">
                    <Col flex="auto">
                        <Form.Item
                            name="prompt"
                            style={{ marginBottom: 0 }}
                        >
                            <TextArea autoSize onKeyDown={onKeyDown} placeholder="" />
                        </Form.Item>
                    </Col>
                    <Col flex='none'>
                        <Form.Item style={{ marginLeft: '15px', marginBottom: 0 }}>
                            <Button htmlType='submit' type="primary" shape="circle" disabled={generating}>
                                <i className="fa-regular fa-lightbulb"></i>
                            </Button>
                        </Form.Item>
                    </Col>
                </Row>
                <div className='d-none d-lg-block small text-secondary mt-2'>CTRL + ENTER / ⌘ + ENTER</div>
            </Form>
        </Layout>
    );
}

const Message = (props) => {
    return (
        <div className='mb-3'>
            <div className={props.role === 'human' ? 'd-flex flex-row-reverse' : 'd-flex flex-row'}>
                <div style={{ width: '32px' }}>
                    <Avatar
                        style={{
                            backgroundColor: props.role === 'human' ? '#f56a00' : '#7265e6',
                            verticalAlign: 'middle',
                        }}
                    >
                        {props.role === 'human' ? 'Human' : 'AI'}
                    </Avatar>
                </div>
                <div className='card mx-3 border-0'
                    style={{
                        backgroundColor: props.role === 'human' ? '#d1e7dd' : '#fff'
                    }}
                >
                    <div className='card-body px-3 pt-3 pb-0'>
                        <ReactMarkdown children={props.message} remarkPlugins={[remarkGfm]} className='p-0 m-0'>

                        </ReactMarkdown>
                    </div>
                </div>
            </div>
        </div>
    );
}

const MessageHistory = (props) => {
    return (
        <div>
            {Object.keys(props.history).map((k, i) => {
                let h = props.history[i];
                return <Message role={h.role} message={h.message} key={i} />;
            })}
        </div>
    );
}