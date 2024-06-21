import { GoogleOAuthProvider } from "@react-oauth/google";
import Auth from "../auth/auth";

const GoogleOauthReact = ({clientId}) => {
    return(
        <div>
            <GoogleOAuthProvider clientId={clientId}>
            <Auth></Auth>
            </GoogleOAuthProvider>
        </div>
    )
}
export default GoogleOauthReact;