import { useState } from 'react';
import { Search, X, Check } from 'lucide-react';
import { AVAILABLE_OBJECTS } from '../../services/mockDetectionService';
import type { AvailableObject } from '../../types/detection';

interface ObjectSelectorProps {
  onSelect: (selected: AvailableObject) => void;
  onClose: () => void;
}

export default function ObjectSelector({ onSelect, onClose }: ObjectSelectorProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredObjects = AVAILABLE_OBJECTS.filter((item) =>
    item.displayName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.material.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-end sm:items-center justify-center p-0 sm:p-4 animate-in fade-in duration-200">
      <div className="bg-white w-full max-w-md rounded-t-3xl sm:rounded-2xl max-h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        
        {/* Header */}
        <div className="p-4 border-b flex justify-between items-center bg-gray-50">
          <div>
            <h2 className="font-bold text-gray-900 text-lg">Select Object</h2>
            <p className="text-xs text-gray-500">Choose what item you are upcycling</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-200 rounded-full transition-colors text-gray-500"
          >
            <X size={20} />
          </button>
        </div>

        {/* Search Field */}
        <div className="p-4 border-b bg-white">
          <div className="relative">
            <Search size={18} className="absolute left-3.5 top-3 text-gray-400" />
            <input
              type="text"
              placeholder="Search items (e.g. bottle, glass, box)..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-gray-100 rounded-xl py-2.5 pl-10 pr-4 text-sm font-medium text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500 border border-transparent"
            />
          </div>
        </div>

        {/* Items List */}
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {filteredObjects.length === 0 ? (
            <div className="py-8 text-center text-gray-400">
              <p className="text-sm font-medium">No matching items found.</p>
            </div>
          ) : (
            filteredObjects.map((item) => (
              <button
                key={item.object}
                onClick={() => onSelect(item)}
                className="w-full flex items-center justify-between p-3.5 rounded-xl border border-gray-100 bg-white hover:bg-green-50/50 hover:border-green-300 transition-all text-left group"
              >
                <div>
                  <h3 className="font-bold text-gray-900 text-base group-hover:text-green-700">
                    {item.displayName}
                  </h3>
                  <div className="flex gap-2 text-xs text-gray-500 mt-0.5">
                    <span>{item.material}</span>
                    <span>•</span>
                    <span>{item.category}</span>
                  </div>
                </div>
                <div className="w-8 h-8 rounded-full bg-gray-100 group-hover:bg-green-600 group-hover:text-white flex items-center justify-center text-gray-400 transition-colors">
                  <Check size={16} />
                </div>
              </button>
            ))
          )}
        </div>

      </div>
    </div>
  );
}
