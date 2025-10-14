import {useState} from "react";
import {Search, LogOut, Import, Menu, TextSearch} from "lucide-react";
import {Button} from "@/components/ui/button";

interface SidebarProps {
  onLogout?: () => void;
  onNavigate?: (path: string) => void;
}

export default function Sidebar({onLogout, onNavigate}: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={`h-screen bg-white border-r flex flex-col justify-between transition-all duration-200 ${
        collapsed ? "w-16" : "w-64"
      }`}
    >
      <div>
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b">
          {!collapsed && <span className="text-xl font-semibold">Gugas ADV</span>}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setCollapsed(!collapsed)}
            className="ml-auto"
          >
            <Menu size={20}/>
          </Button>
        </div>

        {/* Menu */}
        <nav className="mt-4 flex flex-col gap-1 px-3">
          <Button
            variant="ghost"
            className={`justify-start gap-2 ${
              collapsed ? "justify-center px-0" : ""
            }`}
            onClick={() => onNavigate?.("/app")}
          >
            <Search size={18}/>
            {!collapsed && <span>Consultas</span>}
          </Button>

          <Button
            variant="ghost"
            className={`justify-start gap-2 ${
              collapsed ? "justify-center px-0" : ""
            }`}
            onClick={() => onNavigate?.("/app/import-file")}
          >
            <Import size={18}/>
            {!collapsed && <span>Importar Arquivo</span>}
          </Button>

          <Button
            variant="ghost"
            className={`justify-start gap-2 ${
              collapsed ? "justify-center px-0" : ""
            }`}
            onClick={() => onNavigate?.("/app/queries-list")}
          >
            <TextSearch size={18}/>
            {!collapsed && <span>Histórico</span>}
          </Button>
        </nav>
      </div>
      {/* Logout */}
      <div className="p-3 border-t">
        <Button
          variant="ghost"
          className={`w-full gap-2 text-red-600 hover:text-red-700 hover:bg-red-50 ${
            collapsed ? "justify-center" : "justify-start"
          }`}
          onClick={onLogout}
        >
          <LogOut size={18}/>
          {!collapsed && <span>Sair</span>}
        </Button>
      </div>
    </aside>
  );
}
