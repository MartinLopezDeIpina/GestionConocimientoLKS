import Tree from "./Tree";

const TreeCall = ({BACKEND_URL, isPersonalTree}) => {
    let user_email;
    let API_URL;

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

    async function fetchUserAndSetEmail() {
        const userInfo = await getUser();
        user_email = userInfo.logged_in_as;
    }

    console.log(`isPersonalTree: ${isPersonalTree}`);
    if(isPersonalTree){
        user_email = fetchUserAndSetEmail();
        //API_URL = BACKEND_URL + '/api/personal/' + user_email;
        API_URL = BACKEND_URL + '/api';
    }else{
        API_URL = BACKEND_URL + '/api';
    }

    return(
        <Tree client:only  API_URL={API_URL} isPersonalTree={isPersonalTree}/>
    )
}

export default TreeCall;