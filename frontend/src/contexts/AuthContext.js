
import { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // store both author id and token
  const [userAuthentication, setUserAuthentication] = useState({
    authorId: '0b61c141-371e-4f34-9b4e-275df8c0e666',  // TODO: Remove hardcoded author id (FrancoPersonal)
    token: 'ee1bd22bd866a1d0e6e3db9ae3a1ef6094224e4b',  // TODO: Remove hardcoded token (FrancoPersonal)
  });

  return (
    <AuthContext.Provider value={{ userAuthentication, setUserAuthentication }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);