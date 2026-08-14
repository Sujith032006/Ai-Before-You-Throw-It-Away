import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  CheckCircle, Sparkles, RefreshCw, Smartphone, Tv, Box, Container, Shirt, 
  Book, Search, AlertTriangle, ShieldCheck, HelpCircle, Layers, Lightbulb, ChevronDown, ChevronUp, Terminal 
} from 'lucide-react';
import { useScan } from '../context/ScanContext';
import ObjectSelector from '../components/scan/ObjectSelector';
import { fetchGeneralIdeas } from '../services/detectionService';
import type { AvailableObject, NormalizedObject } from '../types/detection';

const QUICK_CATEGORIES: Array<AvailableObject & { icon: any }> = [
  { object: 'remote_control', displayName: 'Remote Control', material: 'Plastic & Circuit Board', category: 'Electronic Waste', icon: Tv },
  { object: 'cell_phone', displayName: 'Cell Phone', material: 'Glass & Battery', category: 'Electronic Waste', icon: Smartphone },
  { object: 'plastic_bottle', displayName: 'Plastic Bottle', material: 'Plastic (PET)', category: 'Household Container', icon: Container },
  { object: 'tin_can', displayName: 'Tin Can', material: 'Aluminum / Steel', category: 'Food Packaging', icon: Box },
  { object: 'glass_jar', displayName: 'Glass Jar', material: 'Glass', category: 'Glass Container', icon: Box },
  { object: 'cardboard_box', displayName: 'Cardboard Box', material: 'Cardboard / Paper', category: 'Packaging Waste', icon: Box },
  { object: 'plastic_chair', displayName: 'Plastic / Wooden Chair', material: 'Molded Plastic / Wood', category: 'Furniture Waste', icon: Box },
  { object: 'old_tshirt', displayName: 'Old T-Shirt', material: 'Cotton / Fabric', category: 'Textile Waste', icon: Shirt },
  { object: 'book', displayName: 'Old Book', material: 'Paper / Cardboard', category: 'Paper Waste', icon: Book },
];

export default function DetectionResult() {
  const navigate = useNavigate();
  const { selectedImage, detectionResult, setDetectionResult, resetScan } = useScan();
  
  const [isSelectorOpen, setIsSelectorOpen] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  const [generalIdeas, setGeneralIdeas] = useState<string[] | null>(null);
  const [isLoadingIdeas, setIsLoadingIdeas] = useState(false);

  // Default fallback item if direct navigate
  const currentResult = detectionResult || {
    object: 'plastic_bottle',
    displayName: 'Plastic Bottle',
    supported: true,
    confidence: 0.94,
    confidenceText: 'HIGH Confidence',
    confidenceLevel: 'high',
    material: 'Plastic (PET)',
    category: 'Household Container',
    source: 'rf_detr',
    status: 'identified',
    verification: 'consistent'
  };

  const isSupported = currentResult.supported ?? (currentResult.status === 'identified' || currentResult.status === 'high_confidence');
  const isUnsupported = currentResult.status === 'identified_but_unsupported' || (!isSupported && currentResult.object !== 'unknown' && currentResult.status !== 'poor_image_quality');
  const isMultipleObjects = currentResult.status === 'multiple_objects' && currentResult.detectedObjects && currentResult.detectedObjects.length > 1;
  const isUnknown = currentResult.status === 'ambiguous' || currentResult.status === 'unknown' || currentResult.object === 'unknown';
  const isPoorQuality = currentResult.status === 'poor_image_quality';

  const handleManualSelect = (selected: AvailableObject) => {
    setDetectionResult({
      object: selected.object,
      displayName: selected.displayName,
      supported: true,
      confidence: null,
      confidenceText: 'User verified',
      confidenceLevel: 'high',
      material: selected.material,
      category: selected.category,
      image: selectedImage || undefined,
      source: 'user_selected',
      status: 'identified',
      verification: 'consistent'
    });
    setIsSelectorOpen(false);
    setGeneralIdeas(null);
  };

  const handleSelectMultipleObject = (obj: NormalizedObject) => {
    setDetectionResult({
      object: obj.name,
      displayName: obj.display_name,
      supported: obj.supported ?? true,
      confidence: obj.confidence || 0.9,
      confidenceText: `${(obj.confidence_level || 'high').toUpperCase()} Confidence`,
      confidenceLevel: obj.confidence_level || 'high',
      material: obj.material,
      category: obj.category,
      image: selectedImage || undefined,
      source: 'user_selected',
      status: obj.supported ? 'identified' : 'identified_but_unsupported',
      verification: 'consistent'
    });
    setGeneralIdeas(null);
  };

  const handleFetchGeneralIdeas = async () => {
    setIsLoadingIdeas(true);
    const ideas = await fetchGeneralIdeas(currentResult.displayName, currentResult.material);
    setGeneralIdeas(ideas);
    setIsLoadingIdeas(false);
  };

  const handleConfirm = () => {
    navigate('/preferences');
  };

  const handleRetake = () => {
    resetScan();
    navigate('/scan');
  };

  return (
    <div className="flex-1 flex flex-col p-4 sm:p-6 bg-gradient-to-b from-slate-50 via-emerald-50/20 to-white items-center justify-center relative overflow-y-auto">
      
      {/* Search Modal */}
      {isSelectorOpen && (
        <ObjectSelector
          onSelect={handleManualSelect}
          onClose={() => setIsSelectorOpen(false)}
        />
      )}

      <div className="w-full max-w-xl bg-white rounded-3xl shadow-xl border border-gray-100 p-6 sm:p-8 text-center relative overflow-hidden">
        {/* Decorative background curve */}
        <div className="absolute top-0 left-0 w-full h-32 bg-gradient-to-b from-emerald-100/80 via-emerald-50/40 to-transparent -z-0"></div>

        {/* Top Header & Preview */}
        <div className="relative z-10 mx-auto mb-4 flex flex-col items-center">
          {selectedImage ? (
            <div className="w-24 h-24 sm:w-28 sm:h-28 rounded-2xl overflow-hidden shadow-md border-4 border-white bg-gray-100 mb-3">
              <img
                src={selectedImage}
                alt="Detected item"
                className="w-full h-full object-cover"
              />
            </div>
          ) : (
            <div className="bg-emerald-100 text-emerald-600 w-20 h-20 rounded-full flex items-center justify-center shadow-inner mb-3">
              <Sparkles size={36} />
            </div>
          )}

          {/* Status Badges */}
          {isPoorQuality ? (
            <span className="text-xs font-black text-amber-800 bg-amber-100 border border-amber-300 px-3.5 py-1 rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1.5">
              <AlertTriangle size={14} /> Image Quality Low
            </span>
          ) : isUnknown ? (
            <span className="text-xs font-black text-slate-800 bg-slate-200 border border-slate-300 px-3.5 py-1 rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1.5">
              <HelpCircle size={14} /> Identification Uncertain
            </span>
          ) : isMultipleObjects ? (
            <span className="text-xs font-black text-purple-800 bg-purple-100 border border-purple-300 px-3.5 py-1 rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1.5">
              <Layers size={14} /> Multiple Objects Detected
            </span>
          ) : isUnsupported ? (
            <span className="text-xs font-black text-amber-900 bg-amber-100 border border-amber-300 px-3.5 py-1 rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1.5">
              <AlertTriangle size={14} /> Identified • Outside Structured DB
            </span>
          ) : currentResult.source === 'vision_ai' || currentResult.status === 'verified' ? (
            <span className="text-xs font-black text-blue-800 bg-blue-100 border border-blue-200 px-3.5 py-1 rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1.5">
              <ShieldCheck size={14} /> Vision AI Verified
            </span>
          ) : (
            <span className="text-xs font-black text-emerald-800 bg-emerald-100/90 border border-emerald-200 px-3.5 py-1 rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1.5">
              <CheckCircle size={14} /> {currentResult.confidenceLevel ? `${currentResult.confidenceLevel.toUpperCase()} Confidence` : 'RF-DETR High Confidence'}
            </span>
          )}
        </div>

        {/* POOR QUALITY WARNING CARD */}
        {isPoorQuality ? (
          <div className="relative z-10 text-left bg-amber-50 border border-amber-200 p-5 rounded-2xl mb-6 shadow-sm">
            <h3 className="font-extrabold text-amber-900 text-base mb-2 flex items-center gap-2">
              <AlertTriangle size={18} className="text-amber-600" />
              📷 Image Quality is Too Low
            </h3>
            <p className="text-xs text-amber-800 mb-3">
              {currentResult.suggestions && currentResult.suggestions.length > 0
                ? currentResult.suggestions.join(' ')
                : 'Try taking another photo with better lighting and the complete object visible.'}
            </p>
            <button
              onClick={handleRetake}
              className="w-full bg-amber-600 hover:bg-amber-700 text-white font-extrabold text-xs py-2.5 rounded-xl transition-colors flex items-center justify-center gap-1.5"
            >
              <RefreshCw size={14} /> Retake Photo
            </button>
          </div>
        ) : isUnknown ? (
          /* UNKNOWN OBJECT CARD */
          <div className="relative z-10 text-left bg-slate-100 border border-slate-200 p-5 rounded-2xl mb-6 shadow-sm">
            <h3 className="font-extrabold text-slate-900 text-base mb-2 flex items-center gap-2">
              <HelpCircle size={18} className="text-slate-600" />
              🤔 Couldn't Confidently Identify Object
            </h3>
            <p className="text-xs text-slate-700 mb-3">
              Try taking another photo with better lighting and the complete object visible, or select your item from the 1-Tap Quick Select list below.
            </p>
            <button
              onClick={handleRetake}
              className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs py-2.5 rounded-xl transition-colors flex items-center justify-center gap-1.5"
            >
              <RefreshCw size={14} /> Retake Photo
            </button>
          </div>
        ) : isMultipleObjects ? (
          /* MULTIPLE OBJECTS SELECTION SCREEN */
          <div className="relative z-10 text-left bg-purple-50 border border-purple-200 p-5 rounded-2xl mb-6 shadow-sm">
            <h3 className="font-extrabold text-purple-950 text-base mb-1 flex items-center gap-2">
              <Layers size={18} className="text-purple-600" />
              Multiple Objects Detected
            </h3>
            <p className="text-xs text-purple-800 mb-4">
              Select which item in your photo you would like to analyze and upcycle:
            </p>

            <div className="space-y-2.5 mb-4">
              {currentResult.detectedObjects?.map((obj, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSelectMultipleObject(obj)}
                  className="w-full p-3.5 rounded-xl border border-purple-200 bg-white hover:bg-purple-100/70 transition-all flex items-center justify-between text-left group"
                >
                  <div>
                    <span className="font-bold text-gray-900 text-sm block group-hover:text-purple-700">
                      {obj.display_name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {obj.material} • {obj.supported ? '♻️ Reuse Available' : 'Outside Structured Database'}
                    </span>
                  </div>
                  <span className="text-xs font-bold text-purple-700 bg-purple-100 px-2.5 py-1 rounded-lg">
                    Select
                  </span>
                </button>
              ))}
            </div>
          </div>
        ) : isUnsupported ? (
          /* UNSUPPORTED OBJECT SCREEN (CHAIR, LAPTOP, TABLE) */
          <>
            <h2 className="text-xs font-extrabold text-amber-800 uppercase tracking-widest mb-1 relative z-10">Actual Identified Item</h2>
            <h1 className="text-2xl sm:text-3xl font-black text-gray-900 mb-2 relative z-10 tracking-tight">
              {currentResult.displayName}
            </h1>

            <div className="bg-amber-50 rounded-2xl p-4 mb-5 text-left border border-amber-200 relative z-10 text-xs text-amber-900 space-y-2">
              <div className="flex items-center gap-2 font-bold text-amber-950 text-sm">
                <AlertTriangle size={16} className="text-amber-600 flex-shrink-0" />
                <span>Outside Structured Reuse Database</span>
              </div>
              <p className="leading-relaxed">
                We successfully identified this object as <span className="font-bold">{currentResult.displayName}</span> (Material: {currentResult.material}). However, structured step-by-step upcycling recipes for this specific object are not yet available in our verified database.
              </p>
            </div>

            {/* General AI Ideas Section */}
            {generalIdeas ? (
              <div className="bg-gradient-to-b from-teal-50 to-emerald-50 rounded-2xl p-4 mb-6 text-left border border-teal-200 relative z-10 space-y-3">
                <h3 className="font-extrabold text-teal-950 text-sm flex items-center gap-2">
                  <Lightbulb size={16} className="text-teal-600" />
                  General AI Upcycling & Refurbishing Ideas
                </h3>
                <ul className="space-y-2 text-xs text-slate-800">
                  {generalIdeas.map((idea, i) => (
                    <li key={i} className="flex items-start gap-2 bg-white/80 p-2.5 rounded-xl border border-teal-100">
                      <span className="text-teal-600 font-bold">•</span>
                      <span>{idea}</span>
                    </li>
                  ))}
                </ul>
                <p className="text-[10px] text-slate-500 italic">
                  Note: These are general AI-generated ideas and are not validated structured projects.
                </p>
              </div>
            ) : (
              <div className="flex gap-3 mb-6 relative z-10">
                <button
                  onClick={handleFetchGeneralIdeas}
                  disabled={isLoadingIdeas}
                  className="flex-1 bg-teal-600 hover:bg-teal-700 text-white font-extrabold text-sm py-3.5 px-4 rounded-2xl shadow-md transition-all flex items-center justify-center gap-2 border border-teal-500"
                >
                  <Lightbulb size={18} />
                  {isLoadingIdeas ? 'Generating AI Ideas...' : 'Ask AI for General Ideas'}
                </button>

                <button
                  onClick={handleRetake}
                  className="bg-gray-100 hover:bg-gray-200 text-gray-800 font-bold text-xs py-3.5 px-4 rounded-2xl border border-gray-300 transition-colors flex items-center justify-center gap-1.5"
                >
                  <RefreshCw size={14} /> Scan Another
                </button>
              </div>
            )}
          </>
        ) : (
          /* NORMAL SUPPORTED OBJECT DISPLAY */
          <>
            <h2 className="text-xs font-extrabold text-gray-400 uppercase tracking-widest mb-1 relative z-10">AI Identified Item</h2>
            <h1 className="text-2xl sm:text-3xl font-black text-gray-900 mb-4 relative z-10 tracking-tight">
              {currentResult.displayName}
            </h1>

            {/* Detection Metadata Details */}
            <div className="bg-gradient-to-r from-emerald-50/60 to-teal-50/60 rounded-2xl p-4 mb-6 text-left space-y-2.5 border border-emerald-100 relative z-10 text-sm shadow-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-semibold">AI Confidence Level</span>
                <span className="text-emerald-700 font-extrabold flex items-center gap-1.5 bg-emerald-100 px-2.5 py-0.5 rounded-md text-xs uppercase">
                  <CheckCircle size={14} />
                  {currentResult.confidenceText || (currentResult.confidenceLevel ? `${currentResult.confidenceLevel} Confidence` : 'High Confidence')}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-semibold">Detected Material</span>
                <span className="text-gray-900 font-bold capitalize">{currentResult.material}</span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-semibold">Upcycling Category</span>
                <span className="text-gray-900 font-bold">{currentResult.category}</span>
              </div>
            </div>

            {/* Primary Confirm Button */}
            <div className="mb-6 relative z-10">
              <button
                onClick={handleConfirm}
                className="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-lg py-4 px-6 rounded-2xl shadow-lg transition-transform hover:scale-[1.02] active:scale-98 flex items-center justify-center gap-2 border-2 border-emerald-500"
              >
                <CheckCircle size={22} />
                Find Reuse Ideas for {currentResult.displayName}
              </button>
            </div>
          </>
        )}

        {/* Dev Diagnostics Drawer Toggle */}
        {currentResult.debugInfo && (
          <div className="relative z-10 mb-5 border-t border-gray-100 pt-3">
            <button
              onClick={() => setShowDebug(!showDebug)}
              className="text-[11px] font-bold text-slate-500 hover:text-slate-800 flex items-center justify-center gap-1 mx-auto bg-slate-100 px-3 py-1 rounded-lg transition-colors"
            >
              <Terminal size={12} />
              <span>Dev Diagnostics {showDebug ? <ChevronUp size={12} className="inline" /> : <ChevronDown size={12} className="inline" />}</span>
            </button>

            {showDebug && (
              <div className="mt-3 bg-slate-950 text-emerald-400 p-3.5 rounded-xl text-left text-[11px] font-mono space-y-1 overflow-x-auto border border-slate-800 shadow-inner">
                <div>RF-DETR Object: {String(currentResult.debugInfo.rfdetr_object)} (Conf: {String(currentResult.debugInfo.rfdetr_confidence)})</div>
                <div>Vision AI Object: {String(currentResult.debugInfo.vision_ai_object)} (Conf: {String(currentResult.debugInfo.vision_ai_confidence)})</div>
                <div>Extracted Material: {String(currentResult.debugInfo.extracted_material)}</div>
                <div>Verification Status: {String(currentResult.debugInfo.verification_status)}</div>
                <div>Normalized Object: {String(currentResult.debugInfo.normalized_name)}</div>
                <div>Database Supported: {String(currentResult.debugInfo.supported_database_status)}</div>
              </div>
            )}
          </div>
        )}

        {/* 1-Tap Quick Category Selection Grid */}
        <div className="relative z-10 border-t border-gray-100 pt-5 text-left">
          <div className="flex justify-between items-center mb-3">
            <h3 className="text-xs font-black text-gray-500 uppercase tracking-wider flex items-center gap-1.5">
              <RefreshCw size={14} className="text-emerald-600" /> Not quite right? 1-Tap Quick Select
            </h3>
            <button
              onClick={() => setIsSelectorOpen(true)}
              className="text-xs font-extrabold text-emerald-600 hover:text-emerald-800 flex items-center gap-1 bg-emerald-50 hover:bg-emerald-100 px-2.5 py-1 rounded-lg transition-colors"
            >
              <Search size={13} />
              Search All
            </button>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
            {QUICK_CATEGORIES.map((cat) => {
              const isSelected = currentResult.object === cat.object;
              const IconComp = cat.icon;
              return (
                <button
                  key={cat.object}
                  onClick={() => handleManualSelect(cat)}
                  className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between h-20 ${
                    isSelected
                      ? 'bg-emerald-600 text-white border-emerald-600 shadow-md ring-2 ring-emerald-300 scale-[1.02]'
                      : 'bg-gray-50 hover:bg-emerald-50/60 border-gray-200 text-gray-800 hover:border-emerald-300'
                  }`}
                >
                  <div className="flex justify-between items-start">
                    <IconComp size={18} className={isSelected ? 'text-white' : 'text-emerald-600'} />
                    {isSelected && <CheckCircle size={14} className="text-white" />}
                  </div>
                  <span className={`text-xs font-bold truncate leading-snug ${isSelected ? 'text-white' : 'text-gray-900'}`}>
                    {cat.displayName}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

      </div>
      
    </div>
  );
}
