import {useForm} from 'react-hook-form';
import {zodResolver} from '@hookform/resolvers/zod';
import {useNavigate} from 'react-router-dom';
import {Lock, User} from 'lucide-react';
import {toast} from 'sonner';

import {useAuth} from '@/providers/auth/useAuth';

import {Button} from '@/components/ui/button';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import {Input} from '@/components/ui/input';
import {FC} from "react";
import {useLogin} from "@/hooks/useLogin.ts";
import {TLoginValidator, LoginValidator} from "@/lib/validators/login-validator.ts";
import {ErrorUtils} from "@/lib/errorUtils.ts";

export const LoginForm: FC = () => {
  const navigate = useNavigate();
  const auth = useAuth();
  const {mutate: loginUser, isPending} = useLogin();

  const form = useForm<TLoginValidator>({
    resolver: zodResolver(LoginValidator),
    defaultValues: {
      username: '',
      password: '',
    },
  });

  const onSubmit = (data: TLoginValidator) => {
    loginUser(
      {username: data.username, password: data.password},
      {
        onSuccess: (res) => {
          auth.login(res.access_token);
          navigate('/app', {replace: true});
        },
        onError: (err) => {
          const errorMessage = ErrorUtils.getErrorMessage(err);
          toast.error('Falha no Login', {
            description: errorMessage || 'Verifique suas credenciais e tente novamente.',
          });
        },
      }
    );
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="username"
          render={({field}) => (
            <FormItem>
              <FormLabel>Usuário</FormLabel>
              <FormControl>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400"/>
                  <Input
                    type="text"
                    maxLength={16}
                    placeholder="Usuário"
                    className="pl-10"
                    {...field}
                  />
                </div>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({field}) => (
            <FormItem>
              <FormLabel>Senha</FormLabel>
              <FormControl>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400"/>
                  <Input
                    type="password"
                    maxLength={16}
                    placeholder="••••••••"
                    className="pl-10"
                    {...field}
                  />
                </div>
              </FormControl>
              <FormMessage/>
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full" disabled={isPending}>
          {isPending ? 'Entrando...' : 'Entrar'}
        </Button>
      </form>
    </Form>
  );
}

export default LoginForm;