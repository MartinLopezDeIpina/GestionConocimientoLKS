import React, { useState, useEffect } from "react";
import { useGoogleLogin } from "@react-oauth/google";
import UserAvatar from "./userAvatar";
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

async function getUserInfo(email){
  var response = await fetch(`http://localhost:5000/get_user_info/${email}`, {
    method: "GET",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return await response.json();
}

async function getProtected() {
  let response = await fetch("http://localhost:5000/protected", {
    method: "GET",
    credentials: "include",
    mode: "cors",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return response;
}

async function logout(){
  let response = await fetch("http://localhost:5000/logout", {
    method: "POST",
    credentials: "include",
    mode: "cors",
    headers: {
      "Content-Type": "application/json",
    },
  });
  return response;
}

export default function Auth({}) {
  const [loggedName, setLoggedName] = useState(null);
  const $logginClicked = useStore(logginClicked)

  useEffect(() => {
    if($logginClicked){
      googleLogin();
      logginClicked.set(false);
    }
  }, [$logginClicked])

  const googleLogin = useGoogleLogin({
    flow: "auth-code",
    onSuccess: async (codeResponse) => {
      let loginDetails = await getUserInfoAndCookies(codeResponse);
      setLoggedName(loginDetails.user.name);
    }
  });


  const handleLogout = async () => {
    let response = await logout();
    if(response.ok){
      setLoggedName(null);
    }
  };

  useEffect(() => {
    async function checkLoggedInStatus() {
      let response = await getProtected();

      if (response.ok) {
        let data = await response.json();
        let userInfo = await getUserInfo(data.logged_in_as);
        setLoggedName(userInfo.name);
      }
    }

    checkLoggedInStatus();
  }, []);


  const returnButton = () => {
    return (
      <>
        {!loggedName ? (
          <button className="googleButton" onClick={() => googleLogin()}>
            <GoogleSVG />
          </button>
        ) : (
          loggedName && <UserAvatar userName={loggedName} onClick={handleLogout}></UserAvatar>
        )}
      </>
    );
  };
  return returnButton();
}
