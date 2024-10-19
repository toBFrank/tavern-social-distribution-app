
import { createContext, useState, useContext } from 'react';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  // store both author id and token
  const [userAuthentication, setUserAuthentication] = useState({
    authorId: '1d6dfebf-63a6-47a9-8e88-5cda73675db5',
    token: '7e31046a8413002b920bdc8dd0232bad6c482e1e',
  });

  return (
    <AuthContext.Provider value={{ userAuthentication, setUserAuthentication }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);