import React, {useState} from "react";
import {Outlet, useLocation, useNavigate} from "react-router-dom";
import {Button} from "@/components/ui/button";
import {Menu, LogOut, ChevronDown, Import, Search, TextSearch} from "lucide-react";
import {useAuth} from "@/providers/auth/useAuth.tsx";

interface MenuItem {
  label: string;
  path: string;
  key: string;
  icon: React.ReactElement;
  disabled?: boolean;
  subItems?: Partial<MenuItem>[];
}

export default function AppRootPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [expandedMenu, setExpandedMenu] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  const auth = useAuth();
  const handleLogout = () => {
    auth.logout();
    navigate("/auth/login");
  };
  
  const menuItems: MenuItem[] = [
    {
      label: "Consultar",
      key: "home",
      path: "/app",
      icon: <Search size={18}/>
    },
    {
      label: "Importar Arquivo",
      key: "import-file",
      path: "/app/import-file",
      icon: <Import size={18}/>
    },
    {
      label: "Histórico",
      key: "queries-list",
      path: "/app/queries-list",
      icon: <TextSearch size={18}/>
    },
  ];
  
  const toggleMenu = (key: string) =>
    setExpandedMenu(expandedMenu === key ? null : key);
  
  const goTo = (menuItem: Partial<MenuItem>) => {
    if (menuItem.path && !menuItem.disabled) {
      navigate(menuItem.path);
    }
  }
  
  return (
    <div className="flex h-screen bg-background text-foreground">
      {/* Sidebar */}
      <aside
        className={`
          fixed inset-y-0 left-0 z-30 w-64 transform bg-sidebar border-r border-sidebar-border transition-transform duration-300 ease-in-out
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
          md:translate-x-0 md:flex md:flex-col
        `}
      >
        <div className="flex items-center justify-center h-16 font-bold text-xl border-b border-sidebar-border">
          NexaS One
        </div>
        
        <nav className="flex-1 px-3 py-6 space-y-2 overflow-y-auto">
          {menuItems.map((item) =>
            item.subItems ? (
              <div key={item.key}>
                <Button
                  variant="ghost"
                  className={`w-full flex justify-between items-center px-3 py-2.5 gap-3 rounded-md transition-colors ${
                    expandedMenu === item.key
                      ? "bg-primary/10 text-primary font-semibold"
                      : "hover:bg-sidebar-accent"
                  }`}
                  onClick={() => toggleMenu(item.key)}
                >
                  <div className="flex items-center gap-3">
                    {item.icon}
                    <span>{item.label}</span>
                  </div>
                  <ChevronDown
                    className={`h-4 w-4 transition-transform ${
                      expandedMenu === item.key ? "rotate-180" : ""
                    }`}
                  />
                </Button>
                
                {expandedMenu === item.key && (
                  <div className="ml-8 mt-1 flex flex-col space-y-1">
                    {item.subItems.map((sub) => (
                      <Button
                        variant="ghost"
                        onClick={() => goTo(sub)}
                        disabled={item.disabled ?? false}
                        className={`w-full justify-start gap-3 px-3 py-2 text-sm rounded-md ${
                          location.pathname === sub.path
                            ? "bg-primary/10 text-primary font-semibold"
                            : "hover:bg-sidebar-accent"
                        }`}
                      >
                        {sub.icon} {sub.label}
                      </Button>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <Button
                variant="ghost"
                onClick={() => goTo(item)}
                disabled={item.disabled ?? false}
                className={`w-full justify-start items-center gap-3 px-3 py-2.5 rounded-md transition-colors ${
                  location.pathname === item.path
                    ? "bg-primary/10 text-primary font-semibold"
                    : "hover:bg-sidebar-accent"
                }`}
              >
                {item.icon}
                <span>{item.label}</span>
              </Button>
            )
          )}
        </nav>
        
        <div className="p-4 border-t border-sidebar-border">
          <Button
            variant="ghost"
            onClick={handleLogout}
            className="w-full justify-start text-red-500 hover:bg-red-50 hover:text-red-600"
          >
            <LogOut className="mr-2 h-5 w-5"/> Sair
          </Button>
        </div>
      </aside>
      
      {/* Overlay para mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/50 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Main area */}
      <div className="flex-1 flex flex-col md:pl-64">
        {/* Header */}
        <header
          className="h-16 bg-sidebar-accent border-b border-sidebar-border flex items-center justify-between px-4 md:px-6">
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              className="md:hidden p-2"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <Menu className="h-6 w-6"/>
            </Button>
          </div>
        </header>
        
        {/* Content */}
        <main className="flex-1 overflow-y-auto p-6 bg-background">
          <Outlet/>
        </main>
      </div>
    </div>
  );
}
