import { GoogleOAuthProvider } from "@react-oauth/google";
import Auth from "../auth/auth";
import '../../public/styles/auth.css';

const GoogleOauthReact = ({clientId}) => {

    return(
        <div className="divGoogleButton">
            <GoogleOAuthProvider clientId={clientId}>
                <Auth/>
            </GoogleOAuthProvider>
        </div>
    )
}
export default GoogleOauthReact;