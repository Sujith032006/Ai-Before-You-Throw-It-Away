import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Settings, Wrench, IndianRupee, Hammer, Sparkles, Layers, Clock, AlertCircle, ArrowLeft } from 'lucide-react';
import { useScan } from '../context/ScanContext';
import { fetchRecommendations } from '../services/recommendationService';
import type { RecommendationRequest } from '../types/recommendation';

export default function Preferences() {
  const navigate = useNavigate();
  const { detectionResult, setRecommendations, setLastPreferences } = useScan();

  const currentObject = detectionResult?.object || 'bottle';
  const objectDisplayName = detectionResult?.displayName || 'Scanned Item';

  const [selectedGoal, setSelectedGoal] = useState('Gardening');
  const [selectedTools, setSelectedTools] = useState<string[]>(['Scissors']);
  const [selectedMaterials, setSelectedMaterials] = useState<string[]>(['Soil']);
  const [selectedBudget, setSelectedBudget] = useState('₹0–₹50');
  const [selectedDifficulty, setSelectedDifficulty] = useState('Easy');
  const [maxTime, setMaxTime] = useState<number>(30);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const toggleTool = (tool: string) => {
    if (selectedTools.includes(tool)) {
      setSelectedTools(selectedTools.filter(t => t !== tool));
    } else {
      setSelectedTools([...selectedTools, tool]);
    }
  };

  const toggleMaterial = (mat: string) => {
    if (selectedMaterials.includes(mat)) {
      setSelectedMaterials(selectedMaterials.filter(m => m !== mat));
    } else {
      setSelectedMaterials([...selectedMaterials, mat]);
    }
  };

  const handleFindProjects = async () => {
    setIsLoading(true);
    setErrorMessage(null);

    const goalMap: Record<string, string> = {
      'Gardening': 'gardening',
      'Storage': 'storage',
      'Decoration': 'decoration',
      'Useful Item': 'useful_item',
      'Surprise Me': 'surprise_me'
    };

    let budgetMin = 0;
    let budgetMax = 50;
    if (selectedBudget === '₹50–₹100') {
      budgetMin = 50;
      budgetMax = 100;
    } else if (selectedBudget === '₹100+') {
      budgetMin = 100;
      budgetMax = 300;
    }

    const payload: RecommendationRequest = {
      object_name: currentObject,
      goal: goalMap[selectedGoal] || 'gardening',
      tools: selectedTools.map(t => t.toLowerCase()),
      materials: selectedMaterials.map(m => m.toLowerCase()),
      budget_min: budgetMin,
      budget_max: budgetMax,
      difficulty: selectedDifficulty.toLowerCase(),
      max_time_minutes: maxTime
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
    <div className="w-full flex-1 bg-slate-950 text-slate-100 pb-20">
      
      {/* Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-slate-950/95 backdrop-blur-md z-50 flex flex-col items-center justify-center p-6 text-center">
          <div className="w-16 h-16 border-4 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin mb-4"></div>
          <h2 className="font-black text-white text-2xl mb-1">Calculating Recommendations...</h2>
          <p className="text-slate-400 text-sm max-w-sm">
            Matching compatibility for <span className="text-emerald-400 font-extrabold">{objectDisplayName}</span> against available tools and constraints.
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
            <p className="text-slate-400 text-xs sm:text-sm">Filter DIY ideas matching your available tools, materials, and time.</p>
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
            <h2 className="flex items-center gap-2 font-extrabold text-white mb-3 text-base">
              <Settings size={18} className="text-emerald-400" /> What do you want to make?
            </h2>
            <div className="flex flex-wrap gap-2.5">
              {['Gardening', 'Storage', 'Decoration', 'Useful Item', 'Surprise Me'].map(goal => (
                <button
                  key={goal}
                  onClick={() => setSelectedGoal(goal)}
                  className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold transition-all ${
                    selectedGoal === goal 
                      ? 'bg-emerald-500 text-slate-950 shadow-lg shadow-emerald-500/20' 
                      : 'bg-slate-950 text-slate-300 hover:bg-slate-800 border border-slate-800'
                  }`}
                >
                  {goal}
                </button>
              ))}
            </div>
          </div>

          {/* Tools Section */}
          <div>
            <h2 className="flex items-center gap-2 font-extrabold text-white mb-3 text-base">
              <Wrench size={18} className="text-blue-400" /> What tools do you have?
            </h2>
            <div className="flex flex-wrap gap-2.5">
              {['Scissors', 'Glue', 'Cutter', 'Wire', 'Paint', 'Drill', 'Hammer'].map(tool => (
                <button
                  key={tool}
                  onClick={() => toggleTool(tool)}
                  className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold border transition-all ${
                    selectedTools.includes(tool)
                      ? 'border-blue-500 bg-blue-500/10 text-blue-300' 
                      : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  {tool}
                </button>
              ))}
            </div>
          </div>

          {/* Materials Section */}
          <div>
            <h2 className="flex items-center gap-2 font-extrabold text-white mb-3 text-base">
              <Layers size={18} className="text-teal-400" /> Materials on hand
            </h2>
            <div className="flex flex-wrap gap-2.5">
              {['Soil', 'Cotton', 'String', 'Fabric', 'Cardboard', 'Paper'].map(mat => (
                <button
                  key={mat}
                  onClick={() => toggleMaterial(mat)}
                  className={`px-4 py-2.5 rounded-xl text-xs sm:text-sm font-bold border transition-all ${
                    selectedMaterials.includes(mat)
                      ? 'border-teal-500 bg-teal-500/10 text-teal-300' 
                      : 'border-slate-800 bg-slate-950 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  {mat}
                </button>
              ))}
            </div>
          </div>

          {/* Budget Section */}
          <div>
            <h2 className="flex items-center gap-2 font-extrabold text-white mb-3 text-base">
              <IndianRupee size={18} className="text-amber-400" /> Budget Range
            </h2>
            <div className="flex bg-slate-950 rounded-2xl p-1.5 border border-slate-800">
              {['₹0–₹50', '₹50–₹100', '₹100+'].map(budget => (
                <button
                  key={budget}
                  onClick={() => setSelectedBudget(budget)}
                  className={`flex-1 py-3 text-xs sm:text-sm font-bold rounded-xl transition-all ${
                    selectedBudget === budget
                      ? 'bg-slate-900 text-emerald-400 shadow-md border border-slate-800'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {budget}
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
                    onClick={() => setSelectedDifficulty(diff)}
                    className={`py-3 rounded-xl text-xs font-bold border transition-all ${
                      selectedDifficulty === diff
                        ? 'border-purple-500 bg-purple-500/10 text-purple-300'
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
                  { label: '< 15m', val: 15 },
                  { label: '< 30m', val: 30 },
                  { label: '< 60m', val: 60 },
                ].map(t => (
                  <button
                    key={t.val}
                    onClick={() => setMaxTime(t.val)}
                    className={`py-3 rounded-xl text-xs font-bold border transition-all ${
                      maxTime === t.val
                        ? 'border-amber-500 bg-amber-500/10 text-amber-300'
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
            Find Reuse Ideas
          </button>

        </div>

      </div>

    </div>
  );
}
