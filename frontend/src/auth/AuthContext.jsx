import React, { createContext, useState, useContext } from 'react';

const AuthContext = createContext({ loggedIn: false, setLoggedIn: () => {}, user: {}, setUser: () => {} });

export function AuthProvider({ children }) {

  const [user, setUser] = useState({});
  const [loggedIn, setLoggedIn] = useState(false);

  return (
    <AuthContext.Provider value={{ loggedIn, setLoggedIn, user, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}