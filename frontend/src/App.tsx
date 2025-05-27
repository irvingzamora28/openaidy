import { useState } from 'react';
import { ChatMessage as ChatMessageType } from './types/chat';
import { apiService } from './services/api';
import { Layout } from './components/Layout';
import { ChatContainer } from './components/ChatContainer';

function App() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<ChatMessageType | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false); // Add sidebar state

  // Use streaming by default
  const useStreaming = true;

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: ChatMessageType = {
      role: 'user',
      content,
      id: Date.now().toString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // Reset streaming message
    setStreamingMessage(null);

    try {
      // Get all messages to maintain conversation context
      const allMessages = [...messages, userMessage];

      if (useStreaming) {
        // Create an initial streaming message
        const initialStreamingMessage: ChatMessageType = {
          role: 'assistant',
          content: '',
          id: `streaming-${Date.now()}`,
        };
        setStreamingMessage(initialStreamingMessage);

        // Use streaming API
        await apiService.sendChatCompletionStream(
          allMessages,
          // Handle each chunk
          (content, _delta) => {
            setStreamingMessage(prev => {
              if (!prev) return null;
              return { ...prev, content };
            });
          },
          // Handle completion
          (assistantMessage) => {
            setStreamingMessage(null);
            setMessages(prev => [...prev, assistantMessage]);
            setIsLoading(false);
          },
          // Handle errors
          (error) => {
            setStreamingMessage(null);
            const errorMessage: ChatMessageType = {
              role: 'system',
              content: error.message || 'Error processing your request',
              id: (Date.now() + 1).toString(),
            };
            setMessages(prev => [...prev, errorMessage]);
            setIsLoading(false);
          }
        );
      } else {
        // Use non-streaming API
        const assistantMessage = await apiService.sendChatCompletion(allMessages);
        setMessages(prev => [...prev, assistantMessage]);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error in chat:', error);
      const errorMessage: ChatMessageType = {
        role: 'system',
        content: error instanceof Error ? error.message : 'Error processing your request',
        id: (Date.now() + 1).toString(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  return (
    <Layout sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen}>
      <div className="max-w-4xl mx-auto p-4 h-full">
        <ChatContainer
          messages={messages}
          streamingMessage={streamingMessage}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          sidebarOpen={sidebarOpen}
        />
      </div>
    </Layout>
  );
}

export default App;
