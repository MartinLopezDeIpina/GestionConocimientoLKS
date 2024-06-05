import React, { useState, useEffect } from 'react';
import { Treebeard } from 'react-treebeard';

import './../../public/styles/tree.css';

function TreeLibrary() {
    const TreeExample = () => {
        const [data, setData] = useState({});
        const [cursor, setCursor] = useState(false);

        useEffect(() => {
            async function fetchTreeData() {
                const data_json = await fetch('http://localhost:5000/api/json_tree').then(response => response.json());
                setData(data_json);
                console.log(data_json);
            }
            fetchTreeData();
        }, []);
        
        const onToggle = (node, toggled) => {
            if (cursor) {
                cursor.active = false;
            }
            node.active = true;
            if (node.children) {
                node.toggled = toggled;
            }
            setCursor(node);
            setData(Object.assign({}, data))
        }


        const customDecorators = {
            Toggle: (props) => {
                return (
                    <div style={props.style}>
                                <svg fill="#000000" height="20px" width="20px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 330" xmlSpace="preserve"><g id="SVGRepo_bgCarrier" strokeWidth="0"></g><g id="SVGRepo_tracerCarrier" strokeLinecap="round" strokeLinejoin="round"></g><g id="SVGRepo_iconCarrier"> <path id="XMLID_222_" d="M250.606,154.389l-150-149.996c-5.857-5.858-15.355-5.858-21.213,0.001 c-5.857,5.858-5.857,15.355,0.001,21.213l139.393,139.39L79.393,304.394c-5.857,5.858-5.857,15.355,0.001,21.213 C82.322,328.536,86.161,330,90,330s7.678-1.464,10.607-4.394l149.999-150.004c2.814-2.813,4.394-6.628,4.394-10.606 C255,161.018,253.42,157.202,250.606,154.389z"></path> </g></svg>
                    </div>
                );
            },
            Header: (props) => {
                return (
                    <div style={props.style}>
                        {props.node.name}
                    </div>
                );
            },
            Container: (props) => {
                return (
                    <div onClick={props.onClick} className='treeContainer'>
                        {/* Hide Toggle When Terminal Here */}
                        <customDecorators.Toggle {...props} />
                        <customDecorators.Header {...props} />
                    </div>
                );
            }
        };

        return (
            <Treebeard data={data} onToggle={onToggle} />
        );
    }

    return (
        <TreeExample />
    );
}

export default TreeLibrary;