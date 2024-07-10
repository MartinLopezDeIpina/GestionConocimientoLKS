// components/AuthenticationCallback.jsx
import React, { useEffect } from 'react';

const AuthenticationCallbackReact = () => {
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const authCode = params.get('code');
    console.log(`code: ${authCode}`);
    console.log(`code.code: ${authCode.code}`);
    
    fetch('http://localhost:5000/google_login', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code: authCode }),
    })
    .then(response => response.json())
    .then(data => {
      // Handle the response from the backend
      console.log(data);
      // Redirect to another page or handle the response as needed
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }, []);

  return (
    <div>
      Authentication Callback
    </div>
  );
};

export default AuthenticationCallbackReact;
