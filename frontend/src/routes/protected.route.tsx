import React from "react";
import {Navigate} from "react-router-dom";
import {useAuth} from "../providers/auth/useAuth.tsx";

export const ProtectedRoute = ({element}: { element: React.ReactNode }) => {
  const {currentToken} = useAuth();

  if (!currentToken()) {
    return <Navigate to="/auth/login"/>;
  }

  return <>{element}</>;
}