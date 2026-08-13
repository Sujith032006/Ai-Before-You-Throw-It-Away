import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { CheckCircle, AlertCircle, Sparkles } from 'lucide-react';
import { useScan } from '../context/ScanContext';
import ObjectSelector from '../components/scan/ObjectSelector';
import type { AvailableObject } from '../types/detection';

export default function DetectionResult() {
  const navigate = useNavigate();
  const { selectedImage, detectionResult, setDetectionResult } = useScan();
  const [isSelectorOpen, setIsSelectorOpen] = useState(false);

  // Fallback default mock if context is empty (e.g. direct page refresh)
  const currentResult = detectionResult || {
    object: 'plastic_bottle',
    displayName: 'Plastic Bottle',
    confidence: 0.96,
    confidenceText: '96%',
    material: 'Plastic (PET)',
    category: 'Household Container',
  };

  const handleManualSelect = (selected: AvailableObject) => {
    setDetectionResult({
      object: selected.object,
      displayName: selected.displayName,
      confidence: null,
      confidenceText: 'Manually selected',
      material: selected.material,
      category: selected.category,
      image: selectedImage || undefined,
    });
    setIsSelectorOpen(false);
  };

  const handleConfirm = () => {
    navigate('/preferences');
  };

  return (
    <div className="flex-1 flex flex-col p-6 bg-gray-50 items-center justify-center relative">
      
      {/* Object Selector Modal */}
      {isSelectorOpen && (
        <ObjectSelector
          onSelect={handleManualSelect}
          onClose={() => setIsSelectorOpen(false)}
        />
      )}

      <div className="w-full max-w-sm bg-white rounded-2xl shadow-lg border border-gray-100 p-6 text-center relative overflow-hidden">
        {/* Top Decorative Background */}
        <div className="absolute top-0 left-0 w-full h-28 bg-gradient-to-b from-green-100 to-green-50/20 rounded-b-[40%] -z-0"></div>

        {/* Image Preview / Icon Badge */}
        <div className="relative z-10 mx-auto mb-4 flex flex-col items-center">
          {selectedImage ? (
            <div className="w-24 h-24 rounded-2xl overflow-hidden shadow-md border-2 border-white bg-gray-100 mb-2">
              <img
                src={selectedImage}
                alt="Detected item"
                className="w-full h-full object-cover"
              />
            </div>
          ) : (
            <div className="bg-green-100 text-green-600 w-16 h-16 rounded-full flex items-center justify-center shadow-inner mb-2">
              <Sparkles size={32} />
            </div>
          )}
          <span className="text-xs font-bold text-green-700 bg-green-100 px-3 py-0.5 rounded-full uppercase tracking-wider">
            Detection Complete
          </span>
        </div>

        <h2 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-1 relative z-10">Detected Object</h2>
        <h1 className="text-2xl font-extrabold text-gray-900 mb-4 relative z-10">
          {currentResult.displayName}
        </h1>

        {/* Detection Metadata Card */}
        <div className="bg-gray-50 rounded-xl p-4 mb-6 text-left space-y-2.5 border border-gray-100 relative z-10 text-sm">
          <div className="flex justify-between items-center">
            <span className="text-gray-500 font-medium">Confidence</span>
            <span className="text-green-600 font-bold flex items-center gap-1">
              <CheckCircle size={15} />
              {currentResult.confidenceText || (currentResult.confidence ? `${Math.round(currentResult.confidence * 100)}%` : 'Manually selected')}
            </span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-gray-500 font-medium">Material</span>
            <span className="text-gray-900 font-semibold">{currentResult.material}</span>
          </div>

          <div className="flex justify-between items-center">
            <span className="text-gray-500 font-medium">Category</span>
            <span className="text-gray-900 font-semibold">{currentResult.category}</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3 relative z-10">
          <button
            onClick={handleConfirm}
            className="flex items-center justify-center w-full bg-green-600 hover:bg-green-700 text-white font-bold py-3.5 px-6 rounded-xl shadow-md transition-transform hover:-translate-y-0.5 active:translate-y-0"
          >
            ✓ Yes, that's correct
          </button>
          
          <button
            onClick={() => setIsSelectorOpen(true)}
            className="flex items-center justify-center gap-2 w-full bg-white hover:bg-gray-50 text-gray-700 font-semibold py-3 px-6 rounded-xl border border-gray-200 transition-colors text-sm"
          >
            <AlertCircle size={16} />
            Change Object
          </button>
        </div>
      </div>
      
    </div>
  );
}
