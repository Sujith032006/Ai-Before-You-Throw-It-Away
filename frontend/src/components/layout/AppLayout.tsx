import { Outlet, Link, useLocation } from 'react-router-dom';
import { Recycle, LayoutDashboard, Camera, History } from 'lucide-react';

export default function AppLayout() {
  const location = useLocation();
  const currentPath = location.pathname;

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100 selection:bg-emerald-500 selection:text-white font-sans antialiased">
      
      {/* TOP GLASSMORPHIC DESKTOP HEADER */}
      <header className="bg-slate-900/90 backdrop-blur-xl border-b border-slate-800/80 sticky top-0 z-40 w-full shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-8 h-16 sm:h-20 flex items-center justify-between">
          
          {/* Logo & Brand */}
          <Link to="/" className="flex items-center gap-3 text-emerald-400 font-extrabold text-lg sm:text-xl tracking-tight hover:opacity-90 transition-opacity">
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center text-white shadow-lg shadow-emerald-900/50 border border-emerald-400/40">
              <Recycle size={24} />
            </div>
            <div className="flex flex-col">
              <span className="leading-none text-white text-base sm:text-lg font-black tracking-wide">Before You Throw It Away</span>
              <span className="text-[11px] text-emerald-400 font-bold tracking-wider uppercase mt-0.5">AI Household Upcycling Hub</span>
            </div>
          </Link>

          {/* DESKTOP TOP NAVIGATION LINKS */}
          <div className="hidden md:flex items-center gap-2">
            <Link
              to="/"
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                currentPath === '/' || currentPath === '/dashboard'
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <LayoutDashboard size={16} />
              <span>Dashboard</span>
            </Link>

            <Link
              to="/scan"
              className={`flex items-center gap-2 px-4.5 py-2 rounded-xl text-xs font-black transition-all ${
                currentPath === '/scan'
                  ? 'bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 shadow-md shadow-emerald-500/20'
                  : 'bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20'
              }`}
            >
              <Camera size={16} />
              <span>Scan Item</span>
            </Link>

            <Link
              to="/history"
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                currentPath === '/history'
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <History size={16} />
              <span>History</span>
            </Link>
          </div>

          {/* Live System Badge */}
          <div className="flex items-center gap-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-bold px-3 py-1.5 rounded-full">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="hidden sm:inline">AI Vision & LLM Ready</span>
            <span className="sm:hidden">Active</span>
          </div>

        </div>
      </header>
      
      {/* FULL WIDTH MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col w-full bg-slate-950 pb-20 md:pb-8">
        <Outlet />
      </main>

      {/* MOBILE BOTTOM NAVIGATION BAR (HIDDEN ON DESKTOP md:) */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full bg-slate-950/95 backdrop-blur-xl border-t border-slate-800/80 px-6 py-2.5 z-40 flex items-center justify-between shadow-2xl">
        
        {/* Dashboard Tab */}
        <Link
          to="/"
          className={`flex flex-col items-center gap-1 text-[11px] font-bold transition-all ${
            currentPath === '/' || currentPath === '/dashboard'
              ? 'text-emerald-400 scale-105'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </Link>

        {/* FLOATING CENTER SCAN BUTTON */}
        <Link
          to="/scan"
          className="flex flex-col items-center justify-center w-14 h-14 rounded-full bg-gradient-to-br from-emerald-500 via-teal-500 to-emerald-600 text-slate-950 shadow-xl shadow-emerald-600/40 border-2 border-slate-900 transition-transform hover:scale-110 active:scale-95 -mt-6"
        >
          <Camera size={26} />
        </Link>

        {/* History Tab */}
        <Link
          to="/history"
          className={`flex flex-col items-center gap-1 text-[11px] font-bold transition-all ${
            currentPath === '/history'
              ? 'text-emerald-400 scale-105'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <History size={20} />
          <span>History</span>
        </Link>

      </nav>

    </div>
  );
}
