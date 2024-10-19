
import { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // store both author id and token
  const [userAuthentication, setUserAuthentication] = useState({
    authorId: null,
    token: null,
  });

  return (
    <AuthContext.Provider value={{ userAuthentication, setUserAuthentication }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);