import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Play, CheckCircle2, ArrowRight, Sparkles, ShieldCheck, Zap, Bot } from 'lucide-react';
import { useScan } from '../context/ScanContext';

const DEMO_SAMPLE_OBJECTS = [
  { name: 'Chair', icon: '🪑', material: 'wood', isSupported: false, category: 'Furniture', confidence: '96%' },
  { name: 'Plastic Bottle', icon: '🍾', material: 'plastic', isSupported: true, category: 'Household Container', confidence: '98%' },
  { name: 'Cardboard Box', icon: '📦', material: 'cardboard', isSupported: true, category: 'Packaging Waste', confidence: '97%' },
  { name: 'Laptop', icon: '💻', material: 'metal & electronics', isSupported: false, category: 'Electronics', confidence: '95%' },
  { name: 'Glass Jar', icon: '🫙', material: 'glass', isSupported: true, category: 'Pantry Storage', confidence: '96%' },
  { name: 'Tin Can', icon: '🥫', material: 'metal', isSupported: true, category: 'Kitchen Packaging', confidence: '94%' },
];

const DEMO_STEPS = [
  { num: 1, label: 'Scan an object', desc: 'User uploads or clicks a demo sample image.' },
  { num: 2, label: 'AI identifies it', desc: 'Gemini Vision AI returns exact object identity & material.' },
  { num: 3, label: 'Choose what you want to make', desc: 'User selects goal (Gardening, Storage, Custom).' },
  { num: 4, label: 'Select tools & materials', desc: 'User toggles available tools (Scissors, Glue, etc.).' },
  { num: 5, label: 'Set budget & time', desc: 'User selects budget ceiling (₹0–₹50, ₹100+) & duration.' },
  { num: 6, label: 'Get personalized ideas', desc: 'AI scores & ranks top 3 upcycling projects.' },
  { num: 7, label: 'Follow instructions', desc: 'Step-by-step personalized DIY guide with pro tips.' },
  { num: 8, label: 'Ask AI anything', desc: 'Context-aware AI assistant modifies steps & answers questions.' },
];

export default function DemoMode() {
  const navigate = useNavigate();
  const { setDetectionResult, setGoals, setTools, setMaterials, setBudget } = useScan();

  const [activeStepIndex, setActiveStepIndex] = useState(0);
  const [selectedDemoObj, setSelectedDemoObj] = useState(DEMO_SAMPLE_OBJECTS[0]);

  const handleStartDemo = (obj = selectedDemoObj) => {
    setSelectedDemoObj(obj);
    setActiveStepIndex(7); // Mark all steps complete

    // Inject demo detection result into ScanContext
    const rawName = obj.name.toLowerCase().replace(/\s+/g, '_');
    setDetectionResult({
      object: rawName,
      displayName: obj.name,
      material: obj.material,
      category: obj.category,
      supported: obj.isSupported,
      confidence: 0.96,
      confidenceLevel: 'high',
      status: obj.isSupported ? 'identified' : 'identified_but_unsupported'
    });

    setGoals(['gardening']);
    setTools(['scissors']);
    setMaterials(['soil']);
    setBudget('₹0–₹50');

    setTimeout(() => {
      navigate('/preferences');
    }, 1200);
  };

  return (
    <div className="w-full flex-1 bg-slate-950 text-slate-100 pb-20">
      
      <div className="max-w-6xl mx-auto px-4 sm:px-8 py-6 space-y-6">

        {/* Top Header Banner */}
        <div className="bg-gradient-to-r from-slate-900 via-emerald-950 to-slate-900 rounded-3xl p-6 sm:p-8 border border-emerald-500/30 shadow-2xl space-y-4">
          <div className="flex items-center gap-2 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-black px-3.5 py-1.5 rounded-full uppercase tracking-wider w-fit">
            <Sparkles size={14} /> Examiner & Hackathon Demo Walkthrough
          </div>

          <h1 className="text-2xl sm:text-4xl font-black text-white leading-tight">AI Before You Throw It Away</h1>
          <p className="text-slate-300 text-xs sm:text-sm max-w-3xl leading-relaxed">
            Experience the complete 8-stage intelligent upcycling pipeline. Select a sample physical object below to test real-time object identification, dynamic preference matching, and reactive AI assistance.
          </p>

          <div className="pt-2">
            <button
              onClick={() => handleStartDemo(selectedDemoObj)}
              className="bg-gradient-to-r from-emerald-500 via-teal-500 to-emerald-600 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black text-sm px-8 py-4 rounded-2xl shadow-xl transition-transform hover:scale-105 active:scale-95 flex items-center gap-2"
            >
              <Play size={20} />
              START DEMO WITH {selectedDemoObj.name.toUpperCase()}
            </button>
          </div>
        </div>

        {/* Sample Demo Objects Selector */}
        <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-6 shadow-xl space-y-4">
          <h2 className="text-base font-extrabold text-white flex items-center gap-2">
            <Zap size={18} className="text-emerald-400" /> Select Demo Object
          </h2>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {DEMO_SAMPLE_OBJECTS.map((obj, idx) => {
              const isSelected = selectedDemoObj.name === obj.name;
              return (
                <button
                  key={idx}
                  onClick={() => { setSelectedDemoObj(obj); handleStartDemo(obj); }}
                  className={`p-4 rounded-2xl border text-center transition-all flex flex-col items-center justify-between space-y-2 ${
                    isSelected
                      ? 'border-emerald-500 bg-emerald-500/10 ring-2 ring-emerald-400/40 text-white'
                      : 'border-slate-800 bg-slate-950 hover:bg-slate-800/60 text-slate-300'
                  }`}
                >
                  <span className="text-3xl">{obj.icon}</span>
                  <div>
                    <span className="font-extrabold text-xs block text-white">{obj.name}</span>
                    <span className="text-[10px] text-slate-400 block capitalize">{obj.material}</span>
                  </div>
                  <span className="text-[10px] font-bold text-emerald-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    {obj.isSupported ? 'Supported' : 'Open-World'}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* 8-Step Pipeline Visualization */}
        <div className="bg-slate-900/90 rounded-3xl border border-slate-800 p-6 shadow-xl space-y-4">
          <h2 className="text-base font-extrabold text-white flex items-center gap-2">
            <ShieldCheck size={18} className="text-blue-400" /> Pipeline Execution Stages
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {DEMO_STEPS.map((step, idx) => {
              const isDone = activeStepIndex >= idx;
              return (
                <div
                  key={step.num}
                  className={`p-4 rounded-2xl border transition-all space-y-2 ${
                    isDone
                      ? 'bg-slate-950 border-emerald-500/40'
                      : 'bg-slate-950/40 border-slate-800 opacity-60'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="w-7 h-7 rounded-xl bg-slate-900 text-slate-300 border border-slate-800 text-xs font-bold flex items-center justify-center">
                      {step.num}
                    </span>
                    {isDone ? (
                      <span className="text-emerald-400 font-extrabold text-[11px] flex items-center gap-1">
                        <CheckCircle2 size={14} /> ✓ Done
                      </span>
                    ) : (
                      <span className="text-slate-500 text-[11px]">Pending</span>
                    )}
                  </div>

                  <h3 className="font-extrabold text-sm text-white">{step.label}</h3>
                  <p className="text-xs text-slate-400 leading-normal">{step.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="bg-slate-900 p-6 rounded-3xl border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Bot size={28} className="text-emerald-400" />
            <div>
              <h3 className="font-extrabold text-white text-sm">Ready to Test Interactive AI Assistance?</h3>
              <p className="text-xs text-slate-400">Launch the demo to test live preference customization and contextual AI chat.</p>
            </div>
          </div>

          <button
            onClick={() => handleStartDemo(selectedDemoObj)}
            className="w-full sm:w-auto bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black px-6 py-3 rounded-2xl shadow-md transition-colors text-xs flex items-center justify-center gap-2"
          >
            <span>Launch Live Demo</span>
            <ArrowRight size={16} />
          </button>
        </div>

      </div>

    </div>
  );
}
