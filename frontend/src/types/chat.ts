export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  role: MessageRole;
  content: string;
  id: string;
  timestamp?: string;
  isLoading?: boolean;
  data?: any; // For any additional data that needs to be attached to the message
}