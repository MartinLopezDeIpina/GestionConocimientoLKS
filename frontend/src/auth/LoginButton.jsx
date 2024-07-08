
import { useGoogleLogin } from "@react-oauth/google";
import GoogleSVG from "../components/SVGs/GoogleSVG";
import { useAuth } from './AuthContext';

const LoginButton = () => {
    const { setLoggedIn } = useAuth();

    const googleLogin = useGoogleLogin({
        flow: "auth-code",
        onSuccess: async (codeResponse) => {
        console.log("setting logged in");
        setLoggedIn(true);
        },
    });

    return (
        <button onClick={() => googleLogin()}>
            <GoogleSVG />
            <span>Login with Google</span>
        </button>

    )
}

export default LoginButton;