import React from 'react';
import { ExternalLink, MapPin, Tag } from 'lucide-react';
import type { SourceReference } from '../types';

interface SourceCardProps {
  source: SourceReference;
}

export const SourceCard: React.FC<SourceCardProps> = ({ source }) => {
  const isDarGlobal = source.source.toLowerCase().includes('darglobal');

  return (
    <a
      href={source.url}
      target="_blank"
      rel="noopener noreferrer"
      className="group block p-3 rounded-lg border border-slate-200 bg-white hover:border-[#C5A880] hover:shadow-sm transition-all duration-200 text-left"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span
            className={`inline-block px-2 py-0.5 text-xs font-semibold rounded ${
              isDarGlobal
                ? 'bg-[#0B192C] text-[#C5A880]'
                : 'bg-emerald-700 text-white'
            }`}
          >
            {source.source}
          </span>
          <h4 className="text-sm font-semibold text-slate-800 group-hover:text-[#B3956D] line-clamp-1">
            {source.title}
          </h4>
        </div>
        <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-[#C5A880] shrink-0" />
      </div>

      {(source.location || source.price) && (
        <div className="flex flex-wrap items-center gap-3 mt-1.5 text-xs text-slate-500">
          {source.location && (
            <span className="flex items-center gap-1">
              <MapPin className="w-3 h-3 text-slate-400" />
              {source.location}
            </span>
          )}
          {source.price && (
            <span className="flex items-center gap-1 font-medium text-slate-700">
              <Tag className="w-3 h-3 text-[#C5A880]" />
              {source.price}
            </span>
          )}
        </div>
      )}

      {source.snippet && (
        <p className="mt-1.5 text-xs text-slate-600 line-clamp-2 leading-relaxed">
          {source.snippet}
        </p>
      )}
    </a>
  );
};
