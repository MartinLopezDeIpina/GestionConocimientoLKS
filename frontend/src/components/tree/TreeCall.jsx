import { useEffect } from "react";
import Tree from "../tree/Tree";



const TreeCall = ({BACKEND_URL, props}) => {
    let user_email;

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

    useEffect(() => {

        async function fetchUserAndSetEmail() {
            const userInfo = await getUser();
            user_email = userInfo.logged_in_as;
        }

        fetchUserAndSetEmail();
    }, []); 


    let API_URL;
    if(props.isPersonalTree){
        API_URL = BACKEND_URL + '/api/personal/' + user_email;
    }else{
        API_URL = BACKEND_URL + '/api';
    }
    props.API_URL = API_URL;

    return(
        <Tree props={props}/>
    )
}
export default TreeCall;