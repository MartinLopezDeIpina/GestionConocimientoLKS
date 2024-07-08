import { GoogleOAuthProvider } from "@react-oauth/google";
import Auth from "../auth/auth";
import '../../public/styles/auth.css';
import LoginButton from "../auth/LoginButton";
import { useState } from "react";

const GoogleOauthReact = ({clientId, isHeaderButton}) => {
    const [loggedIn, setLoggedIn] = useState(false);
    const [user, setUser] = useState({});

    return(
        <div className="divGoogleButton">
            <GoogleOAuthProvider clientId={clientId}>
                {
                isHeaderButton ? 
                    <Auth loggedIn={loggedIn} setLoggedIn={setLoggedIn} user={user} setUser={setUser}></Auth>
                    : 
                    <LoginButton setLoggedIn={setLoggedIn}/>
                }
            </GoogleOAuthProvider>
        </div>
    )
}
export default GoogleOauthReact;