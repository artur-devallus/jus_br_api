import {Search, LogOut} from "lucide-react";
import {Button} from "@/components/ui/button";

interface SidebarProps {
  onLogout?: () => void;
  onNavigate?: (path: string) => void;
}

export default function Sidebar({onLogout, onNavigate}: SidebarProps) {
  return (
    <aside className="w-64 h-screen bg-white border-r flex flex-col justify-between">
      <div>
        <div className="p-6 text-2xl font-semibold border-b">Jus BR</div>
        <nav className="mt-4 flex flex-col gap-1 px-3">
          <Button
            variant="ghost"
            className="justify-start gap-2"
            onClick={() => onNavigate?.("/app/consultas")}
          >
            <Search size={18}/>
            Consultas
          </Button>
        </nav>
      </div>

      <div className="p-3 border-t">
        <Button
          variant="ghost"
          className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50 gap-2"
          onClick={onLogout}
        >
          <LogOut size={18}/>
          Sair
        </Button>
      </div>
    </aside>
  );
}
