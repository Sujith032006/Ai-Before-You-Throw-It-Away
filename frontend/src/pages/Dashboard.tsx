import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { 
  Recycle, CheckCircle2, Camera, ArrowRight, Star, 
  Sparkles, Clock, Leaf, ShieldCheck, ChevronRight, Award, Search
} from 'lucide-react';
import { useScan } from '../context/ScanContext';
import { fetchDashboardStats } from '../services/dashboardService';
import type { ActivityItem } from '../types/dashboard';

export default function Dashboard() {
  const navigate = useNavigate();
  const { activityList } = useScan();
  const [statsData, setStatsData] = useState<{
    total_scans: number;
    total_projects: number;
    completed_projects: number;
    recent_activity: ActivityItem[];
  }>({
    total_scans: 1,
    total_projects: 1,
    completed_projects: 1,
    recent_activity: []
  });

  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'all' | 'completed' | 'active'>('all');

  const currentDateStr = new Date().toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });

  // Dynamically sync context activities + backend API
  useEffect(() => {
    async function loadStats() {
      try {
        const apiRes = await fetchDashboardStats();
        // Merge API & context activities dynamically
        const combined = [...activityList];
        if (apiRes.recent_activity) {
          apiRes.recent_activity.forEach(item => {
            if (!combined.some(c => c.project_id === item.project_id)) {
              combined.push(item);
            }
          });
        }

        const totalScans = Math.max(combined.length, apiRes.total_scans || 1);
        const totalProjects = Math.max(combined.length, apiRes.total_projects || 1);
        const completedProjects = combined.filter(c => c.status === 'completed').length;

        setStatsData({
          total_scans: totalScans,
          total_projects: totalProjects,
          completed_projects: completedProjects,
          recent_activity: combined
        });
      } catch {
        const totalScans = activityList.length || 1;
        const completedProjects = activityList.filter(c => c.status === 'completed').length;
        setStatsData({
          total_scans: totalScans,
          total_projects: totalScans,
          completed_projects: completedProjects,
          recent_activity: activityList
        });
      }
    }
    loadStats();
  }, [activityList]);

  // Dynamic filter calculation
  const displayedActivities = statsData.recent_activity.filter(item => {
    const matchesSearch = item.object_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.project_name.toLowerCase().includes(searchQuery.toLowerCase());
    if (activeTab === 'completed') return matchesSearch && item.status === 'completed';
    if (activeTab === 'active') return matchesSearch && item.status === 'in_progress';
    return matchesSearch;
  });

  return (
    <div className="w-full flex-1 bg-slate-950 text-slate-100 pb-16">
      
      {/* Centered Max-Width Full-Screen Responsive Desktop Wrapper */}
      <div className="max-w-7xl mx-auto px-4 sm:px-8 py-6 space-y-6">

        {/* 1. HERO HEADER BANNER (Full-width responsive card) */}
        <div className="relative bg-gradient-to-r from-slate-900 via-emerald-950 to-slate-900 p-6 sm:p-8 rounded-3xl border border-slate-800 shadow-2xl overflow-hidden">
          
          {/* Ambient Glowing Orbs */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl -z-0 pointer-events-none"></div>
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-teal-500/10 rounded-full blur-3xl -z-0 pointer-events-none"></div>

          <div className="relative z-10 flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            
            <div className="space-y-3 max-w-2xl">
              {/* Top Badges */}
              <div className="flex items-center gap-2">
                <span className="text-[11px] font-extrabold uppercase tracking-widest text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full flex items-center gap-1.5 backdrop-blur-md">
                  <Sparkles size={13} className="animate-pulse" />
                  {currentDateStr} • Dynamic Upcycling Hub
                </span>

                <span className="inline-flex items-center gap-1.5 text-[11px] font-bold text-teal-300 bg-teal-500/10 border border-teal-500/20 px-3 py-1 rounded-full">
                  <ShieldCheck size={13} /> Live System
                </span>
              </div>

              {/* Welcome Title */}
              <h1 className="text-2xl sm:text-4xl font-black text-white tracking-tight leading-tight">
                Give Everyday Trash a <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-teal-300 to-emerald-200">Second Life</span>
              </h1>
              
              <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal">
                Divert household waste from landfills. Scan objects with real-time YOLO computer vision to unlock personalized DIY upcycling projects tailored to your tools and goals.
              </p>
            </div>

            {/* HERO SCAN ACTION BUTTON */}
            <div className="lg:flex-shrink-0">
              <button
                onClick={() => navigate('/scan')}
                className="w-full lg:w-auto bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-black py-4 px-8 rounded-2xl shadow-xl shadow-emerald-500/25 transition-all hover:scale-105 active:scale-95 flex items-center justify-center gap-3 text-base tracking-wide border border-emerald-300/40 group"
              >
                <div className="w-9 h-9 rounded-xl bg-slate-950/20 flex items-center justify-center text-slate-950 group-hover:scale-110 transition-transform">
                  <Camera size={22} />
                </div>
                <span>📷 SCAN ITEM TO UPCYCLE</span>
                <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
              </button>
            </div>

          </div>
        </div>

        {/* 2. RESPONSIVE DESKTOP MULTI-COLUMN LAYOUT */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 sm:gap-8">
          
          {/* LEFT 2 COLUMNS (Stats, Impact Gauge & Popular Catalog) */}
          <div className="lg:col-span-2 space-y-6 sm:space-y-8">

            {/* IMPACT METRICS STATS CARDS */}
            <div>
              <h2 className="text-xs font-extrabold text-slate-400 uppercase tracking-widest mb-3">Live Impact Metrics</h2>
              
              <div className="grid grid-cols-3 gap-3 sm:gap-5">
                
                {/* Scanned Card */}
                <div className="bg-slate-900/90 p-4 sm:p-6 rounded-3xl border border-slate-800 shadow-lg text-center flex flex-col items-center hover:border-blue-500/40 transition-all hover:scale-[1.02]">
                  <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400 mb-3">
                    <Camera size={22} />
                  </div>
                  <span className="text-3xl sm:text-4xl font-black text-white leading-none">
                    {statsData.total_scans}
                  </span>
                  <span className="text-[11px] sm:text-xs font-bold text-slate-400 uppercase tracking-wider mt-2">
                    Items Scanned
                  </span>
                </div>

                {/* Created Card */}
                <div className="bg-slate-900/90 p-4 sm:p-6 rounded-3xl border border-slate-800 shadow-lg text-center flex flex-col items-center hover:border-teal-500/40 transition-all hover:scale-[1.02]">
                  <div className="w-12 h-12 rounded-2xl bg-teal-500/10 border border-teal-500/20 flex items-center justify-center text-teal-400 mb-3">
                    <Recycle size={22} />
                  </div>
                  <span className="text-3xl sm:text-4xl font-black text-white leading-none">
                    {statsData.total_projects}
                  </span>
                  <span className="text-[11px] sm:text-xs font-bold text-slate-400 uppercase tracking-wider mt-2">
                    Projects Created
                  </span>
                </div>

                {/* Completed Card */}
                <div className="bg-slate-900/90 p-4 sm:p-6 rounded-3xl border border-slate-800 shadow-lg text-center flex flex-col items-center hover:border-emerald-500/40 transition-all hover:scale-[1.02]">
                  <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-3">
                    <CheckCircle2 size={22} />
                  </div>
                  <span className="text-3xl sm:text-4xl font-black text-emerald-400 leading-none">
                    {statsData.completed_projects}
                  </span>
                  <span className="text-[11px] sm:text-xs font-bold text-slate-400 uppercase tracking-wider mt-2">
                    Completed
                  </span>
                </div>

              </div>
            </div>

            {/* ENVIRONMENTAL IMPACT SUMMARY GAUGE */}
            <div className="bg-gradient-to-r from-slate-900 via-emerald-950/40 to-slate-900 rounded-3xl p-5 sm:p-6 border border-emerald-500/20 shadow-lg relative overflow-hidden">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                    <Leaf size={22} />
                  </div>
                  <div>
                    <h3 className="font-extrabold text-sm text-white uppercase tracking-wider">Environmental Impact Meter</h3>
                    <p className="text-xs text-slate-400">Real-time diverted household waste calculations</p>
                  </div>
                </div>

                <span className="text-xs font-black text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-lg border border-emerald-500/20 flex items-center gap-1.5">
                  <Award size={14} /> Upcycling Champion
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-800/80">
                <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 text-center">
                  <span className="text-2xl sm:text-3xl font-black text-emerald-400 block leading-tight">
                    ~{(statsData.completed_projects * 0.45).toFixed(1)} kg
                  </span>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mt-1 block">
                    Waste Diverted From Landfill
                  </span>
                </div>

                <div className="bg-slate-950/60 p-4 rounded-2xl border border-slate-800 text-center">
                  <span className="text-2xl sm:text-3xl font-black text-teal-300 block leading-tight">
                    ~{(statsData.completed_projects * 0.9).toFixed(1)} kg
                  </span>
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider mt-1 block">
                    Estimated CO₂ Offset
                  </span>
                </div>
              </div>
            </div>

            {/* POPULAR DIY UPCYCLING REUSE CATALOG */}
            <div>
              <h2 className="text-xs font-extrabold text-slate-400 uppercase tracking-widest mb-3">Popular Reuse Catalog</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Project Card 1 */}
                <div 
                  onClick={() => navigate('/personalized-guide?id=plastic-bottle-self-watering-planter')}
                  className="bg-gradient-to-br from-slate-900 to-slate-950 p-5 rounded-3xl border border-slate-800 hover:border-emerald-500/50 transition-all cursor-pointer shadow-lg group hover:scale-[1.01]"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-extrabold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20">
                      Gardening • Easy
                    </span>
                    <Star size={16} className="text-amber-400 fill-amber-400" />
                  </div>
                  <h3 className="font-extrabold text-white text-lg group-hover:text-emerald-400 transition-colors mb-1">
                    🌱 Self-Watering Planter
                  </h3>
                  <p className="text-xs text-slate-400 line-clamp-2 mb-4 leading-relaxed">
                    Transform plastic bottles into self-contained planters with wicking moisture control.
                  </p>
                  <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                    Start Guide <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                  </span>
                </div>

                {/* Project Card 2 */}
                <div 
                  onClick={() => navigate('/personalized-guide?id=tin-can-desk-organizer')}
                  className="bg-gradient-to-br from-slate-900 to-slate-950 p-5 rounded-3xl border border-slate-800 hover:border-emerald-500/50 transition-all cursor-pointer shadow-lg group hover:scale-[1.01]"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-extrabold text-teal-400 bg-teal-500/10 px-2.5 py-1 rounded-md border border-teal-500/20">
                      Storage • Easy
                    </span>
                    <Star size={16} className="text-amber-400 fill-amber-400" />
                  </div>
                  <h3 className="font-extrabold text-white text-lg group-hover:text-emerald-400 transition-colors mb-1">
                    🥫 Desk Organizer & Pen Holder
                  </h3>
                  <p className="text-xs text-slate-400 line-clamp-2 mb-4 leading-relaxed">
                    Convert tin cans into stylish desk stationery organizers and desk storage.
                  </p>
                  <span className="text-xs font-bold text-teal-400 flex items-center gap-1">
                    Start Guide <ChevronRight size={16} className="group-hover:translate-x-1 transition-transform" />
                  </span>
                </div>

              </div>
            </div>

          </div>

          {/* RIGHT COLUMN (Recent Activity Feed & 3-Step Process) */}
          <div className="space-y-6 sm:space-y-8">
            
            {/* RECENT ACTIVITY FEED */}
            <div className="bg-slate-900/90 p-5 sm:p-6 rounded-3xl border border-slate-800 shadow-xl">
              
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xs font-extrabold text-slate-400 uppercase tracking-widest">Recent Activity</h2>
                <Link to="/history" className="text-xs font-bold text-emerald-400 hover:text-emerald-300 flex items-center gap-1">
                  Full History <ChevronRight size={14} />
                </Link>
              </div>

              {/* Search & Filter Pills */}
              <div className="space-y-3 mb-4">
                <div className="relative">
                  <Search size={16} className="absolute top-1/2 left-3.5 -translate-y-1/2 text-slate-500" />
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search activities..."
                    className="w-full bg-slate-950 text-xs text-white pl-10 pr-4 py-2.5 rounded-xl border border-slate-800 focus:outline-none focus:border-emerald-500 transition-colors"
                  />
                </div>

                <div className="flex items-center gap-1.5 bg-slate-950 p-1 rounded-xl border border-slate-800 text-[11px] font-bold">
                  <button
                    onClick={() => setActiveTab('all')}
                    className={`flex-1 py-1.5 rounded-lg transition-all ${
                      activeTab === 'all' ? 'bg-emerald-500 text-slate-950 font-black' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    All ({statsData.recent_activity.length})
                  </button>

                  <button
                    onClick={() => setActiveTab('completed')}
                    className={`flex-1 py-1.5 rounded-lg transition-all ${
                      activeTab === 'completed' ? 'bg-emerald-500 text-slate-950 font-black' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Done ({statsData.recent_activity.filter(a => a.status === 'completed').length})
                  </button>

                  <button
                    onClick={() => setActiveTab('active')}
                    className={`flex-1 py-1.5 rounded-lg transition-all ${
                      activeTab === 'active' ? 'bg-emerald-500 text-slate-950 font-black' : 'text-slate-400 hover:text-white'
                    }`}
                  >
                    Active ({statsData.recent_activity.filter(a => a.status === 'in_progress').length})
                  </button>
                </div>
              </div>

              {/* Activity Cards List */}
              <div className="space-y-3 max-h-[420px] overflow-y-auto pr-1">
                {displayedActivities.map((item, idx) => (
                  <div 
                    key={idx}
                    onClick={() => navigate(`/personalized-guide?id=${item.project_id}`)}
                    className="bg-slate-950 p-3.5 rounded-2xl border border-slate-800 hover:border-emerald-500/50 transition-all cursor-pointer flex items-center justify-between group"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center text-lg font-bold flex-shrink-0 group-hover:scale-105 transition-transform">
                        {item.object_name.includes('Bottle') ? '🧴' : item.object_name.includes('Can') ? '🥫' : '👕'}
                      </div>

                      <div>
                        <div className="flex items-center gap-1.5 mb-0.5">
                          <span className="font-extrabold text-white text-xs">{item.object_name}</span>
                          <span className="text-[9px] font-black text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
                            {item.match_score}%
                          </span>
                        </div>

                        <p className="text-[11px] text-slate-300 line-clamp-1 font-medium">{item.project_name}</p>
                      </div>
                    </div>

                    <div className="flex flex-col items-end gap-1">
                      {item.status === 'completed' ? (
                        <span className="inline-flex items-center gap-1 text-[9px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/30">
                          <CheckCircle2 size={10} /> Done
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-[9px] font-bold text-amber-300 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/30">
                          <Clock size={10} /> Active
                        </span>
                      )}
                    </div>
                  </div>
                ))}

                {displayedActivities.length === 0 && (
                  <div className="p-4 text-center text-xs text-slate-500">
                    No activity records found.
                  </div>
                )}
              </div>

            </div>

            {/* 3-STEP PROCESS EXPLANATION */}
            <div className="bg-slate-900/60 rounded-3xl p-5 border border-slate-800 text-left space-y-3.5">
              <h2 className="text-xs font-extrabold text-slate-400 uppercase tracking-widest text-center mb-3">
                How It Works in 3 Steps
              </h2>

              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-xl bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center font-black text-xs flex-shrink-0">
                  1
                </div>
                <div>
                  <h3 className="font-bold text-white text-xs">Computer Vision Scan</h3>
                  <p className="text-[11px] text-slate-400 mt-0.5">Capture or upload photos. Ultralytics YOLO detects household items instantly.</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-xl bg-teal-500/20 text-teal-400 border border-teal-500/30 flex items-center justify-center font-black text-xs flex-shrink-0">
                  2
                </div>
                <div>
                  <h3 className="font-bold text-white text-xs">Recommendation Engine</h3>
                  <p className="text-[11px] text-slate-400 mt-0.5">Ranks reuse project ideas matching your tools, budget, and time constraint.</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-xl bg-purple-500/20 text-purple-400 border border-purple-500/30 flex items-center justify-center font-black text-xs flex-shrink-0">
                  3
                </div>
                <div>
                  <h3 className="font-bold text-white text-xs">Generative AI Personalization</h3>
                  <p className="text-[11px] text-slate-400 mt-0.5">Generates tailored step-by-step instructions and interactive AI Project Assistant.</p>
                </div>
              </div>
            </div>

          </div>

        </div>

      </div>

    </div>
  );
}
