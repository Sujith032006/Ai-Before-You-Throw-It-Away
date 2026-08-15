import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings, Wrench, IndianRupee, Hammer, Sparkles, Layers, Clock, AlertCircle, ArrowLeft, Plus, Check, RotateCcw, X } from 'lucide-react';
import { useScan } from '../context/ScanContext';
import { fetchRecommendations } from '../services/recommendationService';
import type { RecommendationRequest } from '../types/recommendation';

const DEFAULT_GOAL_OPTIONS = [
  { label: 'Gardening', key: 'gardening' },
  { label: 'Storage', key: 'storage' },
  { label: 'Decoration', key: 'decoration' },
  { label: 'Useful Item', key: 'useful_item' },
  { label: 'Furniture', key: 'furniture' },
  { label: 'Surprise Me', key: 'surprise_me' }
];

const DEFAULT_TOOL_OPTIONS = ['Scissors', 'Glue', 'Cutter', 'Wire', 'Paint', 'Drill', 'Hammer'];
const DEFAULT_MATERIAL_OPTIONS = ['Soil', 'Cotton', 'String', 'Fabric', 'Cardboard', 'Paper'];

export default function Preferences() {
  const navigate = useNavigate();
  const { 
    detectionResult, setRecommendations, setLastPreferences,
    goals, setGoals, tools, setTools, materials, setMaterials,
    budget, setBudget, difficulty, setDifficulty, timeAvailable, setTimeAvailable
  } = useScan();

  const currentObject = detectionResult?.object || 'bottle';
  const objectDisplayName = detectionResult?.displayName || 'Scanned Item';

  // Custom options state
  const [customGoalsList, setCustomGoalsList] = useState<Array<{ label: string; key: string }>>([]);
  const [customToolsList, setCustomToolsList] = useState<string[]>([]);
  const [customMaterialsList, setCustomMaterialsList] = useState<string[]>([]);

  // Modal input states
  const [activeModal, setActiveModal] = useState<'goal' | 'tool' | 'material' | null>(null);
  const [modalInputValue, setModalInputValue] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const toggleGoal = (goalKey: string) => {
    if (goals.includes(goalKey)) {
      if (goals.length > 1) {
        setGoals(goals.filter(g => g !== goalKey));
      }
    } else {
      setGoals([...goals, goalKey]);
    }
  };

  const toggleTool = (tool: string) => {
    const tLower = tool.toLowerCase();
    if (tools.includes(tLower)) {
      setTools(tools.filter(t => t !== tLower));
    } else {
      setTools([...tools, tLower]);
    }
  };

  const toggleMaterial = (mat: string) => {
    const mLower = mat.toLowerCase();
    if (materials.includes(mLower)) {
      setMaterials(materials.filter(m => m !== mLower));
    } else {
      setMaterials([...materials, mLower]);
    }
  };

  const handleAddCustomItem = () => {
    const val = modalInputValue.trim();
    if (!val) return;

    if (activeModal === 'goal') {
      const k = val.toLowerCase().replace(/\s+/g, '_');
      if (!customGoalsList.some(g => g.key === k)) {
        setCustomGoalsList([...customGoalsList, { label: val, key: k }]);
      }
      if (!goals.includes(k)) {
        setGoals([...goals, k]);
      }
    } else if (activeModal === 'tool') {
      const tLower = val.toLowerCase();
      if (!customToolsList.includes(val)) {
        setCustomToolsList([...customToolsList, val]);
      }
      if (!tools.includes(tLower)) {
        setTools([...tools, tLower]);
      }
    } else if (activeModal === 'material') {
      const mLower = val.toLowerCase();
      if (!customMaterialsList.includes(val)) {
        setCustomMaterialsList([...customMaterialsList, val]);
      }
      if (!materials.includes(mLower)) {
        setMaterials([...materials, mLower]);
      }
    }

    setModalInputValue('');
    setActiveModal(null);
  };

  const handleFindProjects = async () => {
    setIsLoading(true);
    setErrorMessage(null);

    let budgetMin = 0;
    let budgetMax = 50;
    if (budget === '₹50–₹100' || budget === '50-100') {
      budgetMin = 50;
      budgetMax = 100;
    } else if (budget === '₹100+' || budget === '100+') {
      budgetMin = 100;
      budgetMax = 300;
    }

    let maxTimeMins = 30;
    if (timeAvailable === '< 15m' || timeAvailable === '15m') maxTimeMins = 15;
    else if (timeAvailable === '< 60m' || timeAvailable === '60m') maxTimeMins = 60;

    const payload: RecommendationRequest = {
      object_name: currentObject,
      object: {
        object_name: currentObject,
        display_name: objectDisplayName,
        material: detectionResult?.material || 'unknown',
        condition: 'used',
        confidence: detectionResult?.confidence || 0.95
      },
      goal: goals.length > 0 ? goals[0] : 'gardening',
      custom_goal: goals.length > 0 ? goals[goals.length - 1] : undefined,
      tools: tools,
      materials: materials,
      budget_min: budgetMin,
      budget_max: budgetMax,
      budget: { min: budgetMin, max: budgetMax, currency: 'INR' },
      difficulty: difficulty.toLowerCase(),
      max_time_minutes: maxTimeMins,
      time_minutes: maxTimeMins
    };

    try {
      const response = await fetchRecommendations(payload);
      setRecommendations(response);
      setLastPreferences(payload);
      navigate('/recommendations');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to generate recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full flex-1 bg-slate-950 text-slate-100 pb-20 relative">
      
      {/* Custom Add Modal Dialog */}
      {activeModal && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 w-full max-w-md shadow-2xl space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-extrabold text-white text-base capitalize">
                ＋ Add Custom {activeModal}
              </h3>
              <button 
                onClick={() => { setActiveModal(null); setModalInputValue(''); }}
                className="text-slate-400 hover:text-white p-1 rounded-lg bg-slate-800/50"
              >
                <X size={18} />
              </button>
            </div>

            <p className="text-xs text-slate-400">
              {activeModal === 'goal' && 'Enter a specific project goal (e.g., "Something for my bedroom", "Pet house").'}
              {activeModal === 'tool' && 'Enter another tool you have (e.g., "Screwdriver", "Sandpaper", "Saw").'}
              {activeModal === 'material' && 'Enter custom material on hand (e.g., "Wood", "Rope", "Old cloth", "Bottle caps").'}
            </p>

            <input
              type="text"
              value={modalInputValue}
              onChange={(e) => setModalInputValue(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') handleAddCustomItem(); }}
              placeholder={activeModal === 'goal' ? 'e.g. Something for college' : activeModal === 'tool' ? 'e.g. Screwdriver' : 'e.g. Rope'}
              className="w-full bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-emerald-500"
              autoFocus
            />

            <div className="flex gap-2 justify-end pt-2">
              <button
                onClick={() => { setActiveModal(null); setModalInputValue(''); }}
                className="px-4 py-2 bg-slate-800 text-slate-300 font-bold text-xs rounded-xl hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={handleAddCustomItem}
                className="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs rounded-xl shadow-md"
              >
                Add {activeModal.toUpperCase()}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 flex flex-col items-center justify-center p-6 text-center">
          <div className="w-16 h-16 border-4 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin mb-4"></div>
          <h2 className="font-black text-white text-2xl mb-1">Calculating Recommendations...</h2>
          <p className="text-slate-400 text-sm max-w-sm">
            Matching compatibility for <span className="text-emerald-400 font-extrabold">{objectDisplayName}</span> against available tools, materials, and time constraints.
          </p>
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 sm:px-8 py-6 space-y-6">

        {/* Top Title Bar */}
        <div className="flex items-center justify-between">
          <div>
            <span className="bg-emerald-500/10 text-emerald-400 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider border border-emerald-500/20">
              Upcycling {objectDisplayName}
            </span>
            <h1 className="text-2xl sm:text-3xl font-black text-white mt-2 mb-1">Customize Your Preferences</h1>
            <p className="text-slate-400 text-xs sm:text-sm">Tap the ＋ icons to add custom goals, tools, and materials to your request.</p>
          </div>

          <button 
            onClick={() => navigate('/result')}
            className="p-2.5 bg-slate-900 hover:bg-slate-800 text-slate-300 rounded-2xl border border-slate-800 transition-colors"
          >
            <ArrowLeft size={20} />
          </button>
        </div>

        {errorMessage && (
          <div className="p-4 bg-rose-950/80 border border-rose-500/30 rounded-2xl flex items-start gap-3 text-rose-300 text-xs font-medium">
            <AlertCircle size={20} className="mt-0.5 flex-shrink-0" />
            <div>{errorMessage}</div>
          </div>
        )}

        <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-6 sm:p-8 space-y-8 shadow-xl">

          {/* Goal Section */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <h2 className="flex items-center gap-2 font-extrabold text-white text-base">
                <Settings size={18} className="text-emerald-400" /> What do you want to make?
              </h2>
              <span className="text-xs font-bold text-emerald-400 bg-emerald-950/60 px-2.5 py-0.5 rounded-full border border-emerald-500/30">
                Selected: {goals.length}
              </span>
            </div>
            <div className="flex flex-wrap gap-2.5">
              {[...DEFAULT_GOAL_OPTIONS, ...customGoalsList].map(g => {
                const isSelected = goals.includes(g.key);
                return (
                  <button
                    key={g.key}
                    onClick={() => toggleGoal(g.key)}
                    className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center gap-1.5 ${
                      isSelected 
                        ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20 ring-2 ring-emerald-300' 
                        : 'bg-slate-950 text-slate-300 hover:bg-slate-800 border border-slate-800'
                    }`}
                  >
                    {isSelected ? <Check size={15} className="text-slate-950 stroke-[3]" /> : <Plus size={15} className="text-emerald-400" />}
                    <span>{g.label}</span>
                  </button>
                );
              })}

              <button
                onClick={() => setActiveModal('goal')}
                className="px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-emerald-950/60 hover:bg-emerald-900/80 text-emerald-400 border border-dashed border-emerald-500/40 transition-all flex items-center gap-1.5"
              >
                <Plus size={15} className="text-emerald-400" />
                <span>Custom Goal</span>
              </button>
            </div>
          </div>

          {/* Tools Section */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <h2 className="flex items-center gap-2 font-extrabold text-white text-base">
                <Wrench size={18} className="text-blue-400" /> What tools do you have?
              </h2>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-blue-400 bg-blue-950/60 px-2.5 py-0.5 rounded-full border border-blue-500/30">
                  Selected: {tools.length}
                </span>
                {tools.length > 0 && (
                  <button 
                    onClick={() => setTools([])}
                    className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 bg-slate-800/60 px-2 py-0.5 rounded-md"
                  >
                    <RotateCcw size={11} /> Clear
                  </button>
                )}
              </div>
            </div>
            <div className="flex flex-wrap gap-2.5">
              {[...DEFAULT_TOOL_OPTIONS, ...customToolsList].map(tool => {
                const tLower = tool.toLowerCase();
                const isSelected = tools.includes(tLower);
                return (
                  <button
                    key={tool}
                    onClick={() => toggleTool(tool)}
                    className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold border transition-all flex items-center gap-1.5 ${
                      isSelected
                        ? 'border-blue-500 bg-blue-500/20 text-blue-300 shadow-md ring-1 ring-blue-400' 
                        : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    {isSelected ? <Check size={15} className="text-blue-300 stroke-[3]" /> : <Plus size={15} className="text-blue-400" />}
                    <span>{tool}</span>
                  </button>
                );
              })}

              <button
                onClick={() => setActiveModal('tool')}
                className="px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-blue-950/60 hover:bg-blue-900/80 text-blue-400 border border-dashed border-blue-500/40 transition-all flex items-center gap-1.5"
              >
                <Plus size={15} className="text-blue-400" />
                <span>Custom Tool</span>
              </button>
            </div>
          </div>

          {/* Materials Section */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <h2 className="flex items-center gap-2 font-extrabold text-white text-base">
                <Layers size={18} className="text-teal-400" /> Materials on hand
              </h2>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-teal-400 bg-teal-950/60 px-2.5 py-0.5 rounded-full border border-teal-500/30">
                  Selected: {materials.length}
                </span>
                {materials.length > 0 && (
                  <button 
                    onClick={() => setMaterials([])}
                    className="text-[11px] text-slate-400 hover:text-white flex items-center gap-1 bg-slate-800/60 px-2 py-0.5 rounded-md"
                  >
                    <RotateCcw size={11} /> Clear
                  </button>
                )}
              </div>
            </div>
            <div className="flex flex-wrap gap-2.5">
              {[...DEFAULT_MATERIAL_OPTIONS, ...customMaterialsList].map(mat => {
                const mLower = mat.toLowerCase();
                const isSelected = materials.includes(mLower);
                return (
                  <button
                    key={mat}
                    onClick={() => toggleMaterial(mat)}
                    className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold border transition-all flex items-center gap-1.5 ${
                      isSelected
                        ? 'border-teal-500 bg-teal-500/20 text-teal-300 shadow-md ring-1 ring-teal-400' 
                        : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    {isSelected ? <Check size={15} className="text-teal-300 stroke-[3]" /> : <Plus size={15} className="text-teal-400" />}
                    <span>{mat}</span>
                  </button>
                );
              })}

              <button
                onClick={() => setActiveModal('material')}
                className="px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold bg-teal-950/60 hover:bg-teal-900/80 text-teal-400 border border-dashed border-teal-500/40 transition-all flex items-center gap-1.5"
              >
                <Plus size={15} className="text-teal-400" />
                <span>Custom Material</span>
              </button>
            </div>
          </div>

          {/* Budget Section */}
          <div>
            <h2 className="flex items-center gap-2 font-extrabold text-white mb-3 text-base">
              <IndianRupee size={18} className="text-amber-400" /> Budget Range
            </h2>
            <div className="flex bg-slate-950 rounded-2xl p-1.5 border border-slate-800">
              {['₹0–₹50', '₹50–₹100', '₹100+'].map(b => (
                <button
                  key={b}
                  onClick={() => setBudget(b)}
                  className={`flex-1 py-3 text-xs sm:text-sm font-bold rounded-xl transition-all ${
                    budget === b
                      ? 'bg-slate-900 text-emerald-400 shadow-md border border-slate-800'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {b}
                </button>
              ))}
            </div>
          </div>

          {/* Difficulty & Time Sections */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
            <div>
              <h2 className="flex items-center gap-2 font-extrabold text-white mb-3 text-base">
                <Hammer size={18} className="text-purple-400" /> Difficulty Level
              </h2>
              <div className="grid grid-cols-3 gap-2">
                {['Easy', 'Medium', 'Hard'].map(diff => (
                  <button
                    key={diff}
                    onClick={() => setDifficulty(diff)}
                    className={`py-3 rounded-xl text-xs font-bold border transition-all ${
                      difficulty.toLowerCase() === diff.toLowerCase()
                        ? 'border-purple-500 bg-purple-500/20 text-purple-300 ring-1 ring-purple-400'
                        : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    {diff}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <h2 className="flex items-center gap-2 font-extrabold text-white mb-3 text-base">
                <Clock size={18} className="text-amber-400" /> Time Available
              </h2>
              <div className="grid grid-cols-3 gap-2">
                {[
                  { label: '< 15m', val: '< 15m' },
                  { label: '< 30m', val: '< 30m' },
                  { label: '< 60m', val: '< 60m' },
                ].map(t => (
                  <button
                    key={t.val}
                    onClick={() => setTimeAvailable(t.val)}
                    className={`py-3 rounded-xl text-xs font-bold border transition-all ${
                      timeAvailable === t.val
                        ? 'border-amber-500 bg-amber-500/20 text-amber-300 ring-1 ring-amber-400'
                        : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                    }`}
                  >
                    {t.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Action CTA */}
          <button 
            onClick={handleFindProjects}
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black py-4 rounded-2xl shadow-xl transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 flex items-center justify-center gap-2 text-base"
          >
            <Sparkles size={22} />
            Find Reuse Ideas ({goals.length} Goals Selected)
          </button>

        </div>

      </div>

    </div>
  );
}
