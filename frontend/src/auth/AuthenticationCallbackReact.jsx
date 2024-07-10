import React, { useEffect } from 'react';

const AuthenticationCallbackReact = () => {

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const authCode = params.get('code');

    
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
      localStorage.setItem('userName', data.user.name);
      window.location.href = '/home';
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }, []);

  return (
    null
  );
};

export default AuthenticationCallbackReact;
