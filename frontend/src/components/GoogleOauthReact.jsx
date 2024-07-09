import { GoogleOAuthProvider } from "@react-oauth/google";
import Auth from "../auth/auth";
import '../../public/styles/auth.css';
import LoginButton from "../auth/LoginButton";

const GoogleOauthReact = ({clientId, isHeaderButton}) => {

    return(
        <div className="divGoogleButton">
            <GoogleOAuthProvider clientId={clientId}>
                {
                isHeaderButton ? 
                    <Auth/>
                    : 
                    <LoginButton/>
                }
            </GoogleOAuthProvider>
        </div>
    )
}
export default GoogleOauthReact;