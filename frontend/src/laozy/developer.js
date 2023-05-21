import React, { useEffect } from 'react';

import { Chat } from '../chat/chat.js'

import { useState } from 'react'
import { Select } from 'antd';

export const Developer = () => {
    const [routes, setRoutes] = useState([]);
    const [options, setOptions] = useState([]);
    const [connector_id, setConnectorId] = useState(null);
    const [docHeight, setDocHeight] = useState(document.documentElement.clientHeight);
    let headerHeight = 48;

    document.body.onresize = () => {
        setDocHeight(document.documentElement.clientHeight);
    };

    const loadRoutes = () => {
        fetch("/api/routes").then(r => {
            if (r.status != 200) return [];
            return r.json();
        }).then(data => {
            let t_options = [];
            let cid = localStorage.getItem('developer_connector_id');

            for (let i = 0; i < data.length; i++) {
                if (data[i].connector === 'web') {
                    if (cid === data[i].connector_id) {
                        setConnectorId(cid);
                    }

                    t_options.push({
                        label: data[i].name,
                        value: data[i].connector_id,
                    });
                }
            }
            setOptions(t_options);
        });
    }

    const updateConnectorId = (cid) => {
        setConnectorId(cid);
        localStorage.setItem('developer_connector_id', cid);
    }

    useEffect(() => {
        loadRoutes();

    }, []);

    return (
        <div>
            <div className='p-2 border-bottom border-light' style={{ height: headerHeight }}>
                <div className='col-lg-3 mx-auto'>
                    {options.length > 0 ? (
                        <Select
                            showSearch
                            placeholder='Select a Connector'
                            defaultValue={connector_id}
                            onChange={updateConnectorId}
                            options={options}

                            className='w-100'
                            filterOption={(input, option) =>
                                (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                            }
                            bordered={false}
                        >

                        </Select>
                    ) : null}

                </div>
            </div>
            {connector_id ? (
                <Chat connector_id={connector_id} height={docHeight - headerHeight} />
            ) : null}
        </div>
    );
}