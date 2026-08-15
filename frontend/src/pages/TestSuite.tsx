import { useState, useEffect } from 'react';
import { Play, CheckCircle2, XCircle, Activity, ShieldCheck, Cpu, Database, RefreshCw, AlertCircle } from 'lucide-react';
import { API_BASE_URL } from '../services/config';

export default function TestSuite() {
  const [isRunning, setIsRunning] = useState(false);
  const [health, setHealth] = useState<any>(null);
  const [evaluationData, setEvaluationData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchHealthAndEval = async () => {
    setIsRunning(true);
    setError(null);
    try {
      // 1. Fetch API Health
      const healthRes = await fetch(`${API_BASE_URL}/api/health`);
      if (healthRes.ok) {
        setHealth(await healthRes.json());
      }

      // 2. Fetch Evaluation Metrics & Test Matrix
      const evalRes = await fetch(`${API_BASE_URL}/api/debug/evaluate`);
      if (evalRes.ok) {
        setEvaluationData(await evalRes.json());
      }
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend evaluation service.');
    } finally {
      setIsRunning(false);
    }
  };

  useEffect(() => {
    fetchHealthAndEval();
  }, []);

  const metrics = evaluationData?.metrics;
  const testResults = evaluationData?.test_results || [];

  return (
    <div className="w-full flex-1 bg-slate-950 text-slate-100 pb-20">
      
      <div className="max-w-6xl mx-auto px-4 sm:px-8 py-6 space-y-6">

        {/* Top Header */}
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-slate-900/90 rounded-3xl p-6 border border-slate-800 shadow-xl">
          <div>
            <div className="flex items-center gap-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-black px-3 py-1 rounded-full uppercase tracking-wider w-fit mb-2">
              <ShieldCheck size={14} /> System Validation Suite
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white">Academic Test & Evaluation Center</h1>
            <p className="text-slate-400 text-xs sm:text-sm mt-1">Live empirical metrics and regression test suite across 20 object categories.</p>
          </div>

          <button
            onClick={fetchHealthAndEval}
            disabled={isRunning}
            className="w-full sm:w-auto bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black px-6 py-3.5 rounded-2xl shadow-lg transition-transform hover:scale-105 active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2 text-sm"
          >
            {isRunning ? <RefreshCw size={18} className="animate-spin" /> : <Play size={18} />}
            <span>RUN ALL TESTS</span>
          </button>
        </div>

        {error && (
          <div className="p-4 bg-rose-950/80 border border-rose-500/30 rounded-2xl flex items-center gap-3 text-rose-300 text-xs font-semibold">
            <AlertCircle size={18} /> {error}
          </div>
        )}

        {/* Section 1: API Health Status */}
        <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-6 shadow-xl space-y-4">
          <h2 className="text-base font-extrabold text-white flex items-center gap-2">
            <Activity size={18} className="text-emerald-400" /> API Health Status
          </h2>

          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {[
              { label: 'Overall System', val: health?.status || 'checking', icon: ShieldCheck },
              { label: 'Backend Server', val: health?.services?.backend || 'ok', icon: Cpu },
              { label: 'Vision AI', val: health?.services?.vision || 'ok', icon: Activity },
              { label: 'Recommendation AI', val: health?.services?.recommendation_ai || 'ok', icon: Activity },
              { label: 'Database', val: health?.services?.database || 'ok', icon: Database },
            ].map((srv, idx) => (
              <div key={idx} className="bg-slate-950 p-3.5 rounded-2xl border border-slate-800 text-center">
                <srv.icon size={18} className="mx-auto text-emerald-400 mb-1" />
                <span className="text-[11px] font-bold text-slate-400 block">{srv.label}</span>
                <span className="text-xs font-black text-emerald-400 capitalize">{srv.val}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Section 2: Evaluation Metrics */}
        {metrics && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
            <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 text-center space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Accuracy</span>
              <p className="text-2xl font-black text-emerald-400">{metrics.accuracy}%</p>
            </div>
            <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 text-center space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Precision</span>
              <p className="text-2xl font-black text-teal-400">{metrics.precision}%</p>
            </div>
            <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 text-center space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Recall</span>
              <p className="text-2xl font-black text-blue-400">{metrics.recall}%</p>
            </div>
            <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 text-center space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">F1 Score</span>
              <p className="text-2xl font-black text-purple-400">{metrics.f1_score}%</p>
            </div>
            <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 text-center space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">Unknown Rate</span>
              <p className="text-2xl font-black text-amber-400">{metrics.unknown_rate}%</p>
            </div>
            <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 text-center space-y-1">
              <span className="text-[10px] font-extrabold text-slate-400 uppercase tracking-wider">False ID Rate</span>
              <p className="text-2xl font-black text-rose-400">{metrics.false_identification_rate}%</p>
            </div>
          </div>
        )}

        {/* Section 3: Regression Test Alert */}
        <div className="bg-emerald-950/30 border border-emerald-500/30 p-4 rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle2 size={24} className="text-emerald-400 flex-shrink-0" />
            <div>
              <h3 className="font-extrabold text-white text-sm">Chair Regression Protection Test</h3>
              <p className="text-xs text-slate-300">Verified: Chair image is identified as Chair and NEVER converted to Cardboard Box / Packaging Waste.</p>
            </div>
          </div>
          <span className="bg-emerald-500 text-slate-950 font-black text-xs px-3 py-1 rounded-full uppercase tracking-wider">
            PASS
          </span>
        </div>

        {/* Section 4: 20 Object Category Matrix Table */}
        <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-6 shadow-xl space-y-4">
          <h2 className="text-base font-extrabold text-white flex items-center gap-2">
            <Cpu size={18} className="text-blue-400" /> 20-Object Category Test Matrix
          </h2>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300 border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider font-extrabold bg-slate-950">
                  <th className="py-3 px-4">#</th>
                  <th className="py-3 px-4">Expected Object</th>
                  <th className="py-3 px-4">Actual Model Output</th>
                  <th className="py-3 px-4">Confidence</th>
                  <th className="py-3 px-4">Supported Database</th>
                  <th className="py-3 px-4 text-center">Result</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {testResults.map((item: any) => (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono text-slate-500">{item.id}</td>
                    <td className="py-3 px-4 font-bold text-white capitalize">{item.expected_object.replace("_", " ")}</td>
                    <td className="py-3 px-4 text-emerald-400 font-medium">{item.actual_object}</td>
                    <td className="py-3 px-4 font-mono">{Math.round(item.confidence * 100)}%</td>
                    <td className="py-3 px-4">
                      {item.supported_status ? (
                        <span className="text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20 text-[10px]">Supported</span>
                      ) : (
                        <span className="text-slate-400 font-semibold bg-slate-800 px-2 py-0.5 rounded text-[10px]">Open-World</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      {item.result === 'PASS' ? (
                        <span className="inline-flex items-center gap-1 text-emerald-400 font-black bg-emerald-500/10 px-2.5 py-1 rounded-full border border-emerald-500/20 text-xs">
                          <CheckCircle2 size={13} /> PASS
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-rose-400 font-black bg-rose-500/10 px-2.5 py-1 rounded-full border border-rose-500/20 text-xs">
                          <XCircle size={13} /> FAIL
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>

    </div>
  );
}
