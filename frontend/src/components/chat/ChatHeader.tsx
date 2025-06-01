import React from "react";
import { ShoppingBag } from "lucide-react";

export const ChatHeader: React.FC = () => {
  return (
    <div className="bg-white/80 backdrop-blur-md shadow-sm border-b border-white/20">
      <div className="max-w-4xl mx-auto px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="bg-gradient-to-r from-pink-500 to-purple-600 p-2 rounded-xl">
            <ShoppingBag className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="font-bold text-xl text-gray-900">Style Assistant</h1>
            <p className="text-sm text-gray-600">
              Your personal fashion curator
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
