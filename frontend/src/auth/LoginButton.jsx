import GoogleSVG from "../components/SVGs/GoogleSVG";
import {useStore} from '@nanostores/react';
import {logginClicked} from '../components/nano/authNano';

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
    const $logginClicked = useStore(logginClicked);

    return (
      <div className="divGoogleButtonWrapper">
        <button className="loginButton" onClick={() => logginClicked.set(true)}>
            <GoogleSVG />
            <span>Iniciar sesión con Google</span>
        </button>
      </div>
    )
}

export default LoginButton;