import { ChatMessage as ChatMessageType } from '@/types/chat';
import ReactMarkdown from 'react-markdown';
import { User, Bot, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props {
  message: ChatMessageType;
}

export function ChatMessage({ message }: Props) {
  // Define avatar and message styles based on role
  const avatarIcons = {
    user: <User className="h-5 w-5" />,
    assistant: <Bot className="h-5 w-5" />,
    system: <AlertTriangle className="h-5 w-5" />
  };
  
  const avatarColors = {
    user: 'bg-blue-500 text-white',
    assistant: 'bg-emerald-500 text-white',
    system: 'bg-amber-500 text-white'
  };
  
  const messageClasses = {
    user: 'bg-blue-50 dark:bg-blue-900/30 border-blue-100 dark:border-blue-800 ml-auto',
    assistant: 'bg-gray-50 dark:bg-gray-800/50 border-gray-100 dark:border-gray-700',
    system: 'bg-amber-50 dark:bg-amber-900/20 border-amber-100 dark:border-amber-800/50 mx-auto'
  };

  const containerClasses = {
    user: 'justify-end',
    assistant: 'justify-start',
    system: 'justify-center'
  };

  const maxWidth = message.role === 'system' ? 'max-w-2xl' : 'max-w-3xl';

  return (
    <div className={cn("flex items-end gap-3", containerClasses[message.role])}>
      {message.role !== 'user' && (
        <div className={cn("flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center", avatarColors[message.role])}>
          {avatarIcons[message.role]}
        </div>
      )}
      
      <div 
        className={cn(
          "p-4 rounded-2xl border shadow-sm", 
          messageClasses[message.role],
          maxWidth
        )}
      >
        <div className="prose dark:prose-invert prose-sm max-w-none">
          <ReactMarkdown>
            {message.content}
          </ReactMarkdown>
        </div>
      </div>
      
      {message.role === 'user' && (
        <div className={cn("flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center", avatarColors[message.role])}>
          {avatarIcons[message.role]}
        </div>
      )}
    </div>
  );
}