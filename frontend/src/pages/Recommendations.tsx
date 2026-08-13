import { Link, useNavigate } from 'react-router-dom';
import { Clock, IndianRupee, Zap, ChevronRight, Star, CheckCircle2, AlertTriangle, ArrowLeft } from 'lucide-react';
import { useScan } from '../context/ScanContext';

export default function Recommendations() {
  const navigate = useNavigate();
  const { recommendations, detectionResult, recordScanActivity } = useScan();

  const objectDisplayName = detectionResult?.displayName || recommendations?.object_name || 'Scanned Object';
  const recList = recommendations?.recommendations || [];

  if (recList.length === 0) {
    return (
      <div className="w-full flex-1 bg-slate-950 text-slate-100 flex flex-col items-center justify-center p-6 text-center">
        <div className="bg-amber-500/10 border border-amber-500/20 text-amber-400 p-5 rounded-3xl mb-4">
          <AlertTriangle size={40} />
        </div>
        <h2 className="text-2xl font-black text-white mb-2">No Matching Projects Found</h2>
        <p className="text-sm text-slate-400 max-w-sm mb-6">
          {recommendations?.message || "No suitable upcycling projects were found for these preferences."}
        </p>
        <Link
          to="/preferences"
          className="bg-emerald-500 text-slate-950 font-black px-8 py-3.5 rounded-2xl shadow-lg hover:bg-emerald-400 transition-colors"
        >
          Change Preferences
        </Link>
      </div>
    );
  }

  const topMatch = recommendations?.top_recommendation || recList[0];
  const otherMatches = recList.filter(item => item.project_id !== topMatch.project_id);

  return (
    <div className="w-full flex-1 bg-slate-950 text-slate-100 pb-16">
      
      {/* Full Width Desktop Container */}
      <div className="max-w-6xl mx-auto px-4 sm:px-8 py-6 space-y-6">
        
        {/* Top Header */}
        <div className="flex items-center justify-between">
          <div>
            <span className="text-xs font-extrabold text-slate-400 uppercase tracking-widest">Ranked Upcycling Ideas</span>
            <h1 className="text-2xl sm:text-3xl font-black text-white mt-1">Top Ideas for {objectDisplayName}</h1>
          </div>
          <Link to="/preferences" className="p-2.5 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-2xl border border-slate-800 transition-colors">
            <ArrowLeft size={20} />
          </Link>
        </div>

        {/* TOP MATCH CARD (FULL WIDTH HERO CARD) */}
        <div className="bg-gradient-to-br from-slate-900 via-emerald-950/40 to-slate-900 rounded-3xl border-2 border-emerald-500/40 p-6 sm:p-8 shadow-2xl relative overflow-hidden">
          
          {/* Top Ribbon */}
          <div className="bg-gradient-to-r from-emerald-500 to-teal-500 text-slate-950 text-xs font-black px-4 py-2 rounded-br-2xl absolute top-0 left-0 flex items-center gap-1.5 shadow-md">
            <Star size={14} fill="currentColor" />
            ⭐ Best Option For You
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
            
            <div className="lg:col-span-2 space-y-4">
              <div>
                <h2 className="font-black text-2xl sm:text-3xl text-white mb-2 leading-tight">{topMatch.name}</h2>
                <p className="text-slate-300 text-sm leading-relaxed">{topMatch.description}</p>
              </div>

              {/* Metadata Badges */}
              <div className="flex flex-wrap items-center gap-3 text-xs text-slate-300 bg-slate-950 p-3 rounded-2xl border border-slate-800 font-semibold">
                <span className="flex items-center gap-1.5 text-purple-400"><Zap size={15} /> {topMatch.difficulty}</span>
                <span>•</span>
                <span className="flex items-center gap-1.5 text-amber-400"><Clock size={15} /> {topMatch.estimated_time_minutes} mins</span>
                <span>•</span>
                <span className="flex items-center gap-1.5 text-emerald-400"><IndianRupee size={15} /> ₹{topMatch.estimated_cost_min}–₹{topMatch.estimated_cost_max}</span>
              </div>

              {/* Why Recommended Explainability Factors */}
              <div className="space-y-2 pt-2">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Why this project was matched:</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {topMatch.matched_factors.map((factor, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-xs text-slate-200 bg-slate-950/60 p-2.5 rounded-xl border border-slate-800">
                      <CheckCircle2 size={16} className="text-emerald-400 mt-0.5 flex-shrink-0" />
                      <span>{factor}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Match Score & Action Column */}
            <div className="flex flex-col items-center justify-between bg-slate-950/80 p-6 rounded-3xl border border-slate-800 text-center space-y-4">
              <div>
                <div className="w-24 h-24 rounded-full bg-emerald-500/10 border-2 border-emerald-500/30 flex flex-col items-center justify-center mx-auto mb-2">
                  <span className="text-3xl font-black text-emerald-400">{topMatch.match_score}%</span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Match</span>
                </div>
                <p className="text-xs text-slate-400">High compatibility score based on your available tools.</p>
              </div>

              <button
                onClick={() => {
                  recordScanActivity(objectDisplayName, topMatch.project_id, topMatch.name, topMatch.match_score);
                  navigate(`/personalized-guide?id=${topMatch.project_id}`);
                }}
                className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black py-4 px-6 rounded-2xl shadow-xl transition-transform hover:scale-105 active:scale-95 flex items-center justify-center gap-2 text-base"
              >
                Show Me How
                <ChevronRight size={20} />
              </button>
            </div>

          </div>

        </div>

        {/* OTHER RECOMMENDATIONS LIST */}
        {otherMatches.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xs font-extrabold text-slate-400 uppercase tracking-widest mb-3">Other Alternatives</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {otherMatches.map((rec) => (
                <div 
                  key={rec.project_id}
                  onClick={() => navigate(`/personalized-guide?id=${rec.project_id}`)}
                  className="bg-slate-900/90 rounded-3xl border border-slate-800 p-5 hover:border-emerald-500/50 transition-all cursor-pointer shadow-lg flex items-center justify-between gap-4 group"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1.5">
                      <span className="text-emerald-400 font-extrabold text-xs bg-emerald-500/10 px-2.5 py-0.5 rounded-md border border-emerald-500/20">
                        {rec.match_score}% Match
                      </span>
                      <span className="text-xs font-semibold text-slate-400">{rec.difficulty}</span>
                    </div>
                    
                    <h3 className="font-extrabold text-white text-base group-hover:text-emerald-400 transition-colors mb-1">{rec.name}</h3>
                    
                    <div className="flex items-center gap-3 text-xs text-slate-400 mt-2">
                      <span className="flex items-center gap-1"><Clock size={14} /> {rec.estimated_time_minutes} mins</span>
                      <span className="flex items-center gap-1"><IndianRupee size={14} /> ₹{rec.estimated_cost_min}–₹{rec.estimated_cost_max}</span>
                    </div>
                  </div>
                  
                  <div className="w-10 h-10 rounded-2xl bg-slate-950 border border-slate-800 flex items-center justify-center text-slate-400 group-hover:bg-emerald-500 group-hover:text-slate-950 transition-colors">
                    <ChevronRight size={20} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

      </div>

    </div>
  );
}
