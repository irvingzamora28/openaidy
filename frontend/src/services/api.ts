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
 * Interface for streaming chat completion chunk
 */
interface ChatCompletionChunk {
  role: string;
  content: string;
  content_delta: string;
  model: string;
  finished: boolean;
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
        role: data.role as 'assistant',
        content: data.content,
        id: Date.now().toString()
      };
    } catch (error) {
      console.error('Error sending chat completion:', error);
      throw error;
    }
  },

  /**
   * Analyze reviews from a URL with progress updates via Server-Sent Events
   * 
   * @param url The URL to analyze reviews from
   * @param onProgress Callback for progress updates
   * @param onComplete Callback when analysis is complete
   * @param onError Callback for errors
   */
  analyzeReviews(
    url: string,
    onProgress: (message: string) => void,
    onComplete: (result: any) => void,
    onError: (error: Error) => void
  ): () => void {
    // Create an AbortController to allow cancelling the fetch request
    const controller = new AbortController();
    let eventSource: EventSource | null = null;
    
    // Start the request
    (async () => {
      try {
        // First, make a POST request to start the analysis
        const response = await fetch('/api/reviews/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ url }),
          signal: controller.signal
        });
        
        if (!response.ok || !response.body) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Create a new EventSource for the SSE stream
        // The server should return a URL to connect to for SSE
        const data = await response.json();
        if (!data.stream_url) {
          throw new Error('No stream URL returned from server');
        }
        
        eventSource = new EventSource(data.stream_url);
        
        eventSource.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            switch (data.event) {
              case 'progress':
                onProgress(data.data);
                break;
                
              case 'complete':
                onComplete(data.data);
                eventSource?.close();
                break;
                
              case 'error':
                eventSource?.close();
                onError(new Error(data.data));
                break;
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e);
            eventSource?.close();
            onError(e instanceof Error ? e : new Error(String(e)));
          }
        };
        
        eventSource.onerror = (error) => {
          console.error('SSE error:', error);
          eventSource?.close();
          onError(new Error('Failed to connect to the server'));
        };
        
      } catch (error) {
        onError(error instanceof Error ? error : new Error(String(error)));
      }
    })();
    
    // Return a cleanup function
    return () => {
      controller.abort();
      eventSource?.close();
    };
  },

  /**
   * Send a streaming chat completion request to the backend
   *
   * @param messages Array of chat messages
   * @param onChunk Callback function to handle each chunk of the response
   * @param onComplete Callback function called when streaming is complete
   * @param onError Callback function to handle errors
   */
  async sendChatCompletionStream(
    messages: ChatMessage[],
    onChunk: (content: string, delta: string) => void,
    onComplete: (message: ChatMessage) => void,
    onError: (error: Error) => void
  ): Promise<void> {
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
      const response = await fetch('/api/chat/completions/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to get streaming response from LLM');
      }

      // Create a reader for the stream
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Failed to create stream reader');
      }

      // Read the stream
      const decoder = new TextDecoder();
      let lastChunk: ChatCompletionChunk | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        // Decode the chunk
        const chunk = decoder.decode(value, { stream: true });

        // Process each SSE message
        const messages = chunk
          .split('\n\n')
          .filter(msg => msg.startsWith('data: '))
          .map(msg => msg.replace('data: ', ''));

        for (const msg of messages) {
          try {
            // Parse the JSON data
            const data = JSON.parse(msg) as ChatCompletionChunk;

            // Call the onChunk callback
            onChunk(data.content, data.content_delta);

            // Store the last chunk for completion
            lastChunk = data;

            // If this is the final chunk, call onComplete
            if (data.finished) {
              onComplete({
                role: 'assistant',
                content: data.content,
                id: Date.now().toString()
              });
              return;
            }
          } catch (e) {
            console.error('Error parsing SSE message:', e);
            // Check if it's an error message
            try {
              const errorData = JSON.parse(msg);
              if (errorData.error) {
                throw new Error(errorData.error);
              }
            } catch (parseError) {
              // Ignore parsing errors for non-JSON messages
            }
          }
        }
      }

      // If we got here without a lastChunk, something went wrong
      if (!lastChunk) {
        throw new Error('No response received from streaming API');
      }

      // Call onComplete with the last chunk
      onComplete({
        role: 'assistant',
        content: lastChunk.content,
        id: Date.now().toString()
      });
    } catch (error) {
      console.error('Error in streaming chat completion:', error);
      onError(error instanceof Error ? error : new Error(String(error)));
    }
  }
};
