import { Briefcase, Settings, LogOut } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

export function Header() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("google_access_token");
    navigate("/login");
  };

  return (
    <header className="flex items-center justify-between p-4 border-b bg-background flex-shrink-0">
      <Link to="/" className="flex items-center gap-2">
        <Briefcase className="h-6 w-6" />
        <h1 className="text-lg sm:text-xl font-bold">Daily Action Hub</h1>
      </Link>
      <div className="flex items-center gap-2">
        <Link to="/settings">
          <Button variant="outline" size="icon">
            <Settings className="h-4 w-4" />
            <span className="sr-only">Settings</span>
          </Button>
        </Link>
        <Button variant="ghost" size="sm" onClick={handleLogout} className="text-muted-foreground hover:text-red-600 hover:bg-red-50">
          <LogOut className="h-4 w-4 mr-2" />
          Logout
        </Button>
      </div>
    </header>
  );
}