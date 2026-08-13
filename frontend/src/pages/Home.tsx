import { Link } from 'react-router-dom';
import { Camera, LayoutDashboard, History, Recycle } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 text-center bg-gradient-to-b from-white via-emerald-50/50 to-emerald-100/30 overflow-y-auto">
      
      <div className="max-w-md w-full my-auto py-6">
        
        {/* Main Hero Header */}
        <div className="mb-8">
          <div className="inline-flex items-center gap-2 bg-emerald-100 text-emerald-800 font-extrabold text-xs px-3.5 py-1.5 rounded-full uppercase tracking-wider mb-4 border border-emerald-200 shadow-sm">
            <Recycle size={15} /> AI Reuse & Upcycling Assistant
          </div>

          <h1 className="text-3xl sm:text-4xl font-black text-gray-900 mb-3 tracking-tight leading-tight">
            ♻️ Before You Throw It Away
          </h1>
          
          <p className="text-sm sm:text-base text-gray-600 mb-8 max-w-xs mx-auto leading-relaxed">
            Give everyday objects another life. Scan items with your camera to unlock creative, personalized upcycling projects.
          </p>

          {/* Primary Action Button */}
          <Link 
            to="/scan" 
            className="w-full inline-flex items-center justify-center gap-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-extrabold text-lg py-4 px-8 rounded-2xl shadow-lg transition-transform hover:scale-105 active:scale-95 border-2 border-emerald-500 mb-4"
          >
            <Camera size={24} />
            Scan an Item
          </Link>

          {/* Secondary Dashboard & History Buttons */}
          <div className="grid grid-cols-2 gap-3">
            <Link
              to="/dashboard"
              className="inline-flex items-center justify-center gap-2 bg-white hover:bg-gray-50 text-emerald-800 font-bold text-xs py-3 px-4 rounded-xl border border-emerald-200 shadow-sm transition-colors"
            >
              <LayoutDashboard size={16} />
              My Dashboard
            </Link>

            <Link
              to="/history"
              className="inline-flex items-center justify-center gap-2 bg-white hover:bg-gray-50 text-gray-700 font-bold text-xs py-3 px-4 rounded-xl border border-gray-200 shadow-sm transition-colors"
            >
              <History size={16} />
              My History
            </Link>
          </div>
        </div>

        {/* 3-Step Process Explanation */}
        <div className="w-full space-y-3 text-left">
          <h2 className="text-xs font-bold text-gray-400 uppercase tracking-widest text-center mb-3">How It Works in 3 Steps</h2>
          
          <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex items-start gap-3.5">
            <div className="bg-emerald-100 text-emerald-700 p-2.5 rounded-xl font-black text-sm flex-shrink-0">
              1
            </div>
            <div>
              <h3 className="font-bold text-gray-900 text-sm">Scan Household Item</h3>
              <p className="text-xs text-gray-500 mt-0.5">Use your device camera or upload a photo for instant computer vision YOLO detection.</p>
            </div>
          </div>

          <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex items-start gap-3.5">
            <div className="bg-teal-100 text-teal-700 p-2.5 rounded-xl font-black text-sm flex-shrink-0">
              2
            </div>
            <div>
              <h3 className="font-bold text-gray-900 text-sm">Discover Upcycling Projects</h3>
              <p className="text-xs text-gray-500 mt-0.5">Our recommendation engine matches ranked DIY project ideas based on your available tools and goal.</p>
            </div>
          </div>

          <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 flex items-start gap-3.5">
            <div className="bg-purple-100 text-purple-700 p-2.5 rounded-xl font-black text-sm flex-shrink-0">
              3
            </div>
            <div>
              <h3 className="font-bold text-gray-900 text-sm">Personalize & Reuse</h3>
              <p className="text-xs text-gray-500 mt-0.5">Generative AI tailors step-by-step instructions and answers questions via an AI Project Assistant.</p>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
