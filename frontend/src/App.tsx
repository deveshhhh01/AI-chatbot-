import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { ChatPage } from './pages/ChatPage';
import { apiService } from './services/api';
import type { SourcesOverview, HealthStatus } from './types';

export const App: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string>(() => {
    return `session_${Date.now()}`;
  });
  const [conversations, setConversations] = useState<Array<{ session_id: string; title: string; updated_at: string }>>([]);
  const [sourcesOverview, setSourcesOverview] = useState<SourcesOverview | null>(null);
  const [health, setHealth] = useState<HealthStatus | null>(null);

  const loadMetadata = async () => {
    try {
      const [sourcesData, healthData, convsData] = await Promise.allSettled([
        apiService.getSources(),
        apiService.getHealth(),
        apiService.getConversations(),
      ]);

      if (sourcesData.status === 'fulfilled') {
        setSourcesOverview(sourcesData.value);
      }
      if (healthData.status === 'fulfilled') {
        setHealth(healthData.value);
      }
      if (convsData.status === 'fulfilled' && convsData.value?.conversations) {
        setConversations(convsData.value.conversations);
      }
    } catch (err) {
      console.warn('Metadata fetch warning:', err);
    }
  };

  useEffect(() => {
    loadMetadata();
    const interval = setInterval(loadMetadata, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleNewChat = () => {
    const newId = `session_${Date.now()}`;
    setCurrentSessionId(newId);
    loadMetadata();
  };

  const handleSelectSession = (sessionId: string) => {
    setCurrentSessionId(sessionId);
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#F8FAFC]">
      <Sidebar
        conversations={conversations}
        currentSessionId={currentSessionId}
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
        sourcesOverview={sourcesOverview}
        health={health}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      <main className="flex-1 flex flex-col min-w-0 h-full overflow-hidden">
        <ChatPage
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          currentSessionId={currentSessionId}
          onNewChat={handleNewChat}
        />
      </main>
    </div>
  );
};

export default App;
