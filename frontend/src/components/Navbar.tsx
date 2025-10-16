import { NavLink } from "react-router-dom";
import { Upload, MessageSquare, Settings, Brain } from "lucide-react";

const Navbar = () => {
  return (
    <nav className="sticky top-0 z-50 gradient-primary shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-2">
            <Brain className="w-8 h-8 text-primary-foreground" />
            <span className="text-xl font-bold text-primary-foreground">
              Smart Knowledge Explorer
            </span>
          </div>
          
          <div className="flex space-x-1">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                  isActive
                    ? "bg-white/20 text-primary-foreground font-semibold"
                    : "text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
                }`
              }
            >
              <Upload className="w-4 h-4" />
              <span className="hidden sm:inline">Upload</span>
            </NavLink>
            
            <NavLink
              to="/query"
              className={({ isActive }) =>
                `flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                  isActive
                    ? "bg-white/20 text-primary-foreground font-semibold"
                    : "text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
                }`
              }
            >
              <MessageSquare className="w-4 h-4" />
              <span className="hidden sm:inline">Query</span>
            </NavLink>
            
            <NavLink
              to="/admin"
              className={({ isActive }) =>
                `flex items-center space-x-2 px-4 py-2 rounded-lg transition-all ${
                  isActive
                    ? "bg-white/20 text-primary-foreground font-semibold"
                    : "text-primary-foreground/80 hover:bg-white/10 hover:text-primary-foreground"
                }`
              }
            >
              <Settings className="w-4 h-4" />
              <span className="hidden sm:inline">Admin</span>
            </NavLink>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
