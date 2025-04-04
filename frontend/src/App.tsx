import { useState } from 'react';
import { ChatMessage as ChatMessageType } from './types/chat';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { apiService } from './services/api';

function App() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<ChatMessageType | null>(null);

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
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-4xl mx-auto p-4">
        {/* Chat Messages */}
        <div className="space-y-4 mb-24">
          {messages.map(message => (
            <ChatMessage key={message.id} message={message} />
          ))}

          {/* Show streaming message if available */}
          {streamingMessage && (
            <ChatMessage key={streamingMessage.id} message={streamingMessage} />
          )}
        </div>

        {/* Input Form */}
        <div className="fixed bottom-0 left-0 right-0 bg-white p-4">
          <div className="max-w-4xl mx-auto">
            <ChatInput
              onSendMessage={handleSendMessage}
              disabled={isLoading}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
