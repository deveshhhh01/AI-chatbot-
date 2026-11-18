import React from 'react';
import { Bot } from 'lucide-react';

export const LoadingIndicator: React.FC = () => {
  return (
    <div className="flex items-start gap-3 my-4">
      <div className="w-8 h-8 rounded-full bg-[#0B192C] flex items-center justify-center text-[#C5A880] shrink-0 shadow-sm">
        <Bot className="w-4 h-4" />
      </div>
      <div className="p-3.5 rounded-2xl bg-white border border-slate-200 shadow-sm max-w-sm">
        <div className="flex items-center gap-1.5 py-1">
          <div className="w-2 h-2 rounded-full bg-[#C5A880] animate-bounce [animation-delay:-0.3s]" />
          <div className="w-2 h-2 rounded-full bg-[#C5A880] animate-bounce [animation-delay:-0.15s]" />
          <div className="w-2 h-2 rounded-full bg-[#C5A880] animate-bounce" />
          <span className="text-xs text-slate-400 ml-2 font-medium">Searching knowledge base...</span>
        </div>
      </div>
    </div>
  );
};
