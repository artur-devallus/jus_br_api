import {Link} from "react-router-dom";
import {motion} from "framer-motion";
import {Button} from "@/components/ui/button";
import logo from "@/assets/logo.png";

export default function LandingPage() {
  return (
    <div
      className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-background text-foreground">
      <div
        className="absolute inset-0 bg-gradient-to-br from-primary/10 via-transparent to-foreground/5 dark:from-primary/20 dark:to-foreground/10"/>
      
      <motion.div
        className="relative z-10 flex flex-col items-center text-center"
        initial={{opacity: 0, y: -30}}
        animate={{opacity: 1, y: 0}}
        transition={{duration: 0.8}}
      >
        {/* Logo */}
        <motion.img
          src={logo}
          alt="Nexas One Logo"
          className="mb-6 max-h-64 w-auto rounded-xl shadow-lg object-contain p-4"
          initial={{scale: 0.8, opacity: 0}}
          animate={{scale: 1, opacity: 1}}
          transition={{duration: 0.6, delay: 0.2}}
        />
        
        {/* Título */}
        <h1
          className="text-4xl font-extrabold tracking-tight sm:text-6xl bg-gradient-to-r from-primary to-foreground bg-clip-text text-transparent">
          NexaS One
        </h1>
        
        {/* Subtítulo */}
        <p className="mt-4 max-w-xl text-lg leading-8 text-muted-foreground sm:text-xl">
          Pesquise processos nos Tribunais Regionais Federais (TRFs) de forma unificada e em tempo real.
        </p>
        
        {/* Botões */}
        <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
          <Button asChild size="lg" className="bg-primary text-primary-foreground hover:bg-primary/90">
            <Link to="/auth/login">Acessar Plataforma</Link>
          </Button>
        </div>
      </motion.div>
      
      {/* Footer */}
      <footer className="absolute bottom-4 text-sm text-muted-foreground">
        © {new Date().getFullYear()} NexaS One. Todos os direitos reservados.
      </footer>
    </div>
  );
};
