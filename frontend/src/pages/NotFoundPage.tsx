import {Link} from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-screen bg-zinc-900 text-[#fdeccd] text-center py-10 px-6">
      <h1 className="text-6xl font-bold mb-4 animate-bounce">404</h1>
      <p className="text-2xl mb-6">Ops! A página que você está procurando não foi encontrada.</p>
      <p className="text-lg mb-8">Mas não se preocupe, vamos te levar de volta.</p>
      <Link
        to="/"
        className="bg-[#fdeccd] text-black font-semibold py-2 px-6 rounded-full text-xl hover:bg-[#e4d1a0] transition duration-300 transform hover:scale-105"
      >
        Voltar para a página inicial
      </Link>
    </div>
  );
}
