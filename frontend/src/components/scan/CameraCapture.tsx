import { useState, useRef, useEffect } from 'react';
import { Camera, RefreshCw, Check, X, AlertCircle } from 'lucide-react';

interface CameraCaptureProps {
  onCapture: (imageDataUrl: string) => void;
  onCancel: () => void;
}

export default function CameraCapture({ onCapture, onCancel }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Stop camera tracks cleanly
  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
  };

  // Start camera on mount
  useEffect(() => {
    let active = true;

    async function startCamera() {
      setIsLoading(true);
      setError(null);

      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setError("Camera access isn't available in this browser. Please upload an image instead.");
        setIsLoading(false);
        return;
      }

      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
        });

        if (active) {
          setStream(mediaStream);
          if (videoRef.current) {
            videoRef.current.srcObject = mediaStream;
          }
          setIsLoading(false);
        } else {
          mediaStream.getTracks().forEach((track) => track.stop());
        }
      } catch (err: any) {
        if (active) {
          if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            setError('Camera permission was denied. You can upload an image instead.');
          } else {
            setError('Unable to access camera. Please check your permissions or upload an image.');
          }
          setIsLoading(false);
        }
      }
    }

    startCamera();

    // Clean up media stream when component unmounts
    return () => {
      active = false;
      stopCamera();
    };
  }, []);

  const handleTakePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const video = videoRef.current;
      const canvas = canvasRef.current;

      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;

      const context = canvas.getContext('2d');
      if (context) {
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
        setCapturedImage(dataUrl);
        // Pause live camera stream view while inspecting captured photo
        stopCamera();
      }
    }
  };

  const handleRetake = async () => {
    setCapturedImage(null);
    setIsLoading(true);
    setError(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } },
      });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
    } catch (err: any) {
      setError('Unable to restart camera stream. Please try uploading an image.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUsePhoto = () => {
    if (capturedImage) {
      stopCamera();
      onCapture(capturedImage);
    }
  };

  const handleClose = () => {
    stopCamera();
    onCancel();
  };

  return (
    <div className="flex flex-col items-center justify-between w-full h-full bg-black text-white p-4 rounded-2xl relative overflow-hidden min-h-[400px]">
      {/* Hidden Canvas for Photo Capture */}
      <canvas ref={canvasRef} className="hidden" />

      {/* Header Controls */}
      <div className="w-full flex justify-between items-center z-10 mb-2">
        <span className="text-xs font-semibold uppercase tracking-wider text-green-400 bg-green-950/80 px-3 py-1 rounded-full border border-green-800">
          Camera Mode
        </span>
        <button
          onClick={handleClose}
          className="p-2 bg-gray-800/80 hover:bg-gray-700 rounded-full transition-colors"
          aria-label="Cancel Camera Mode"
        >
          <X size={20} />
        </button>
      </div>

      {/* Viewport Display (Video Stream or Captured Image or Error) */}
      <div className="flex-1 w-full flex items-center justify-center relative overflow-hidden rounded-xl bg-gray-900 my-2">
        {error ? (
          <div className="p-6 text-center text-red-300 max-w-xs flex flex-col items-center gap-3">
            <AlertCircle size={40} className="text-red-400" />
            <p className="text-sm font-medium">{error}</p>
            <button
              onClick={handleClose}
              className="mt-2 bg-white text-gray-900 font-bold px-4 py-2 rounded-lg text-sm"
            >
              Upload Image Instead
            </button>
          </div>
        ) : capturedImage ? (
          <img
            src={capturedImage}
            alt="Captured item preview"
            className="w-full h-full object-contain max-h-[350px]"
          />
        ) : (
          <>
            {isLoading && (
              <div className="absolute inset-0 flex items-center justify-center bg-gray-900 text-gray-400 text-sm">
                Initializing camera...
              </div>
            )}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover max-h-[350px]"
            />
          </>
        )}
      </div>

      {/* Action Footer */}
      {!error && (
        <div className="w-full flex justify-center items-center gap-4 mt-2 z-10">
          {capturedImage ? (
            <>
              <button
                onClick={handleRetake}
                className="flex items-center gap-2 bg-gray-800 hover:bg-gray-700 text-white px-5 py-3 rounded-xl font-medium transition-colors"
              >
                <RefreshCw size={18} />
                Retake
              </button>
              <button
                onClick={handleUsePhoto}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-500 text-white px-6 py-3 rounded-xl font-bold transition-transform hover:scale-105"
              >
                <Check size={18} />
                Use This Photo
              </button>
            </>
          ) : (
            <button
              onClick={handleTakePhoto}
              disabled={isLoading}
              className="flex items-center gap-2 bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white px-8 py-3.5 rounded-full font-bold text-lg shadow-lg transition-transform hover:scale-105 active:scale-95"
            >
              <Camera size={22} />
              Capture Photo
            </button>
          )}
        </div>
      )}
    </div>
  );
}
