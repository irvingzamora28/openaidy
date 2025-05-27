
import { useState, useEffect } from 'react';
import { ChatMessage as ChatMessageType } from '@/types/chat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';

interface ChatContainerProps {
  messages: ChatMessageType[];
  streamingMessage: ChatMessageType | null;
  isLoading: boolean;
  onSendMessage: (content: string) => void;
  sidebarOpen?: boolean; // Add sidebar state prop
}

export function ChatContainer({ 
  messages, 
  streamingMessage, 
  isLoading, 
  onSendMessage,
  sidebarOpen = false // Default to false if not provided
}: ChatContainerProps) {
  // Track if we're on desktop
  const [isDesktop, setIsDesktop] = useState(false);
  
  // Check window size on mount and when resizing
  useEffect(() => {
    const checkIsDesktop = () => {
      setIsDesktop(window.innerWidth >= 1024);
    };
    
    // Check initially
    checkIsDesktop();
    
    // Add resize listener
    window.addEventListener('resize', checkIsDesktop);
    
    // Clean up
    return () => window.removeEventListener('resize', checkIsDesktop);
  }, []);
  return (
    <div className="flex flex-col h-full">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-6 mb-24 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700 scrollbar-track-transparent">
        {messages.map(message => (
          <ChatMessage key={message.id} message={message} />
        ))}

        {/* Show streaming message if available */}
        {streamingMessage && (
          <ChatMessage key={streamingMessage.id} message={streamingMessage} />
        )}
      </div>

      {/* Input Form - adjusts position based on sidebar state */}
      <div 
        className={`fixed bottom-0 left-0 bg-white/90 dark:bg-gray-800/90 backdrop-blur-md p-6 border-t border-gray-200 dark:border-gray-700 transition-all duration-300 ease-out shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]`}
        style={{
          right: sidebarOpen && isDesktop ? '16rem' : 0
        }}
      >
        <div className="max-w-4xl mx-auto px-4">
          <ChatInput
            onSendMessage={onSendMessage}
            disabled={isLoading}
          />
        </div>
      </div>
    </div>
  );
}
