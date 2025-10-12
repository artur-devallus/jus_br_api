import axios, {HttpStatusCode} from 'axios';
import {getValidTokenFromStorage} from "./token-utils.ts";

function getAxiosClient() {
  const client = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
  });
  client.interceptors.request.use((config) => {
    const token = getValidTokenFromStorage('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });
  client.interceptors.response.use(
    response => response,
    error => {
      const reqUrl = error.response.request.responseURL;
      if (error.response?.status === HttpStatusCode.Unauthorized && !reqUrl.endsWith('/v1/auth/token/')) {
        localStorage.removeItem("authToken");
        window.location.href = '/auth/login';
      }
      return Promise.reject(error);
    }
  );
  return client;
}


export const api = getAxiosClient();
