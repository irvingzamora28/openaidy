import { ChatMessage as ChatMessageType } from '../types/chat';

interface Props {
  message: ChatMessageType;
}

export function ChatMessage({ message }: Props) {
  const messageClasses = {
    user: 'bg-blue-100 ml-12',
    assistant: 'bg-gray-100 mr-12',
    system: 'bg-red-100',
  };

  return (
    <div className={`p-4 rounded-lg ${messageClasses[message.role]}`}>
      {message.content}
    </div>
  );
}