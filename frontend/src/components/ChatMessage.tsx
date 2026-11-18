import React, { useState } from 'react';
import { User, Bot, Copy, Check, ChevronDown, ChevronUp, BookOpen } from 'lucide-react';
import type { ChatMessage as ChatMessageType } from '../types';
import { SourceCard } from './SourceCard';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === 'user';
  const [copied, setCopied] = useState(false);
  const [showSources, setShowSources] = useState(true);

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`flex gap-3 my-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <div className="w-8 h-8 rounded-full bg-[#0B192C] flex items-center justify-center text-[#C5A880] shrink-0 mt-0.5 shadow-sm">
          <Bot className="w-4 h-4" />
        </div>
      )}

      <div className={`flex flex-col max-w-[85%] md:max-w-[78%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div
          className={`p-4 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? 'bg-[#0B192C] text-white rounded-tr-none shadow-sm'
              : 'bg-white text-slate-800 border border-slate-200 rounded-tl-none shadow-sm'
          }`}
        >
          <div className="whitespace-pre-wrap">{message.content}</div>

          {message.isStreaming && (
            <span className="inline-block w-2 h-4 ml-1 bg-[#C5A880] animate-pulse" />
          )}

          {!isUser && !message.isStreaming && (
            <div className="mt-3 pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
              <span>Verified AI Output</span>
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1 hover:text-[#0B192C] transition-colors p-1"
                title="Copy response"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>
            </div>
          )}
        </div>

        {/* Source References Section */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 w-full">
            <button
              onClick={() => setShowSources(!showSources)}
              className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 transition-colors mb-2"
            >
              <BookOpen className="w-3.5 h-3.5 text-[#C5A880]" />
              <span>Verified Sources ({message.sources.length})</span>
              {showSources ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
            </button>

            {showSources && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mt-1">
                {message.sources.map((src, idx) => (
                  <SourceCard key={idx} source={src} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>

      {isUser && (
        <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600 shrink-0 mt-0.5">
          <User className="w-4 h-4" />
        </div>
      )}
    </div>
  );
};
