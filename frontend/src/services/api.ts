import { ChatMessage } from '../types/chat';

/**
 * Interface for chat completion request
 */
interface ChatCompletionRequest {
  messages: {
    role: string;
    content: string;
  }[];
  model?: string;
  temperature?: number;
  max_tokens?: number;
}

/**
 * Interface for chat completion response
 */
interface ChatCompletionResponse {
  role: string;
  content: string;
  model: string;
}

/**
 * API service for interacting with the backend
 */
export const apiService = {
  /**
   * Send a chat completion request to the backend
   * 
   * @param messages Array of chat messages
   * @returns Promise with the assistant's response
   */
  async sendChatCompletion(messages: ChatMessage[]): Promise<ChatMessage> {
    try {
      // Format messages for the API
      const formattedMessages = messages.map(msg => ({
        role: msg.role,
        content: msg.content
      }));
      
      // Create request body
      const requestBody: ChatCompletionRequest = {
        messages: formattedMessages,
        temperature: 0.7
      };
      
      // Send request to backend
      const response = await fetch('/api/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get response from LLM');
      }
      
      // Parse response
      const data: ChatCompletionResponse = await response.json();
      
      // Return formatted message
      return {
        role: data.role,
        content: data.content,
        id: Date.now().toString()
      };
    } catch (error) {
      console.error('Error sending chat completion:', error);
      throw error;
    }
  }
};
