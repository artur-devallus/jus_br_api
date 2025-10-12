export const auth = {
  setToken: (t: string) => localStorage.setItem("authToken", t),
  getToken: () => localStorage.getItem("authToken"),
  clear: () => localStorage.removeItem("authToken"),
};
