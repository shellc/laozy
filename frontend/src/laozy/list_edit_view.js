import React, { useEffect } from 'react'
import { useState } from 'react'

import {
    Input,
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
        props.delete(i).then(() => {props.load(setList)});
    }
    const show = (eid) => {
        document.getElementById(eid).style.display='inline';
    }
    const hide = (eid) => {
        document.getElementById(eid).style.display='none';
    }

    useEffect(() => {
        if (props.load) props.load(setList);
    }, [view]);

    return (
        <div className='p-3'>
            {view === 'editor' ? (
                <div>
                    <div className='pb-2 border-bottom mb-3'>
                        <Button type='none' onClick={() => setView(null)}><i className="fa-solid fa-angle-left"></i></Button>
                    </div>
                    {props.editor ? (
                        <props.editor instance={instance} />
                    ) : null}
                </div>
            ) : (
                <div className='d-flex flex-row flex-wrap'>
                    <div className='p-2'>
                        <a href="#" onClick={() => { setView('editor'); setInstance({}) }}><div className='card border-0'>
                            <div className='card-body'>
                                <i className="fa-solid fa-plus"></i>
                            </div>
                        </div></a>
                    </div>
                    {list && list.length > 0 && list.map((i, k) => (
                        <div className='p-2' key={i.id}>
                            
                            <div className='card border-0'>
                                <div className='card-body' onMouseOver={() => show('del_' + k)} onMouseLeave={() => hide('del_' + k)}>
                                <a href="#" onClick={() => edit(i)}>{i.name}</a>
                                    <a id={'del_' + k} href="#" style={{display: 'none'}} onClick={() => deleteItem(i)}>
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