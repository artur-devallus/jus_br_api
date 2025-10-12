import { Link } from "react-router-dom";
import {Button} from "@/components/ui/button.tsx";

export default function LandingPage() {
  return (
    <div className="flex flex-col items-center justify-center h-[80vh] text-center px-6">
      <h1 className="text-5xl font-bold mb-6">Consulta Processual Federal</h1>
      <p className="text-lg text-gray-600 max-w-2xl">
        Pesquise processos nos Tribunais Regionais Federais (TRFs) de forma unificada e em tempo real.
      </p>
      <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
        <Button asChild size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
          <Link to="/auth/login">Acessar Plataforma</Link>
        </Button>
      </div>
    </div>
  );
}
