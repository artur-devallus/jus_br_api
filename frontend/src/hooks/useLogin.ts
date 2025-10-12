import {useMutation} from "@tanstack/react-query";
import {api} from "@/lib/axios.ts";

const getLoginForm = (username: string, password: string): FormData => {
  const form: FormData = new FormData();
  form.append('username', username);
  form.append('password', password);
  return form;
}

export const useLogin = () => {
  return useMutation({
    mutationFn: (payload: {
      username: string;
      password: string;
    }) => api.post(`/v1/auth/token`, getLoginForm(payload.username, payload.password)).then((res) => res.data),
  });
};