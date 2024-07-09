
import { useGoogleLogin } from "@react-oauth/google";
import GoogleSVG from "../components/SVGs/GoogleSVG";
import {useStore} from '@nanostores/react';
import {isLoggedNano, userNano, logginClicked} from '../components/nano/authNano';

async function getUserInfoAndCookies(codeResponse) {
  var response = await fetch("http://localhost:5000/google_login", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ code: codeResponse.code }),
  });
  return await response.json();
}

const LoginButton = () => {
    const $isLoggedNano = useStore(isLoggedNano);
    const $userNano = useStore(userNano);
    const $logginClicked = useStore(logginClicked);

    return (
        <button onClick={() => logginClicked.set(true)}>
            <GoogleSVG />
            <span>Login with Google</span>
        </button>

    )
}

export default LoginButton;