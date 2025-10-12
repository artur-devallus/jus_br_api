import {type ReactNode, useState} from "react";
import {AuthContext} from "./AuthContext.tsx";
import {getValidTokenFromStorage} from "../../lib/token-utils.ts";

const TOKEN_NAME: string = 'authToken';


interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({children}: AuthProviderProps) => {
  const [token, setToken] = useState<string | null>(getValidTokenFromStorage(TOKEN_NAME));

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem(TOKEN_NAME, newToken);
  };

  const logout = () => {
    localStorage.removeItem(TOKEN_NAME);
    setToken(null);
  };

  const isAuthenticated = () => {
    return getValidTokenFromStorage(TOKEN_NAME) !== null;
  }

  const currentToken = () => {
    return getValidTokenFromStorage(TOKEN_NAME) ?? token;
  }

  return (
    <AuthContext.Provider value={{currentToken, login, logout, isAuthenticated}}>
      {children}
    </AuthContext.Provider>
  );
};

