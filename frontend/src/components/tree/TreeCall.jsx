import { useEffect, useState } from "react";
import Tree from "./Tree";

const TreeCall = ({BACKEND_URL, isPersonalTree}) => {
    const[API_URL, setAPI_URL] = useState(undefined);

    async function getUser(){
        let response = await fetch(`${BACKEND_URL}/protected`, {
            method: "GET",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
        });
        if(!response.ok){
            throw new Error("Error en el protected");
        }
        return await response.json();
    }

    async function getUserFetchedEmail() {
        const userInfo = await getUser();
        return userInfo.logged_in_as;
    }

    useEffect(() => {
        async function setupAPI_URL(){
            if(isPersonalTree){
                const user_email = await getUserFetchedEmail();
                setAPI_URL(`${BACKEND_URL}/api/personal/${user_email}`);
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