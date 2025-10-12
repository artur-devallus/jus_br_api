import {createContext} from "react";

type AuthContextType = {
  currentToken(): string | null;
  login: (token: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
};

export const AuthContext = createContext<AuthContextType | undefined>(undefined);
