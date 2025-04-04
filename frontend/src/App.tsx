import { useState } from 'react';
import { ChatMessage as ChatMessageType } from './types/chat';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';

function App() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: ChatMessageType = {
      role: 'user',
      content,
      id: Date.now().toString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // TODO: Implement API call
      // For now, just echo the message after a delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const assistantMessage: ChatMessageType = {
        role: 'assistant',
        content: `Echo: ${content}`,
        id: (Date.now() + 1).toString(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessageType = {
        role: 'system',
        content: 'Error processing your request',
        id: (Date.now() + 1).toString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
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
