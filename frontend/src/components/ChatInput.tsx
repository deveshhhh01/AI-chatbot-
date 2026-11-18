import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Filter, RefreshCw } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string, sourceFilter: string) => void;
  isLoading: boolean;
  onNewChat: () => void;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  isLoading,
  onNewChat,
}) => {
  const [input, setInput] = useState('');
  const [sourceFilter, setSourceFilter] = useState('all');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim(), sourceFilter);
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full bg-white border-t border-slate-200 p-4 shadow-lg">
      <div className="max-w-4xl mx-auto flex flex-col gap-2.5">
        {/* Source Filter and Session Controls */}
        <div className="flex items-center justify-between text-xs">
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1 font-medium text-slate-500">
              <Filter className="w-3.5 h-3.5 text-[#C5A880]" />
              Filter by Platform:
            </span>
            <div className="flex bg-slate-100 p-0.5 rounded-lg border border-slate-200">
              <button
                type="button"
                onClick={() => setSourceFilter('all')}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  sourceFilter === 'all'
                    ? 'bg-[#0B192C] text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                All Sources
              </button>
              <button
                type="button"
                onClick={() => setSourceFilter('DarGlobal')}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  sourceFilter === 'DarGlobal'
                    ? 'bg-[#0B192C] text-[#C5A880] shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                DarGlobal
              </button>
              <button
                type="button"
                onClick={() => setSourceFilter('Wasalt')}
                className={`px-2.5 py-1 rounded-md font-medium transition-all ${
                  sourceFilter === 'Wasalt'
                    ? 'bg-emerald-700 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Wasalt
              </button>
            </div>
          </div>

          <button
            type="button"
            onClick={onNewChat}
            className="flex items-center gap-1 text-slate-500 hover:text-[#0B192C] transition-colors p-1"
            title="Start new conversation"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">New Session</span>
          </button>
        </div>

        {/* Input Textarea & Send Button */}
        <form
          onSubmit={handleSubmit}
          className="relative flex items-end gap-2 bg-slate-50 border border-slate-200 rounded-xl p-2 focus-within:border-[#C5A880] focus-within:bg-white focus-within:ring-2 focus-within:ring-[#C5A880]/20 transition-all"
        >
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about properties in Dubai, Riyadh, amenities, prices, or developers..."
            className="w-full resize-none bg-transparent px-2 py-1.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none max-h-36"
            disabled={isLoading}
          />

          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`p-2.5 rounded-lg transition-all duration-200 shrink-0 ${
              input.trim() && !isLoading
                ? 'bg-[#0B192C] text-[#C5A880] hover:bg-[#132847] shadow-sm cursor-pointer'
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
            title="Send Message"
          >
            {isLoading ? (
              <Sparkles className="w-4 h-4 animate-spin text-[#C5A880]" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </form>

        <div className="flex items-center justify-between text-[11px] text-slate-400 px-1">
          <span>Press Enter to send, Shift + Enter for new line</span>
          <span>Verified RAG Architecture • No fabricated property citations</span>
        </div>
      </div>
    </div>
  );
};
