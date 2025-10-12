import {Link} from 'react-router-dom';
import {CogIcon} from "lucide-react";

export default function MaintenancePage() {
  return (
    <div
      className="flex flex-col items-center justify-center min-h-screen bg-zinc-900 text-[#fdeccd] text-center py-10 px-6">
      <CogIcon className="text-6xl mb-4 animate-pulse"/>
      <h1 className="text-6xl font-bold mb-4">Manutenção em andamento</h1>
      <p className="text-2xl mb-6">Estamos realizando melhorias no sistema. Em breve, estaremos de volta!</p>
      <p className="text-lg mb-8">Pedimos desculpas pelo inconveniente. Tente novamente em alguns minutos.</p>
      <Link
        to="/"
        className="bg-[#fdeccd] text-black font-semibold py-2 px-6 rounded-full text-xl hover:bg-[#e4d1a0] transition duration-300 transform hover:scale-105"
      >
        Voltar para a página inicial
      </Link>
    </div>
  );
}
