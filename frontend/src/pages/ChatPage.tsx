import React, { useState, useEffect, useRef } from 'react';
import { Menu, Building, MapPin, Compass, ShieldCheck } from 'lucide-react';
import type { ChatMessage as ChatMessageType, SourceReference } from '../types';
import { ChatMessage } from '../components/ChatMessage';
import { ChatInput } from '../components/ChatInput';
import { LoadingIndicator } from '../components/LoadingIndicator';
import { apiService } from '../services/api';

interface ChatPageProps {
  onToggleSidebar: () => void;
  currentSessionId: string;
  onNewChat: () => void;
}

const SUGGESTED_PROMPTS = [
  {
    title: 'Explore DarGlobal Projects',
    prompt: 'What luxury residential projects are available on DarGlobal?',
    source: 'DarGlobal',
  },
  {
    title: 'Find Properties in Dubai',
    prompt: 'Show me all luxury real estate projects in Dubai with their amenities and locations.',
    source: 'DarGlobal',
  },
  {
    title: 'Explore Wasalt Listings',
    prompt: 'What properties are listed on Wasalt in Saudi Arabia and what are their prices?',
    source: 'Wasalt',
  },
  {
    title: 'Compare Projects',
    prompt: 'Compare luxury branded developments from DarGlobal with residential properties from Wasalt.',
    source: 'Both',
  },
  {
    title: 'Check Amenities in W Residences',
    prompt: 'What amenities and features are available in W Residences Dubai Downtown?',
    source: 'DarGlobal',
  },
  {
    title: 'Properties with 3+ Bedrooms',
    prompt: 'Which properties and villas have 3 or more bedrooms across DarGlobal and Wasalt?',
    source: 'Both',
  },
];

export const ChatPage: React.FC<ChatPageProps> = ({
  onToggleSidebar,
  currentSessionId,
  onNewChat,
}) => {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Load chat history when session changes
  useEffect(() => {
    const loadHistory = async () => {
      try {
        setError(null);
        const data = await apiService.getChatHistory(currentSessionId);
        if (data && data.messages) {
          const loaded: ChatMessageType[] = data.messages.map((m: any, idx: number) => ({
            id: `msg_${idx}_${Date.now()}`,
            role: m.role,
            content: m.content,
            sources: m.sources,
            timestamp: m.created_at,
          }));
          setMessages(loaded);
        }
      } catch (err) {
        console.warn('Could not load history for session:', err);
      }
    };
    if (currentSessionId) {
      loadHistory();
    }
  }, [currentSessionId]);

  const handleSendMessage = async (text: string, sourceFilter: string) => {
    setError(null);
    const userMsgId = `user_${Date.now()}`;
    const assistantMsgId = `asst_${Date.now()}`;

    const userMsg: ChatMessageType = {
      id: userMsgId,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    let assistantAnswer = '';
    let assistantSources: SourceReference[] = [];

    // Attempt streaming with fallback to non-streaming
    try {
      await apiService.streamMessage(
        text,
        currentSessionId,
        sourceFilter,
        (chunk) => {
          assistantAnswer += chunk;
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last && last.id === assistantMsgId) {
              return [
                ...prev.slice(0, -1),
                {
                  ...last,
                  content: assistantAnswer,
                  isStreaming: true,
                },
              ];
            } else {
              return [
                ...prev,
                {
                  id: assistantMsgId,
                  role: 'assistant',
                  content: assistantAnswer,
                  sources: assistantSources,
                  timestamp: new Date().toISOString(),
                  isStreaming: true,
                },
              ];
            }
          });
        },
        (metadata) => {
          assistantSources = metadata.sources || [];
          setMessages((prev) => {
            const last = prev[prev.length - 1];
            if (last && last.id === assistantMsgId) {
              return [
                ...prev.slice(0, -1),
                {
                  ...last,
                  sources: assistantSources,
                  retrieved_documents: metadata.retrieved_documents,
                },
              ];
            }
            return prev;
          });
        },
        async (streamErr) => {
          console.warn('Stream failed or completed with warning. Falling back to non-streaming endpoint...', streamErr);
          try {
            const resp = await apiService.sendMessage(text, currentSessionId, sourceFilter);
            setMessages((prev) => {
              const withoutStreaming = prev.filter((m) => m.id !== assistantMsgId);
              return [
                ...withoutStreaming,
                {
                  id: assistantMsgId,
                  role: 'assistant',
                  content: resp.answer,
                  sources: resp.sources,
                  retrieved_documents: resp.retrieved_documents,
                  timestamp: new Date().toISOString(),
                  isStreaming: false,
                },
              ];
            });
          } catch (apiErr: any) {
            setError(apiErr.message || 'Failed to generate response.');
          } finally {
            setIsLoading(false);
          }
        },
        () => {
          // Stream completed
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMsgId ? { ...m, isStreaming: false } : m
            )
          );
          setIsLoading(false);
        }
      );
    } catch (err: any) {
      console.error('Error in send message:', err);
      setError(err.message || 'An error occurred.');
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-screen overflow-hidden bg-[#F8FAFC]">
      {/* Top Navbar */}
      <header className="h-16 border-b border-slate-200 bg-white/80 backdrop-blur-md px-4 sm:px-6 flex items-center justify-between z-10 shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="md:hidden p-2 rounded-lg text-slate-600 hover:bg-slate-100 transition-colors"
            title="Toggle Menu"
          >
            <Menu className="w-5 h-5" />
          </button>
          <div>
            <h2 className="text-base font-bold text-[#0B192C] flex items-center gap-2">
              <span>Real Estate Intelligence Assistant</span>
              <span className="hidden sm:inline-block px-2 py-0.5 text-[10px] font-semibold bg-[#C5A880]/15 text-[#987850] rounded-full border border-[#C5A880]/30">
                DarGlobal &amp; Wasalt
              </span>
            </h2>
            <p className="text-xs text-slate-500 hidden sm:block">
              Accurate, grounded insights backed by live vector retrieval
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="hidden sm:inline">RAG Knowledge Base Connected</span>
            <span className="sm:hidden">Connected</span>
          </div>
        </div>
      </header>

      {/* Main Messages Container */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 max-w-4xl w-full mx-auto">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center min-h-[70vh] text-center max-w-2xl mx-auto py-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#0B192C] to-[#1E3050] text-[#C5A880] flex items-center justify-center mb-5 shadow-lg border border-[#C5A880]/20">
              <Building className="w-8 h-8" />
            </div>

            <h1 className="text-2xl sm:text-3xl font-extrabold text-[#0B192C] tracking-tight">
              Real Estate Intelligence Assistant
            </h1>
            <p className="text-sm text-slate-600 mt-2 max-w-md leading-relaxed">
              Explore property insights, residential projects, amenities, and developer data from{' '}
              <strong className="text-slate-900">DarGlobal</strong> and{' '}
              <strong className="text-slate-900">Wasalt</strong> using AI.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mt-8 w-full text-left">
              {SUGGESTED_PROMPTS.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSendMessage(item.prompt, 'all')}
                  className="p-3.5 rounded-xl border border-slate-200 bg-white hover:border-[#C5A880] hover:shadow-sm transition-all duration-200 group cursor-pointer"
                >
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-500 mb-1">
                    <span className="group-hover:text-[#B3956D]">{item.title}</span>
                    <span
                      className={`px-1.5 py-0.5 rounded text-[10px] ${
                        item.source === 'DarGlobal'
                          ? 'bg-[#0B192C] text-[#C5A880]'
                          : item.source === 'Wasalt'
                          ? 'bg-emerald-700 text-white'
                          : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {item.source}
                    </span>
                  </div>
                  <p className="text-xs text-slate-700 font-medium line-clamp-2 leading-relaxed">
                    {item.prompt}
                  </p>
                </button>
              ))}
            </div>

            <div className="flex items-center gap-4 mt-8 pt-6 border-t border-slate-200 text-xs text-slate-400">
              <span className="flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" /> Grounded in Verified Data
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <Compass className="w-3.5 h-3.5 text-[#C5A880]" /> Multi-Turn Memory
              </span>
              <span>•</span>
              <span className="flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5 text-slate-500" /> UAE &amp; Saudi Arabia
              </span>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} message={msg} />
            ))}

            {isLoading && !messages.some((m) => m.isStreaming) && <LoadingIndicator />}
            {error && (
              <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-xs my-2">
                <strong>Error:</strong> {error}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Pinned Bottom Input */}
      <ChatInput
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        onNewChat={onNewChat}
      />
    </div>
  );
};
