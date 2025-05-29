import { ChatMessage as ChatMessageType } from '@/types/chat';
import ReactMarkdown from 'react-markdown';
import { User, Bot, AlertTriangle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ExtractedReview {
  author?: string;
  rating?: string | number;
  text: string;
  [key: string]: any;
}

interface ReviewAnalysisData {
  overall_sentiment?: string;
  common_themes?: string[];
  frequent_complaints?: string[];
  frequent_praises?: string[];
  rating_patterns?: string;
  representative_reviews?: Array<{
    author: string;
    rating: number | string;
    text: string;
    date: string;
  }>;
  [key: string]: any;
}

interface ReviewMessageData {
  review_analysis?: ReviewAnalysisData;
  extracted_reviews?: ExtractedReview[];
  [key: string]: any;
}

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

  const maxWidth = message.role === 'system' ? 'max-w-2xl' : 'max-w-6xl';

  // Render review analysis data if available
  const renderReviewAnalysis = () => {
    if (!message.data) return null;
    
    const { review_analysis = [], extracted_reviews = [] } = message.data as ReviewMessageData;
    const firstAnalysis = Array.isArray(review_analysis) ? review_analysis[0] : review_analysis;
    
    if (!firstAnalysis) return null;
    
    const {
      overall_sentiment = '',
      common_themes = [],
      frequent_complaints = [],
      frequent_praises = [],
      rating_patterns = '',
      representative_reviews = []
    } = firstAnalysis;
    
    return (
      <div className="mt-4 space-y-6">
        {/* Overall Sentiment */}
        {overall_sentiment && (
          <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h3 className="font-semibold text-sm mb-2">Overall Sentiment</h3>
            <p className="text-sm">{overall_sentiment}</p>
          </div>
        )}
        
        {/* Common Themes */}
        {common_themes.length > 0 && (
          <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
            <h3 className="font-semibold text-sm mb-2">Common Themes</h3>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              {common_themes.map((theme, index) => (
                <li key={index}>{theme}</li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Frequent Complaints */}
        {frequent_complaints.length > 0 && (
          <div className="p-4 bg-red-50 dark:bg-red-900/20 rounded-lg">
            <h3 className="font-semibold text-sm text-red-700 dark:text-red-300 mb-2">
              Frequent Complaints
            </h3>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              {frequent_complaints.map((complaint, index) => (
                <li key={index} className="text-red-700 dark:text-red-300">
                  {complaint}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Frequent Praises */}
        {frequent_praises.length > 0 && (
          <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
            <h3 className="font-semibold text-sm text-green-700 dark:text-green-300 mb-2">
              What Users Like
            </h3>
            <ul className="list-disc pl-5 space-y-1 text-sm">
              {frequent_praises.map((praise, index) => (
                <li key={index} className="text-green-700 dark:text-green-300">
                  {praise}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        {/* Rating Patterns */}
        {rating_patterns && (
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
            <h3 className="font-semibold text-sm text-blue-700 dark:text-blue-300 mb-2">
              Rating Patterns
            </h3>
            <p className="text-sm">{rating_patterns}</p>
          </div>
        )}
        
        {/* Representative Reviews */}
        {representative_reviews.length > 0 && (
          <div className="space-y-4">
            <h3 className="font-semibold text-sm">
              Representative Reviews ({extracted_reviews.length} total)
            </h3>
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
              {representative_reviews.map((review, index) => (
                <div 
                  key={index} 
                  className="p-4 bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-lg"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-sm">
                      {review.author || 'Anonymous'}
                      {review.date && (
                        <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                          {review.date}
                        </span>
                      )}
                    </span>
                    {review.rating && (
                      <span className="text-xs bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100 px-2 py-0.5 rounded">
                        {review.rating} ★
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-700 dark:text-gray-300">
                    {review.text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={cn("flex items-end gap-3", containerClasses[message.role])}>
      {message.role !== 'user' && (
        <div className={cn("flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center", avatarColors[message.role])}>
          {message.isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : avatarIcons[message.role]}
        </div>
      )}
      
      <div 
        className={cn(
          "p-4 rounded-2xl border shadow-sm w-full",
          messageClasses[message.role],
          maxWidth,
          message.isLoading && 'animate-pulse'
        )}
      >
        <div className="prose dark:prose-invert prose-sm max-w-none">
          <ReactMarkdown>
            {message.content}
          </ReactMarkdown>
          {renderReviewAnalysis()}
        </div>
        
        {message.isLoading && (
          <div className="mt-2 text-xs text-gray-500 dark:text-gray-400 flex items-center">
            <Loader2 className="h-3 w-3 mr-1.5 animate-spin" />
            Processing...
          </div>
        )}
      </div>
      
      {message.role === 'user' && (
        <div className={cn("flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center", avatarColors[message.role])}>
          {avatarIcons[message.role]}
        </div>
      )}
    </div>
  );
}