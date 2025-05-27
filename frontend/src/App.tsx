import { useState } from 'react';
import { ChatMessage as ChatMessageType } from './types/chat';
import { apiService } from './services/api';
import { Layout } from './components/Layout';
import { ChatContainer } from './components/ChatContainer';
import { AgentProvider, useAgent } from './contexts/AgentContext';

function AppContent() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<ChatMessageType | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false); // Add sidebar state
  const { selectedAgent, currentAgentConfig } = useAgent();

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
      // Handle different agent types
      if (selectedAgent === 'chat') {
        // Regular chat flow
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
      } else if (selectedAgent === 'app-reviews') {
        // App reviews analysis flow
        try {
          // Parse the content if it's JSON (for complex inputs)
          let requestData: any;
          try {
            requestData = JSON.parse(content);
          } catch {
            // For simple agents with a single input
            requestData = { url: content };
          }
          
          // Create a processing message
          const processingMessage: ChatMessageType = {
            role: 'system',
            content: `Analyzing reviews from: ${requestData.url}\n\nThis may take a minute...`,
            id: `processing-${Date.now()}`,
          };
          setMessages(prev => [...prev, processingMessage]);
          
          // Call the reviews analysis API
          const response = await fetch(currentAgentConfig.endpoint, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData),
          });
          
          if (!response.ok) {
            throw new Error(`Error: ${response.status} ${response.statusText}`);
          }
          
          const data = await response.json();
          
          // Create a result message
          const resultMessage: ChatMessageType = {
            role: 'assistant',
            content: `## Review Analysis Results\n\n${JSON.stringify(data.review_analysis, null, 2)}`,
            id: Date.now().toString(),
          };
          
          // Remove the processing message and add the result
          setMessages(prev => prev.filter(msg => msg.id !== processingMessage.id).concat(resultMessage));
          setIsLoading(false);
        } catch (error) {
          const errorMessage: ChatMessageType = {
            role: 'system',
            content: `Error analyzing reviews: ${error instanceof Error ? error.message : 'Unknown error'}`,
            id: Date.now().toString(),
          };
          setMessages(prev => [...prev, errorMessage]);
          setIsLoading(false);
        }
      } else if (currentAgentConfig.disabled) {
        // Handle disabled agents
        const errorMessage: ChatMessageType = {
          role: 'system',
          content: `The ${currentAgentConfig.label} agent is coming soon. Please try another agent.`,
          id: Date.now().toString(),
        };
        setMessages(prev => [...prev, errorMessage]);
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

function App() {
  return (
    <AgentProvider>
      <AppContent />
    </AgentProvider>
  );
}

export default App;
