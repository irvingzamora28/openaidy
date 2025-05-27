import { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { useAgent, InputField } from '@/contexts/AgentContext';

interface Props {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, disabled }: Props) {
  // For simple agents with a single input, we'll use a string
  // For complex agents with multiple inputs, we'll use an object
  const [inputValues, setInputValues] = useState<Record<string, string | number | boolean>>({});
  const mainInputRef = useRef<HTMLTextAreaElement | HTMLInputElement>(null);
  const { currentAgentConfig } = useAgent();

  // Reset input values when agent changes
  useEffect(() => {
    const initialValues: Record<string, string | number | boolean> = {};
    
    // Set default values from config
    currentAgentConfig.inputs.forEach(input => {
      if (input.defaultValue !== undefined) {
        initialValues[input.id] = input.defaultValue;
      } else {
        initialValues[input.id] = input.type === 'checkbox' ? false : '';
      }
    });
    
    setInputValues(initialValues);
    
    // Focus the first input when agent changes
    setTimeout(() => {
      mainInputRef.current?.focus();
    }, 0);
  }, [currentAgentConfig.type]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (disabled) return;
    
    // Check if required fields are filled
    const requiredFieldsFilled = currentAgentConfig.inputs
      .filter(input => input.required)
      .every(input => {
        const value = inputValues[input.id];
        return typeof value === 'string' ? value.trim() !== '' : value !== undefined;
      });
    
    if (!requiredFieldsFilled) return;
    
    // For simple agents with a single text/textarea input
    if (currentAgentConfig.inputs.length === 1 && 
        (currentAgentConfig.inputs[0].type === 'text' || currentAgentConfig.inputs[0].type === 'textarea')) {
      const inputId = currentAgentConfig.inputs[0].id;
      const value = inputValues[inputId] as string;
      if (value.trim()) {
        onSendMessage(value.trim());
        
        // Reset the input value
        setInputValues(prev => ({
          ...prev,
          [inputId]: ''
        }));
        
        // Reset height for textarea
        if (mainInputRef.current && currentAgentConfig.inputs[0].type === 'textarea') {
          (mainInputRef.current as HTMLTextAreaElement).style.height = 'auto';
        }
      }
    } else {
      // For complex agents with multiple inputs, send the entire input values object as JSON
      onSendMessage(JSON.stringify(inputValues));
      
      // Reset input values to defaults
      const resetValues: Record<string, string | number | boolean> = {};
      currentAgentConfig.inputs.forEach(input => {
        if (input.defaultValue !== undefined) {
          resetValues[input.id] = input.defaultValue;
        } else {
          resetValues[input.id] = input.type === 'checkbox' ? false : '';
        }
      });
      setInputValues(resetValues);
    }
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>, inputId: string) => {
    setInputValues(prev => ({
      ...prev,
      [inputId]: e.target.value
    }));
    
    // Auto-resize logic for textarea
    const textarea = e.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>, inputId: string, type: string) => {
    let value: string | number | boolean = e.target.value;
    
    // Convert value based on input type
    if (type === 'number') {
      value = e.target.value === '' ? '' : Number(e.target.value);
    } else if (type === 'checkbox') {
      value = e.target.checked;
    }
    
    setInputValues(prev => ({
      ...prev,
      [inputId]: value
    }));
  };

  const handleSelectChange = (e: React.ChangeEvent<HTMLSelectElement>, inputId: string) => {
    setInputValues(prev => ({
      ...prev,
      [inputId]: e.target.value
    }));
  };

  // Handle Ctrl+Enter or Command+Enter to submit
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      handleSubmit(e);
    }
  };

  // Render a single input field based on its type
  const renderInputField = (input: InputField, index: number) => {
    const isMainInput = index === 0;
    const value = inputValues[input.id] !== undefined ? inputValues[input.id] : '';
    
    switch (input.type) {
      case 'textarea':
        return (
          <div key={input.id} className="w-full">
            {input.label && index > 0 && (
              <label htmlFor={input.id} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {input.label}{input.required && <span className="text-red-500 ml-1">*</span>}
              </label>
            )}
            <div className={`relative ${isMainInput ? 'flex items-end' : ''}`}>
              <textarea
                id={input.id}
                ref={isMainInput ? mainInputRef as React.RefObject<HTMLTextAreaElement> : undefined}
                value={value as string}
                onChange={(e) => handleTextareaChange(e, input.id)}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                className={`w-full p-4 ${isMainInput ? 'pr-12' : ''} max-h-[120px] rounded-2xl resize-none focus:outline-none bg-transparent text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 border border-gray-200 dark:border-gray-600 focus:border-blue-400 dark:focus:border-blue-500`}
                placeholder={input.placeholder}
                rows={1}
                required={input.required}
              />
              {isMainInput && (
                <div className="absolute right-3 bottom-3 flex items-center">
                  {!value && (
                    <div className="mr-2 text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      <kbd className="px-1 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-mono text-xs">Ctrl</kbd>+<kbd className="px-1 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-mono text-xs">Enter</kbd>
                    </div>
                  )}
                  <button
                    type="submit"
                    disabled={disabled || !canSubmit()}
                    className="p-2 rounded-full bg-blue-500 dark:bg-blue-600 text-white hover:bg-blue-600 dark:hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:hover:bg-blue-500 dark:disabled:hover:bg-blue-600"
                    aria-label="Send message"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        );
      case 'text':
        return (
          <div key={input.id} className="w-full">
            {input.label && index > 0 && (
              <label htmlFor={input.id} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {input.label}{input.required && <span className="text-red-500 ml-1">*</span>}
              </label>
            )}
            <div className={`relative ${isMainInput ? 'flex items-end' : ''}`}>
              <input
                id={input.id}
                ref={isMainInput ? mainInputRef as React.RefObject<HTMLInputElement> : undefined}
                type="text"
                value={value as string}
                onChange={(e) => handleInputChange(e, input.id, 'text')}
                onKeyDown={handleKeyDown}
                disabled={disabled}
                className={`w-full p-4 ${isMainInput ? 'pr-12' : ''} h-[52px] rounded-2xl focus:outline-none bg-transparent text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 border border-gray-200 dark:border-gray-600 focus:border-blue-400 dark:focus:border-blue-500`}
                placeholder={input.placeholder}
                required={input.required}
              />
              {isMainInput && (
                <div className="absolute right-3 bottom-3 flex items-center">
                  {!value && (
                    <div className="mr-2 text-xs text-gray-500 dark:text-gray-400 whitespace-nowrap">
                      <kbd className="px-1 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-mono text-xs">Ctrl</kbd>+<kbd className="px-1 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 font-mono text-xs">Enter</kbd>
                    </div>
                  )}
                  <button
                    type="submit"
                    disabled={disabled || !canSubmit()}
                    className="p-2 rounded-full bg-blue-500 dark:bg-blue-600 text-white hover:bg-blue-600 dark:hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:hover:bg-blue-500 dark:disabled:hover:bg-blue-600"
                    aria-label="Send message"
                  >
                    <Send className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        );
      case 'number':
        return (
          <div key={input.id} className="w-full mt-3">
            <label htmlFor={input.id} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {input.label}{input.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <input
              id={input.id}
              type="number"
              value={value as number | string}
              onChange={(e) => handleInputChange(e, input.id, 'number')}
              disabled={disabled}
              className="w-full p-3 h-[42px] rounded-lg focus:outline-none bg-transparent text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 border border-gray-200 dark:border-gray-600 focus:border-blue-400 dark:focus:border-blue-500"
              placeholder={input.placeholder}
              min={input.min}
              max={input.max}
              required={input.required}
            />
          </div>
        );
      case 'checkbox':
        return (
          <div key={input.id} className="w-full mt-3 flex items-center">
            <input
              id={input.id}
              type="checkbox"
              checked={Boolean(value)}
              onChange={(e) => handleInputChange(e, input.id, 'checkbox')}
              disabled={disabled}
              className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              required={input.required}
            />
            <label htmlFor={input.id} className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
              {input.label}{input.required && <span className="text-red-500 ml-1">*</span>}
            </label>
          </div>
        );
      case 'radio':
        return (
          <div key={input.id} className="w-full mt-3">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {input.label}{input.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <div className="space-y-2">
              {input.options?.map((option) => (
                <div key={option.value} className="flex items-center">
                  <input
                    id={`${input.id}-${option.value}`}
                    type="radio"
                    name={input.id}
                    value={option.value}
                    checked={value === option.value}
                    onChange={(e) => handleInputChange(e, input.id, 'radio')}
                    disabled={disabled}
                    className="h-4 w-4 border-gray-300 text-blue-600 focus:ring-blue-500"
                    required={input.required}
                  />
                  <label htmlFor={`${input.id}-${option.value}`} className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                    {option.label}
                  </label>
                </div>
              ))}
            </div>
          </div>
        );
      case 'select':
        return (
          <div key={input.id} className="w-full mt-3">
            <label htmlFor={input.id} className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {input.label}{input.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            <select
              id={input.id}
              value={value as string}
              onChange={(e) => handleSelectChange(e, input.id)}
              disabled={disabled}
              className="w-full p-3 h-[42px] rounded-lg focus:outline-none bg-transparent text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-600 focus:border-blue-400 dark:focus:border-blue-500"
              required={input.required}
            >
              {input.options?.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        );
      default:
        return null;
    }
  };

  // Check if the form can be submitted
  const canSubmit = () => {
    return currentAgentConfig.inputs
      .filter(input => input.required)
      .every(input => {
        const value = inputValues[input.id];
        return typeof value === 'string' ? value.trim() !== '' : value !== undefined;
      });
  };

  // For simple agents with a single input, use the original layout
  // For complex agents with multiple inputs, use a more form-like layout
  const isSimpleAgent = currentAgentConfig.inputs.length === 1 && 
    (currentAgentConfig.inputs[0].type === 'text' || currentAgentConfig.inputs[0].type === 'textarea');

  return (
    <form onSubmit={handleSubmit} className="relative">
      {isSimpleAgent ? (
        // Simple agent with a single input
        <div className="relative flex items-end rounded-2xl bg-white/50 dark:bg-gray-700/50 backdrop-blur-sm border border-gray-200 dark:border-gray-600 focus-within:border-blue-400 dark:focus-within:border-blue-500 transition-all shadow-sm hover:shadow-md">
          {renderInputField(currentAgentConfig.inputs[0], 0)}
        </div>
      ) : (
        // Complex agent with multiple inputs
        <div className="rounded-2xl bg-white/50 dark:bg-gray-700/50 backdrop-blur-sm border border-gray-200 dark:border-gray-600 p-4 transition-all shadow-sm hover:shadow-md space-y-3">
          <div className="mb-3 font-medium text-gray-900 dark:text-gray-100">
            {currentAgentConfig.label}
            {currentAgentConfig.description && (
              <p className="mt-1 text-sm font-normal text-gray-500 dark:text-gray-400">{currentAgentConfig.description}</p>
            )}
          </div>
          {currentAgentConfig.inputs.map((input, index) => renderInputField(input, index))}
          {!currentAgentConfig.inputs.some(input => input.type === 'textarea' || input.type === 'text') && (
            <div className="flex justify-end mt-4">
              <button
                type="submit"
                disabled={disabled || !canSubmit()}
                className="px-4 py-2 rounded-lg bg-blue-500 dark:bg-blue-600 text-white hover:bg-blue-600 dark:hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:hover:bg-blue-500 dark:disabled:hover:bg-blue-600 flex items-center gap-2"
              >
                <Send className="h-4 w-4" />
                Submit
              </button>
            </div>
          )}
        </div>
      )}
      {currentAgentConfig.type !== 'chat' && (
        <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          <span className="font-medium">{currentAgentConfig.label}</span> agent selected. {currentAgentConfig.disabled ? 'This agent is coming soon.' : ''}
        </div>
      )}
    </form>
  );
}