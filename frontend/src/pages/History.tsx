import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Clock, CheckCircle2, ChevronRight, History as HistoryIcon, Search, Trash2 } from 'lucide-react';
import { fetchUserHistory, deleteScanHistoryItem, clearAllUserHistory } from '../services/dashboardService';
import { useScan } from '../context/ScanContext';
import type { HistoryItem } from '../types/dashboard';

export default function History() {
  const navigate = useNavigate();
  const { deleteScanItem, clearAllScans } = useScan();
  const [historyItems, setHistoryItems] = useState<HistoryItem[]>([]);
  const [filter, setFilter] = useState<'all' | 'completed' | 'in_progress'>('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      try {
        const res = await fetchUserHistory();
        setHistoryItems(res.history || []);
      } catch {
        // Fallback in service
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const handleDeleteItem = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this scan from your history?")) {
      setHistoryItems(prev => prev.filter(item => item.id !== id));
      await deleteScanItem(id);
      await deleteScanHistoryItem(id);
    }
  };

  const handleClearAll = async () => {
    if (window.confirm("Are you sure you want to delete ALL scan history? This action cannot be undone.")) {
      setHistoryItems([]);
      await clearAllScans();
      await clearAllUserHistory();
    }
  };

  const filteredList = historyItems.filter(item => {
    if (filter === 'completed') return item.status === 'completed';
    if (filter === 'in_progress') return item.status === 'in_progress';
    return true;
  });

  return (
    <div className="w-full flex-1 bg-slate-950 text-slate-100 pb-16">
      
      {/* Full Width Desktop Container */}
      <div className="max-w-5xl mx-auto px-4 sm:px-8 py-6 space-y-6">

        {/* Top Banner */}
        <div className="relative bg-gradient-to-r from-slate-900 via-emerald-950 to-slate-900 p-6 sm:p-8 rounded-3xl border border-slate-800 shadow-2xl overflow-hidden">
          <div className="flex items-center justify-between mb-4">
            <button 
              onClick={() => navigate('/')}
              className="p-2.5 bg-slate-950/80 hover:bg-slate-800 text-slate-300 rounded-2xl border border-slate-800 transition-colors inline-flex"
            >
              <ArrowLeft size={20} />
            </button>
            
            <div className="flex items-center gap-3">
              <span className="text-xs font-extrabold uppercase tracking-widest bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3.5 py-1.5 rounded-full flex items-center gap-1.5">
                <HistoryIcon size={14} /> Saved History & Logs
              </span>

              {historyItems.length > 0 && (
                <button
                  onClick={handleClearAll}
                  className="text-xs font-bold text-red-400 bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 px-3 py-1.5 rounded-full transition-colors flex items-center gap-1.5"
                >
                  <Trash2 size={14} />
                  Clear All History
                </button>
              )}
            </div>
          </div>

          <h1 className="text-2xl sm:text-4xl font-black text-white tracking-tight mb-2">📜 Activity History & Upcycling Logs</h1>
          <p className="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-xl font-normal">
            Review previous computer vision item scans, generated AI personalized guides, and delete unwanted scans anytime.
          </p>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-2 bg-slate-900 p-1.5 rounded-2xl border border-slate-800 shadow-sm text-xs font-extrabold max-w-md">
          <button
            onClick={() => setFilter('all')}
            className={`flex-1 py-2.5 rounded-xl transition-all ${
              filter === 'all' 
                ? 'bg-emerald-500 text-slate-950 font-black shadow-md' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            All ({historyItems.length})
          </button>
          <button
            onClick={() => setFilter('completed')}
            className={`flex-1 py-2.5 rounded-xl transition-all ${
              filter === 'completed' 
                ? 'bg-emerald-500 text-slate-950 font-black shadow-md' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            Completed
          </button>
          <button
            onClick={() => setFilter('in_progress')}
            className={`flex-1 py-2.5 rounded-xl transition-all ${
              filter === 'in_progress' 
                ? 'bg-emerald-500 text-slate-950 font-black shadow-md' 
                : 'text-slate-400 hover:text-white'
            }`}
          >
            In Progress
          </button>
        </div>

        {/* LIST ITEMS */}
        <div className="space-y-3">
          {filteredList.map((item) => (
            <div
              key={item.id}
              onClick={() => navigate(`/personalized-guide?id=${item.project_id}`)}
              className="bg-slate-900/90 p-4 sm:p-5 rounded-3xl border border-slate-800 hover:border-emerald-500/50 shadow-lg transition-all cursor-pointer flex items-center justify-between gap-4 group"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center text-2xl font-bold flex-shrink-0 group-hover:scale-105 transition-transform">
                  {item.object_name.includes('Bottle') ? '🧴' : item.object_name.includes('Can') ? '🥫' : item.object_name.includes('Remote') || item.object_name.includes('Electronic') ? '📱' : '📦'}
                </div>

                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-extrabold text-white text-base">{item.object_name}</span>
                    <span className="text-[10px] font-black text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/20">
                      {item.match_score}% Match
                    </span>
                  </div>

                  <p className="text-xs font-semibold text-slate-300 mb-1">
                    Project: <span className="text-emerald-400">{item.recommended_project}</span>
                  </p>

                  <span className="text-[10px] text-slate-500 font-semibold block">Scanned: {item.date}</span>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {item.status === 'completed' ? (
                  <span className="inline-flex items-center gap-1.5 text-xs font-extrabold text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/30">
                    <CheckCircle2 size={14} /> Completed
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 text-xs font-extrabold text-amber-300 bg-amber-500/10 px-3 py-1.5 rounded-full border border-amber-500/30">
                    <Clock size={14} /> Active
                  </span>
                )}

                {/* Delete Button */}
                <button
                  onClick={(e) => handleDeleteItem(e, item.id)}
                  title="Delete scan item"
                  className="p-2.5 rounded-2xl bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 transition-colors"
                >
                  <Trash2 size={16} />
                </button>

                <div className="w-9 h-9 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center text-slate-400 group-hover:bg-emerald-500 group-hover:text-slate-950 transition-colors">
                  <ChevronRight size={18} />
                </div>
              </div>
            </div>
          ))}

          {filteredList.length === 0 && !loading && (
            <div className="bg-slate-900 p-8 rounded-3xl border border-slate-800 text-center">
              <Search size={40} className="mx-auto text-slate-600 mb-2" />
              <h3 className="font-bold text-white text-base">No Scan Records Found</h3>
              <p className="text-xs text-slate-400 mt-1">There are no history records matching this filter.</p>
            </div>
          )}
        </div>

      </div>

    </div>
  );
}
