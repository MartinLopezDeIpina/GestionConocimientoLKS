import { useEffect, useState } from "react";
import Tree from "./Tree";

const TreeCall = ({BACKEND_URL, isPersonalTree}) => {
    const[API_URL, setAPI_URL] = useState(undefined);

    useEffect(() => {
        async function setupAPI_URL(){
            if(isPersonalTree){
                setAPI_URL(`${BACKEND_URL}/api/personal`);
            }else{
                setAPI_URL(`${BACKEND_URL}/api`);
            }
        }

        setupAPI_URL();
    }, []);


    return(
        (API_URL === undefined) ? (<div></div>) : <Tree client API_URL={API_URL} isPersonalTree={isPersonalTree}/>
    )
}

export default TreeCall;