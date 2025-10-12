import {z} from "zod";

export const LoginValidator = z.object({
  username: z.string().min(1, {message: "Usuário inválido"}).max(16, {message: 'Usuário inválido'}),
  password: z.string().min(6, {message: "A senha deve ter no mínimo 6 caracteres."}).max(16, {message: 'A senha deve possuir no máximo 16 caracteres.'}),
});

// Extrai o tipo TypeScript do esquema para usar no nosso formulário
export type TLoginValidator = z.infer<typeof LoginValidator>;
