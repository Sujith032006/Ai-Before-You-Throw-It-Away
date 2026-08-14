import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, Sparkles, RefreshCw, Smartphone, Tv, Box, Container, Shirt, Book, Search, AlertTriangle, ShieldCheck, HelpCircle } from 'lucide-react';
import { useScan } from '../context/ScanContext';
import ObjectSelector from '../components/scan/ObjectSelector';
import type { AvailableObject } from '../types/detection';

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

  // Default fallback item if direct navigate
  const currentResult = detectionResult || {
    object: 'plastic_bottle',
    displayName: 'Plastic Bottle',
    confidence: 0.94,
    confidenceText: '94%',
    material: 'Plastic (PET)',
    category: 'Household Container',
    source: 'rf_detr',
    status: 'high_confidence'
  };

  const isUnknown = currentResult.status === 'unknown' || currentResult.object === 'unknown';
  const isPoorQuality = currentResult.status === 'poor_image_quality';

  const handleManualSelect = (selected: AvailableObject) => {
    setDetectionResult({
      object: selected.object,
      displayName: selected.displayName,
      confidence: null,
      confidenceText: 'User verified',
      material: selected.material,
      category: selected.category,
      image: selectedImage || undefined,
      source: 'user_selected',
      status: 'verified'
    });
    setIsSelectorOpen(false);
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
          ) : currentResult.source === 'vision_ai' || currentResult.status === 'verified' ? (
            <span className="text-xs font-black text-blue-800 bg-blue-100 border border-blue-200 px-3.5 py-1 rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1.5">
              <ShieldCheck size={14} /> Vision AI Verified
            </span>
          ) : (
            <span className="text-xs font-black text-emerald-800 bg-emerald-100/90 border border-emerald-200 px-3.5 py-1 rounded-full uppercase tracking-wider shadow-sm flex items-center gap-1.5">
              <CheckCircle size={14} /> RF-DETR High Confidence
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
            <div className="flex gap-2">
              <button
                onClick={handleRetake}
                className="flex-1 bg-amber-600 hover:bg-amber-700 text-white font-extrabold text-xs py-2.5 rounded-xl transition-colors flex items-center justify-center gap-1.5"
              >
                <RefreshCw size={14} /> Retake Photo
              </button>
            </div>
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
            <div className="flex gap-2">
              <button
                onClick={handleRetake}
                className="flex-1 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-xs py-2.5 rounded-xl transition-colors flex items-center justify-center gap-1.5"
              >
                <RefreshCw size={14} /> Retake Photo
              </button>
            </div>
          </div>
        ) : (
          /* NORMAL DETECTION DISPLAY */
          <>
            <h2 className="text-xs font-extrabold text-gray-400 uppercase tracking-widest mb-1 relative z-10">AI Identified Item</h2>
            <h1 className="text-2xl sm:text-3xl font-black text-gray-900 mb-4 relative z-10 tracking-tight">
              {currentResult.displayName}
            </h1>

            {/* Detection Metadata Details */}
            <div className="bg-gradient-to-r from-emerald-50/60 to-teal-50/60 rounded-2xl p-4 mb-6 text-left space-y-2.5 border border-emerald-100 relative z-10 text-sm shadow-sm">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-semibold">AI Confidence Score</span>
                <span className="text-emerald-700 font-extrabold flex items-center gap-1.5 bg-emerald-100 px-2.5 py-0.5 rounded-md">
                  <CheckCircle size={15} />
                  {currentResult.confidenceText || (currentResult.confidence ? `${Math.round(currentResult.confidence * 100)}%` : 'User verified')}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-gray-600 font-semibold">Detected Material</span>
                <span className="text-gray-900 font-bold">{currentResult.material}</span>
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
                Yes, proceed with {currentResult.displayName}
              </button>
            </div>
          </>
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
