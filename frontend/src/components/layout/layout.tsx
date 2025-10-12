import {Outlet, useNavigate} from "react-router-dom";
import Sidebar from "@/components/layout/sidebar";
import {useAuth} from "@/providers/auth/useAuth.tsx";

export default function Layout() {
  const navigate = useNavigate();
  const auth = useAuth();
  const handleLogout = () => {
    auth.logout();
    navigate("/auth/login");
  };

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar onLogout={handleLogout} onNavigate={handleNavigate}/>
      <main className="flex-1 overflow-y-auto p-6">
        <Outlet/>
      </main>
    </div>
  );
}
