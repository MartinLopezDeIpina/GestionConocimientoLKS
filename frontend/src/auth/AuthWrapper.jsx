import React from 'react';
import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from './AuthContext';

const AuthWrapper = ({ children, clientId }) => {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  );
};

export default AuthWrapper;