import { ChatMessage as ChatMessageType } from '../types/chat';
import ReactMarkdown from 'react-markdown';

interface Props {
  message: ChatMessageType;
}

export function ChatMessage({ message }: Props) {
  const messageClasses = {
    user: 'bg-blue-100 dark:bg-blue-900 ml-12 text-gray-800 dark:text-gray-100',
    assistant: 'bg-gray-100 dark:bg-gray-800 mr-12 text-gray-800 dark:text-gray-100',
    system: 'bg-red-100 dark:bg-red-900 text-gray-800 dark:text-gray-100',
  };

  return (
    <div className={`p-4 rounded-lg ${messageClasses[message.role]}`}>
      <ReactMarkdown>
        {message.content}
      </ReactMarkdown>
    </div>
  );
}