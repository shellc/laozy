import React, { useEffect } from 'react'
import { useState } from 'react'

import {
    Button,
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
    const show = (eid) => {
        document.getElementById(eid).style.display = 'inline';
    }
    const hide = (eid) => {
        document.getElementById(eid).style.display = 'none';
    }

    useEffect(() => {
        if (props.load) props.load(setList);
    }, [view]);

    return (
        <div>
            {view === 'editor' ? (
                <div>
                    <div className='p-2 border-bottom mb-3 position-sticky z-1 top-0'
                        style={{ backgroundColor: '#eee' }}
                    >
                        <Button type='none' onClick={() => setView(null)}><i className="fa-solid fa-bars-staggered"></i></Button>
                    </div>
                    {props.editor ? (
                        <div className='p-3'>
                            <props.editor instance={instance} />
                        </div>
                    ) : null}
                </div>
            ) : (
                <div className='p-3 d-flex flex-row flex-wrap'>
                    <div className='p-2'>
                        <a href="#" onClick={() => { setView('editor'); setInstance({}) }}>
                            <div className='card border-0 shadow-sm'>
                                <div className='card-body'>
                                    &nbsp;<i className="fa-solid fa-circle-plus"></i>&nbsp;
                                </div>
                            </div>
                        </a>
                    </div>
                    {list && list.length > 0 && list.map((i, k) => (
                        <div className='p-2' key={i.id}>

                            <div className='card border-0 shadow-sm'>
                                <div className='card-body' onMouseOver={() => show('del_' + k)} onMouseLeave={() => hide('del_' + k)}>
                                    <a href="#" onClick={() => edit(i)}>{i.name}</a>
                                    <a id={'del_' + k} href="#" style={{ display: 'none' }} onClick={() => deleteItem(i)}>
                                        <i className="fa-solid fa-trash-can text-secondary ms-3"></i>
                                    </a>
                                </div>
                            </div>

                        </div>
                    ))}
                </div>
            )}

        </div>
    );
}