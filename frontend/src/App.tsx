import { useState, useEffect } from 'react';
import { ChatMessage as ChatMessageType } from './types/chat';
import { apiService } from './services/api';
import { Layout } from './components/Layout';
import { ChatContainer } from './components/ChatContainer';
import { AgentProvider, useAgent } from './contexts/AgentContext';
import toast from 'react-hot-toast';

function AppContent() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [streamingMessage, setStreamingMessage] = useState<ChatMessageType | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { selectedAgent, currentAgentConfig } = useAgent();
  
  // Cleanup function for review analysis
  useEffect(() => {
    return () => {
      // Any cleanup if needed
    };
  }, []);

  const useStreaming = true;

  const handleSendMessage = async (content: string, inputValues?: Record<string, any>) => {
    // If this is a review analysis request
    if (selectedAgent === 'app-reviews' && inputValues?.url) {
      try {
        setIsProcessing(true);
        
        // Add user message
        const userMessage: ChatMessageType = {
          id: Date.now().toString(),
          role: 'user',
          content: `Analyzing reviews from: ${inputValues.url}`,
        };
        
        setMessages(prev => [...prev, userMessage]);
        
        // Add a loading message
        const loadingMessage: ChatMessageType = {
          id: 'loading',
          role: 'assistant',
          content: 'Starting review analysis...',
          isLoading: true
        };
        
        setMessages(prev => [...prev, loadingMessage]);
        
        // Start the review analysis
        const cleanup = apiService.analyzeReviews(
          inputValues.url,
          // Progress callback
          (progress: string) => {
            setMessages(prev => 
              prev.map(msg => 
                msg.id === 'loading' 
                  ? { ...msg, content: progress }
                  : msg
              )
            );
          },
          // Complete callback
          (result: any) => {
            console.log('Review analysis result:', result);
            
            // Extract the review analysis from the results
            const reviewAnalysis = result.results?.review_analysis || [];
            const extractedReviews = result.results?.extracted_reviews || [];
            
            // Create a summary message
            const summary = `Analysis complete! Processed ${extractedReviews.length} reviews.`;
            
            setMessages(prev => [
              ...prev.filter(msg => msg.id !== 'loading'),
              {
                id: Date.now().toString(),
                role: 'assistant',
                content: summary,
                data: {
                  ...result.results,
                  review_analysis: reviewAnalysis,
                  extracted_reviews: extractedReviews
                }
              }
            ]);
            setIsProcessing(false);
          },
          // Error callback
          (error: Error) => {
            console.error('Review analysis error:', error);
            setMessages(prev => [
              ...prev.filter(msg => msg.id !== 'loading'),
              {
                id: Date.now().toString(),
                role: 'assistant',
                content: `Error analyzing reviews: ${error.message}`
              }
            ]);
            setIsProcessing(false);
            toast.error('Failed to analyze reviews');
          }
        );
        
        // Return cleanup function
        return () => {
          if (cleanup) cleanup();
        };
        
      } catch (error) {
        console.error('Error starting review analysis:', error);
        toast.error('Failed to start review analysis');
        setIsProcessing(false);
      }
      return;
    }
    
    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      content,
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    setStreamingMessage(null);

    try {
      if (selectedAgent === 'chat') {
        const allMessages = [...messages, userMessage];

        if (useStreaming) {
          const initialStreamingMessage: ChatMessageType = {
            role: 'assistant',
            content: '',
            id: `streaming-${Date.now()}`,
          };
          setStreamingMessage(initialStreamingMessage);

          await apiService.sendChatCompletionStream(
            allMessages,
            (content, _delta) => {
              setStreamingMessage(prev => {
                if (!prev) return null;
                return { ...prev, content };
              });
            },
            (assistantMessage) => {
              setStreamingMessage(null);
              setMessages(prev => [...prev, assistantMessage]);
              setIsLoading(false);
            },
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
          const assistantMessage = await apiService.sendChatCompletion(allMessages);
          setMessages(prev => [...prev, assistantMessage]);
          setIsLoading(false);
        }
      } else if (selectedAgent === 'app-reviews') {
        // This block is a fallback and should not be reached since we handle app-reviews at the beginning
        // of the function. We'll keep it as a safety net but log a warning.
        console.warn('Unexpected code path: app-reviews agent should be handled by the initial check');
        const errorMessage: ChatMessageType = {
          role: 'system',
          content: 'Please provide a valid URL to analyze reviews.',
          id: Date.now().toString(),
        };
        setMessages(prev => [...prev, errorMessage]);
        setIsLoading(false);
      } else if (currentAgentConfig.disabled) {
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
      <div className="max-w-6xl mx-auto p-4 h-full">
        <ChatContainer 
          messages={messages}
          streamingMessage={streamingMessage}
          isLoading={isLoading || isProcessing}
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
