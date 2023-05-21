import React, { useEffect } from 'react'
import { useState } from 'react'

import {
    Button,
    Card
} from 'antd'

export const ListAndEditView = (props = {}) => {
    const [view, setView] = useState(null);
    const [instance, setInstance] = useState();
    const [list, setList] = useState([]);

    const edit = (instance) => {
        setInstance(instance);
        setView('editor');
    }

    const deleteItem = (i) => {
        props.delete(i).then(() => { props.load(setList) });
    }

    useEffect(() => {
        if (props.load) props.load(setList);
    }, [view]);

    return (
        <div>
            {view === 'editor' ? (
                <div>
                    <div className='p-2 border-bottom mb-3 position-sticky z-1 top-0 bg-light'>
                        <Button type='none' onClick={() => setView(null)}><i className="fa-solid fa-bars-staggered"></i></Button>
                    </div>
                    {props.editor ? (
                        <div className='p-3'>
                            <props.editor instance={instance} />
                        </div>
                    ) : null}
                </div>
            ) : (
                <div>
                    <div className='mt-4 ps-4'>
                        <Button type='dashed' onClick={() => { setView('editor'); setInstance({}) }}>
                            <i className="fa-solid fa-circle-plus me-2"></i> New {props.label ? props.label : ''}
                        </Button>
                    </div>
                    <div className='p-3 d-flex flex-row flex-wrap'>
                        {list && list.length > 0 && list.map((i, k) => (
                            <div className='p-2' key={i.id}>
                                <Card
                                    hoverable
                                    style={{ 
                                        position: 'relative'
                                    }}
                                    bodyStyle={{
                                        padding: '1rem 0.5rem'
                                    }}
                                >
                                    <Button type='none' id={'del_' + k} onClick={() => deleteItem(i)} className='position-absolute top-0 end-0 p-1 text-secondary'>
                                        <i className="fa-regular fa-circle-xmark"></i>
                                    </Button>
                                    <Button type='link' onClick={() => edit(i)}>{i.name}</Button>
                                </Card>
                            </div>
                        ))}
                    </div>
                </div>
            )}

        </div>
    );
}