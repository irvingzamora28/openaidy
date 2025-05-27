import { createContext, useContext, useState, ReactNode } from 'react';

// Define the agent types
export type AgentType = 'chat' | 'app-reviews' | 'product-reviews' | 'youtube-comments';

// Define the possible input field types
export type InputFieldType = 'text' | 'textarea' | 'number' | 'checkbox' | 'radio' | 'select';

// Define a single input field configuration
export interface InputField {
  id: string;
  type: InputFieldType;
  label: string;
  placeholder?: string;
  required?: boolean;
  options?: Array<{ value: string; label: string }>; // For radio, checkbox, select
  defaultValue?: string | number | boolean;
  min?: number; // For number inputs
  max?: number; // For number inputs
}

// Define the agent configuration
export interface AgentConfig {
  type: AgentType;
  label: string;
  description?: string;
  inputs: InputField[];
  endpoint: string;
  disabled?: boolean;
}

// Define the available agents
export const agents: Record<AgentType, AgentConfig> = {
  'chat': {
    type: 'chat',
    label: 'Chat',
    description: 'Chat with the AI assistant',
    inputs: [
      {
        id: 'message',
        type: 'textarea',
        label: 'Message',
        placeholder: 'Type your message...',
        required: true
      }
    ],
    endpoint: '/api/chat'
  },
  'app-reviews': {
    type: 'app-reviews',
    label: 'App Reviews',
    description: 'Analyze app reviews from the Chrome Web Store',
    inputs: [
      {
        id: 'url',
        type: 'text',
        label: 'Chrome Web Store URL',
        placeholder: 'https://chrome.google.com/webstore/detail/...',
        required: true
      }
    ],
    endpoint: '/api/reviews/analyze'
  },
  'product-reviews': {
    type: 'product-reviews',
    label: 'Product Reviews',
    description: 'Analyze product reviews from e-commerce sites',
    inputs: [
      {
        id: 'url',
        type: 'text',
        label: 'Product URL',
        placeholder: 'Enter product page URL...',
        required: true
      },
      {
        id: 'sentiment',
        type: 'radio',
        label: 'Filter by sentiment',
        options: [
          { value: 'all', label: 'All reviews' },
          { value: 'positive', label: 'Positive only' },
          { value: 'negative', label: 'Negative only' }
        ],
        defaultValue: 'all',
        required: false
      },
      {
        id: 'count',
        type: 'number',
        label: 'Number of reviews',
        placeholder: 'How many reviews to analyze',
        min: 5,
        max: 100,
        defaultValue: 20,
        required: false
      }
    ],
    endpoint: '/api/product-reviews/analyze',
    disabled: true
  },
  'youtube-comments': {
    type: 'youtube-comments',
    label: 'YouTube Comments',
    description: 'Analyze comments from YouTube videos',
    inputs: [
      {
        id: 'url',
        type: 'text',
        label: 'Video URL',
        placeholder: 'Enter YouTube video URL...',
        required: true
      },
      {
        id: 'filter',
        type: 'select',
        label: 'Filter comments',
        options: [
          { value: 'top', label: 'Top comments' },
          { value: 'recent', label: 'Most recent' },
          { value: 'all', label: 'All comments' }
        ],
        defaultValue: 'top',
        required: false
      }
    ],
    endpoint: '/api/youtube-comments/analyze',
    disabled: true
  }
};

// Create the context
interface AgentContextType {
  selectedAgent: AgentType;
  setSelectedAgent: (agent: AgentType) => void;
  currentAgentConfig: AgentConfig;
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

// Create a provider component
export function AgentProvider({ children }: { children: ReactNode }) {
  const [selectedAgent, setSelectedAgent] = useState<AgentType>('chat');

  const currentAgentConfig = agents[selectedAgent];

  return (
    <AgentContext.Provider value={{ selectedAgent, setSelectedAgent, currentAgentConfig }}>
      {children}
    </AgentContext.Provider>
  );
}

// Create a hook to use the context
export function useAgent() {
  const context = useContext(AgentContext);
  if (context === undefined) {
    throw new Error('useAgent must be used within an AgentProvider');
  }
  return context;
}
