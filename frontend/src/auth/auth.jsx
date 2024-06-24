import React, { useState, useEffect } from "react";
import GoogleIcon from "@mui/icons-material/Google";
import IconButton from "@mui/material/IconButton";
import { useGoogleLogin } from "@react-oauth/google";
import UserAvatar from "./userAvatar";

async function getUserInfoAndCoockies(codeResponse) {
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

export default function Auth() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUser] = useState({});
  const googleLogin = useGoogleLogin({
    flow: "auth-code",
    onSuccess: async (codeResponse) => {
      let loginDetails = await getUserInfoAndCoockies(codeResponse);
      console.log(loginDetails);
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
      let response = await getProtected();
      console.log(response);

      if (response.ok) {
        let data = await response.json();
        let userInfo = await getUserInfo(data.logged_in_as);
        setUser(userInfo);
        setLoggedIn(true);
      }
    }

    checkLoggedInStatus();
  }, []);

  useEffect(() => {
    console.log(`logged in: ${loggedIn}`);
  }, [loggedIn]);

  const returnButton = () => {
    return (
      <>
        {!loggedIn ? (
          <IconButton
            color="primary"
            aria-label="add to shopping cart"
            onClick={() => googleLogin()}
          >
          <GoogleIcon fontSize="large" />
          </IconButton>
        ) : (
          <UserAvatar userName={user.name} onClick={handleLogout}></UserAvatar>
        )}
      </>
    );
  };
  return returnButton();
}
