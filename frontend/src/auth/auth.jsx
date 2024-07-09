import React, { useState, useEffect } from "react";
import { useGoogleLogin } from "@react-oauth/google";
import UserAvatar from "./userAvatar";
import GoogleSVG from "../components/SVGs/GoogleSVG";
import { useAuth } from './AuthContext';


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
  const { loggedIn, setLoggedIn, user, setUser } = useAuth();

  const googleLogin = useGoogleLogin({
    flow: "auth-code",
    onSuccess: async (codeResponse) => {
      let loginDetails = await getUserInfoAndCookies(codeResponse);
      setLoggedIn(true);
      setUser(loginDetails.user);
    },
  });


  const handleLogout = async () => {
    let response = await logout();
    if(response.ok){
      setLoggedIn(false);
    }
  };

  useEffect(() => {
    async function checkLoggedInStatus() {
      console.log("Checking logged in status");
      let response = await getProtected();
      console.log(response);

      if (response.ok) {
        let data = await response.json();
        let userInfo = await getUserInfo(data.logged_in_as);
        setUser(userInfo);
        setLoggedIn(true);
        console.log('set logged in true');
      }
    }

    checkLoggedInStatus();
  }, [loggedIn]);

  const returnButton = () => {
    return (
      <>
        {!loggedIn ? (
          <button className="googleButton" onClick={() => googleLogin()}>
            <GoogleSVG />
          </button>
        ) : (
          user && <UserAvatar userName={user.name} onClick={handleLogout}></UserAvatar>
        )}
      </>
    );
  };
  return returnButton();
}
