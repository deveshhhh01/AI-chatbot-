import React from 'react';
import {
  MessageSquare,
  Plus,
  Building,
  Database,
  Cpu,
  ChevronRight,
  ShieldCheck
} from 'lucide-react';
import type { SourcesOverview, HealthStatus } from '../types';

interface SidebarProps {
  conversations: Array<{ session_id: string; title: string; updated_at: string }>;
  currentSessionId: string;
  onSelectSession: (sessionId: string) => void;
  onNewChat: () => void;
  sourcesOverview: SourcesOverview | null;
  health: HealthStatus | null;
  isOpen: boolean;
  onClose: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  conversations,
  currentSessionId,
  onSelectSession,
  onNewChat,
  sourcesOverview,
  health,
  isOpen,
  onClose,
}) => {
  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-30 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed md:static inset-y-0 left-0 z-40 w-72 bg-[#0B192C] text-slate-200 flex flex-col justify-between border-r border-[#1B2A47] transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        {/* Top Header & Branding */}
        <div className="flex flex-col h-full overflow-hidden">
          <div className="p-4 border-b border-[#1B2A47]">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-[#C5A880] to-[#987850] flex items-center justify-center text-[#0B192C] shadow-md font-bold text-lg">
                D&W
              </div>
              <div>
                <h1 className="font-bold text-white text-base tracking-tight leading-tight">
                  DarGlobal <span className="text-[#C5A880] font-normal">&amp;</span> Wasalt
                </h1>
                <p className="text-[11px] text-slate-400 font-medium tracking-wide">
                  Real Estate Intelligence AI
                </p>
              </div>
            </div>

            <button
              onClick={() => {
                onNewChat();
                if (window.innerWidth < 768) onClose();
              }}
              className="w-full mt-4 flex items-center justify-center gap-2 px-3 py-2.5 rounded-lg bg-[#C5A880] hover:bg-[#B3956D] text-[#0B192C] font-semibold text-sm transition-all shadow-sm cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>New Conversation</span>
            </button>
          </div>

          {/* Conversation History List */}
          <div className="flex-1 overflow-y-auto p-3 space-y-1">
            <div className="px-2 py-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Recent Chats
            </div>

            {conversations.length === 0 ? (
              <div className="px-3 py-4 text-xs text-slate-400 text-center italic">
                No past conversations yet
              </div>
            ) : (
              conversations.map((c) => {
                const isSelected = c.session_id === currentSessionId;
                return (
                  <button
                    key={c.session_id}
                    onClick={() => {
                      onSelectSession(c.session_id);
                      if (window.innerWidth < 768) onClose();
                    }}
                    className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium text-left transition-colors ${
                      isSelected
                        ? 'bg-[#1E3050] text-[#C5A880] font-semibold'
                        : 'text-slate-300 hover:bg-[#132238] hover:text-white'
                    }`}
                  >
                    <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-70" />
                    <span className="truncate flex-1">{c.title || 'Conversation'}</span>
                    <ChevronRight className="w-3 h-3 shrink-0 opacity-50" />
                  </button>
                );
              })
            )}
          </div>

          {/* Data Sources and System Stats Card */}
          <div className="p-3 border-t border-[#1B2A47] space-y-2 bg-[#081220]/60">
            <div className="px-1 text-[11px] font-semibold text-slate-400 uppercase tracking-wider flex items-center justify-between">
              <span>Data Coverage</span>
              <ShieldCheck className="w-3 h-3 text-[#C5A880]" />
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2 rounded-lg bg-[#0F223D] border border-[#1E3252]">
                <div className="text-[11px] font-semibold text-[#C5A880] flex items-center gap-1">
                  <Building className="w-3 h-3" /> DarGlobal
                </div>
                <div className="text-[10px] text-slate-300 mt-0.5">UAE, Oman, Spain, UK, KSA</div>
              </div>

              <div className="p-2 rounded-lg bg-[#0F223D] border border-[#1E3252]">
                <div className="text-[11px] font-semibold text-emerald-400 flex items-center gap-1">
                  <Building className="w-3 h-3" /> Wasalt
                </div>
                <div className="text-[10px] text-slate-300 mt-0.5">Riyadh, Jeddah, Khobar</div>
              </div>
            </div>

            {/* Provider and Knowledge Stats */}
            <div className="pt-2 border-t border-[#15233A] text-[11px] text-slate-400 space-y-1">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1">
                  <Database className="w-3 h-3 text-[#C5A880]" /> Vector Chunks:
                </span>
                <span className="font-semibold text-slate-200">
                  {health?.vector_store_chunks ?? sourcesOverview?.vector_indexed_chunks ?? 0}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1">
                  <Cpu className="w-3 h-3 text-cyan-400" /> Active LLM:
                </span>
                <span className="font-semibold text-slate-200 truncate max-w-[130px]" title={health?.active_llm_provider || 'Gemini'}>
                  {health?.active_llm_provider || 'Gemini 2.5'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </aside>
    </>
  );
};
