import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Camera as CameraIcon, Trash2, Sparkles, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useScan } from '../context/ScanContext';
import { analyzeImageWithBackend } from '../services/detectionService';
import CameraCapture from '../components/scan/CameraCapture';

const MAX_FILE_SIZE_MB = 5;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const ALLOWED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];

export default function ScanItem() {
  const navigate = useNavigate();
  const { selectedImage, setSelectedImage, setDetectionResult } = useScan();

  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // File Upload Handler
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setErrorMessage(null);
    const file = e.target.files?.[0];

    if (!file) return;

    if (!ALLOWED_TYPES.includes(file.type)) {
      setErrorMessage('Please select a valid image file (JPG, PNG, or WEBP).');
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setErrorMessage(`This image is too large. Please choose an image smaller than ${MAX_FILE_SIZE_MB}MB.`);
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === 'string') {
        setSelectedImage(reader.result);
      }
    };
    reader.readAsDataURL(file);
  };

  // Camera Capture Handler
  const handleCameraCapture = (imageDataUrl: string) => {
    setSelectedImage(imageDataUrl);
    setIsCameraActive(false);
  };

  // Remove Image
  const handleRemoveImage = () => {
    setSelectedImage(null);
    setErrorMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Analyze Item Handler
  const handleAnalyze = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);
    setErrorMessage(null);

    try {
      const result = await analyzeImageWithBackend(selectedImage);
      setDetectionResult(result);
      navigate('/result');
    } catch (err: any) {
      setErrorMessage(err.message || 'Something went wrong while analyzing the image. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="w-full flex-1 bg-slate-950 text-slate-100 pb-16">
      
      {/* Full Width Desktop Container */}
      <div className="max-w-4xl mx-auto px-4 sm:px-8 py-6 space-y-6">
        
        <div className="text-center sm:text-left">
          <span className="bg-emerald-500/10 text-emerald-400 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider border border-emerald-500/20">
            Step 1 • Computer Vision Object Scanning
          </span>
          <h1 className="text-2xl sm:text-3xl font-black text-white mt-2 mb-1">Scan Your Household Item</h1>
          <p className="text-slate-400 text-xs sm:text-sm">
            Take a photo with your webcam or upload an image of the item you are about to throw away.
          </p>
        </div>

        {/* Hidden File Input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Error Banner */}
        {errorMessage && (
          <div className="p-4 bg-rose-950/80 border border-rose-500/30 rounded-2xl flex items-start gap-3 text-rose-300">
            <AlertCircle size={20} className="mt-0.5 flex-shrink-0" />
            <div className="flex-1 text-xs font-medium">
              {errorMessage}
            </div>
          </div>
        )}

        {/* Camera Mode Overlay */}
        {isCameraActive ? (
          <div className="w-full min-h-[420px]">
            <CameraCapture
              onCapture={handleCameraCapture}
              onCancel={() => setIsCameraActive(false)}
            />
          </div>
        ) : (
          /* Main Image Container / Preview */
          <div className="w-full min-h-[380px] bg-slate-900/90 rounded-3xl border-2 border-dashed border-slate-800 flex flex-col items-center justify-center relative overflow-hidden transition-all shadow-xl p-6">
            
            {isAnalyzing && (
              <div className="absolute inset-0 bg-slate-950/95 backdrop-blur-md flex flex-col items-center justify-center z-20 p-6 text-center">
                <div className="w-16 h-16 border-4 border-emerald-500/20 border-t-emerald-400 rounded-full animate-spin mb-4"></div>
                <p className="text-emerald-400 font-black text-xl mb-1">Running RF-DETR + Vision AI Analysis...</p>
                <p className="text-slate-400 text-xs max-w-xs">Classifying object with RF-DETR Transformer Engine...</p>
              </div>
            )}

            {!selectedImage ? (
              <div className="text-center p-8 flex flex-col items-center">
                <div className="w-20 h-20 rounded-3xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
                  <Sparkles size={40} />
                </div>
                <p className="text-white font-black text-xl mb-1">No Image Selected</p>
                <p className="text-xs text-slate-400 max-w-sm mb-6">
                  Upload a photo or open your device camera to identify the household item.
                </p>

                <div className="flex flex-col sm:flex-row items-center gap-4 w-full max-w-sm">
                  <button
                    onClick={() => {
                      setErrorMessage(null);
                      setIsCameraActive(true);
                    }}
                    className="w-full flex items-center justify-center gap-2.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black py-4 px-6 rounded-2xl shadow-lg transition-transform hover:scale-105"
                  >
                    <CameraIcon size={20} />
                    <span>Use Camera</span>
                  </button>

                  <button
                    onClick={() => {
                      setErrorMessage(null);
                      fileInputRef.current?.click();
                    }}
                    className="w-full flex items-center justify-center gap-2.5 bg-slate-800 hover:bg-slate-700 text-white font-extrabold py-4 px-6 rounded-2xl border border-slate-700 transition-colors"
                  >
                    <Upload size={20} />
                    <span>Upload Image</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="relative w-full flex flex-col items-center justify-center">
                <img
                  src={selectedImage}
                  alt="Selected preview"
                  className="max-h-[380px] max-w-full object-contain rounded-2xl shadow-xl mb-4 border border-slate-800"
                />
                <div className="flex items-center gap-2 text-emerald-400 bg-emerald-500/10 px-4 py-1.5 rounded-full text-xs font-bold border border-emerald-500/20">
                  <CheckCircle2 size={16} />
                  Image Loaded • Ready to Detect
                </div>
              </div>
            )}
          </div>
        )}

        {/* Control Buttons when image is selected */}
        {!isCameraActive && selectedImage && (
          <div className="flex gap-4 max-w-md mx-auto">
            <button
              onClick={handleRemoveImage}
              disabled={isAnalyzing}
              className="flex items-center justify-center gap-2 bg-slate-900 hover:bg-rose-950/80 text-slate-300 hover:text-rose-300 font-bold py-4 px-6 rounded-2xl border border-slate-800 transition-colors disabled:opacity-50"
            >
              <Trash2 size={20} />
              Remove
            </button>

            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="flex-1 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-slate-950 font-black py-4 px-8 rounded-2xl shadow-xl transition-transform hover:scale-105 active:scale-95 disabled:opacity-70 flex justify-center items-center gap-2.5 text-base"
            >
              <Sparkles size={22} />
              {isAnalyzing ? 'Analyzing...' : 'Analyze Item Now'}
            </button>
          </div>
        )}

      </div>

    </div>
  );
}
