import React from 'react';
import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from './AuthContext';

const AuthWrapper = ({ children, clientId }) => {
  return (
    <GoogleOAuthProvider clientId={clientId}>
      <AuthProvider>
        {children}
      </AuthProvider>
    </GoogleOAuthProvider>
  );
};

export default AuthWrapper;