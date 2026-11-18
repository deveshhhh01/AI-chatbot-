import React from 'react';
import { ExternalLink, MapPin, Building2, Bed, Bath, Maximize2 } from 'lucide-react';
import type { ProjectItem } from '../types';

interface ProjectCardProps {
  project: ProjectItem;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  const isDarGlobal = project.source.toLowerCase().includes('darglobal');

  return (
    <div className="flex flex-col rounded-xl border border-slate-200 bg-white overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200">
      {project.image_urls && project.image_urls.length > 0 && (
        <div className="h-44 w-full bg-slate-100 overflow-hidden relative">
          <img
            src={project.image_urls[0]}
            alt={project.project_name}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as HTMLElement).style.display = 'none';
            }}
          />
          <span
            className={`absolute top-3 left-3 px-2.5 py-1 text-xs font-bold rounded shadow-sm ${
              isDarGlobal ? 'bg-[#0B192C] text-[#C5A880]' : 'bg-emerald-700 text-white'
            }`}
          >
            {project.source}
          </span>
        </div>
      )}

      <div className="p-4 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-start justify-between gap-2">
            <h3 className="font-semibold text-slate-900 text-base line-clamp-1">
              {project.project_name}
            </h3>
            {project.price?.formatted && (
              <span className="text-sm font-bold text-[#B3956D] shrink-0">
                {project.price.formatted}
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1">
            <MapPin className="w-3.5 h-3.5 text-slate-400" />
            <span>
              {project.location.city}, {project.location.country}
            </span>
          </div>

          <p className="mt-2 text-xs text-slate-600 line-clamp-3 leading-relaxed">
            {project.description}
          </p>

          <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-100 text-xs text-slate-600">
            {project.property_type && (
              <span className="flex items-center gap-1">
                <Building2 className="w-3.5 h-3.5 text-slate-400" />
                {project.property_type}
              </span>
            )}
            {project.bedrooms && (
              <span className="flex items-center gap-1">
                <Bed className="w-3.5 h-3.5 text-slate-400" />
                {project.bedrooms} Beds
              </span>
            )}
            {project.bathrooms && (
              <span className="flex items-center gap-1">
                <Bath className="w-3.5 h-3.5 text-slate-400" />
                {project.bathrooms} Baths
              </span>
            )}
            {project.area_sqm && (
              <span className="flex items-center gap-1">
                <Maximize2 className="w-3.5 h-3.5 text-slate-400" />
                {project.area_sqm} m²
              </span>
            )}
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-400">
            {project.developer ? `By ${project.developer}` : 'Official Platform Listing'}
          </span>
          <a
            href={project.source_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-xs font-semibold text-[#0B192C] hover:text-[#C5A880] transition-colors"
          >
            <span>View Original</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </div>
  );
};
