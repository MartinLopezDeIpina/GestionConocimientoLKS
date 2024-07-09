import React, { useState, useEffect } from "react";
import { useGoogleLogin } from "@react-oauth/google";
import UserAvatar from "./userAvatar";
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
  const $isLoggedNano = useStore(isLoggedNano);
  const $userNano = useStore(userNano);
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
      isLoggedNano.set(true);
      userNano.set(loginDetails.user);
    },
  });


  const handleLogout = async () => {
    let response = await logout();
    if(response.ok){
      isLoggedNano.set(false);
    }
  };

  useEffect(() => {
    async function checkLoggedInStatus() {
      let response = await getProtected();

      if (response.ok) {
        let data = await response.json();
        let userInfo = await getUserInfo(data.logged_in_as);
        userNano.set(userInfo);
        isLoggedNano.set(true);
      }
    }

    checkLoggedInStatus();
  }, []);


  const returnButton = () => {
    return (
      <>
        {!$isLoggedNano ? (
          <button className="googleButton" onClick={() => googleLogin()}>
            <GoogleSVG />
          </button>
        ) : (
          $userNano && <UserAvatar userName={$userNano.name} onClick={handleLogout}></UserAvatar>
        )}
      </>
    );
  };
  return returnButton();
}
