import * as React from 'react';
import { useState, useEffect } from 'react';
import { DarkModeToggle } from './DarkModeToggle';
// Removed unused imports
import { Menu, Home, Settings, User, ChevronDown, ChevronRight, Star } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAgent, AgentType } from '@/contexts/AgentContext';

interface LayoutProps {
  children: React.ReactNode;
  sidebarOpen?: boolean;
  setSidebarOpen?: (open: boolean) => void;
}

// Define sidebar navigation items in one place
const sidebarItems = [
  { icon: Home, label: 'Dashboard', path: '/' },
  { 
    icon: Star, 
    label: 'Review Agents', 
    children: [
      { icon: Star, label: 'App Reviews', path: '/reviews/app', disabled: false },
    ] 
  },
  { icon: Settings, label: 'Settings', path: '/settings' },
  { icon: User, label: 'Profile', path: '/profile' }
];

// Sidebar content component to reuse in both desktop and mobile
const SidebarContent = () => {
  const [expandedItems, setExpandedItems] = useState<Record<string, boolean>>({
    'Review Agents': true // Start with Review Agents expanded
  });
  const { selectedAgent, setSelectedAgent } = useAgent();
  
  const toggleExpand = (label: string) => {
    setExpandedItems(prev => ({
      ...prev,
      [label]: !prev[label]
    }));
  };

  const handleAgentSelect = (agentType: AgentType) => {
    setSelectedAgent(agentType);
  };
  
  return (
    <>
      <div className="flex-1">
        <nav className="space-y-1">
          {sidebarItems.map((item, index) => (
            <div key={index}>
              <div 
                className={`flex items-center justify-between p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 cursor-pointer ${item.children ? '' : 'pl-3'}`}
                onClick={() => {
                  if (item.children) {
                    toggleExpand(item.label);
                  } else if (item.path === '/') {
                    handleAgentSelect('chat');
                  }
                }}
              >
                <div className="flex items-center gap-2">
                  <item.icon className="h-5 w-5" />
                  <span className={item.children ? 'font-medium' : ''}>{item.label}</span>
                </div>
                {item.children && (
                  expandedItems[item.label] ? 
                    <ChevronDown className="h-4 w-4" /> : 
                    <ChevronRight className="h-4 w-4" />
                )}
              </div>
              
              {/* Render children if expanded */}
              {item.children && expandedItems[item.label] && (
                <div className="ml-4 pl-2 border-l border-gray-200 dark:border-gray-700 mt-1 space-y-1">
                  {item.children.map((child, childIndex) => (
                    <div 
                      key={childIndex} 
                      className={`flex items-center gap-2 p-2 rounded ${child.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-200 dark:hover:bg-gray-700 cursor-pointer'} ${
                        selectedAgent === (child.path === '/reviews/app' ? 'app-reviews' : 
                                          child.path === '/reviews/product' ? 'product-reviews' : 
                                          child.path === '/reviews/youtube' ? 'youtube-comments' : '') ? 
                        'bg-blue-100 dark:bg-blue-900/20' : ''
                      }`}
                      onClick={() => {
                        if (!child.disabled) {
                          if (child.path === '/reviews/app') handleAgentSelect('app-reviews');
                          else if (child.path === '/reviews/product') handleAgentSelect('product-reviews');
                          else if (child.path === '/reviews/youtube') handleAgentSelect('youtube-comments');
                        }
                      }}
                    >
                      <child.icon className="h-4 w-4" />
                      <span>{child.label}</span>
                      {child.disabled && (
                        <span className="text-xs bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded text-gray-500 dark:text-gray-400 ml-1">Soon</span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>
      </div>
      <div className="mt-auto pt-4 border-t border-gray-200 dark:border-gray-700">
        <DarkModeToggle />
      </div>
    </>
  );
};

export function Layout({ children, sidebarOpen: propSidebarOpen, setSidebarOpen: propSetSidebarOpen }: LayoutProps) {
  // Use props if provided, otherwise use local state
  const [localSidebarOpen, setLocalSidebarOpen] = useState(false);
  
  // Use the prop values if provided, otherwise use local state
  const sidebarOpen = propSidebarOpen !== undefined ? propSidebarOpen : localSidebarOpen;
  const setSidebarOpen = propSetSidebarOpen || setLocalSidebarOpen;
  
  // Close sidebar on window resize
  useEffect(() => {
    const handleResize = () => {
      if (sidebarOpen) {
        setSidebarOpen(false);
      }
    };
    
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [sidebarOpen]);
  
  // Toggle sidebar
  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-200">
      {/* Header with app name and toggle button */}
      <header className="fixed top-0 left-0 right-0 z-30 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 h-16 flex items-center px-4 shadow-sm">
        <div className="flex items-center justify-between w-full max-w-7xl mx-auto">
          <h1 className="text-xl font-bold text-gray-800 dark:text-white">OpenAIDY Chat</h1>
          
          {/* Sidebar toggle button - on the right side */}
          <div className="flex items-center gap-4">
            <button
              className="p-2 rounded-full hover:bg-gray-100/80 dark:hover:bg-gray-700/80 transition-colors"
              onClick={toggleSidebar}
              aria-expanded={sidebarOpen}
            >
              <Menu className="h-5 w-5" />
              <span className="sr-only">Toggle sidebar</span>
            </button>
          </div>
        </div>
      </header>

      {/* Mobile Sidebar - slides from right on small screens */}
      <div 
        className={cn(
          // Base styles for mobile
          "fixed z-20 bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border-l border-gray-200 dark:border-gray-700 transition-transform duration-300 ease-out will-change-transform shadow-xl",
          "top-0 bottom-0 right-0 w-[85%] md:w-80",
          // Transform for mobile
          sidebarOpen ? "translate-x-0" : "translate-x-full",
          // Hide on desktop
          "lg:hidden"
        )}
      >
        {/* Mobile sidebar content */}
        <div className="flex flex-col h-full">
          {/* Close button */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
            <button 
              onClick={() => setSidebarOpen(false)}
              className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
              </svg>
              <span className="sr-only">Close sidebar</span>
            </button>
            <h2 className="text-xl font-bold text-gray-800 dark:text-white">OpenAIDY Chat</h2>
          </div>
          
          {/* Sidebar content */}
          <div className="flex flex-col h-full p-4">
            <SidebarContent />
          </div>
        </div>
      </div>
      
      {/* Desktop Sidebar - slides from right on large screens */}
      <div 
        className={cn(
          // Base styles for desktop
          "fixed z-20 bg-white/95 dark:bg-gray-800/95 backdrop-blur-md border-l border-gray-200 dark:border-gray-700 transition-transform duration-300 ease-out will-change-transform shadow-lg",
          "top-16 bottom-0 right-0 w-64 rounded-tl-xl",
          // Transform for desktop
          sidebarOpen ? "translate-x-0" : "translate-x-full",
          // Only show on desktop
          "hidden lg:block"
        )}
      >
        {/* Sidebar content for desktop */}
        <div className="flex flex-col h-full p-4">
          <SidebarContent />
        </div>
      </div>

      {/* Backdrop for mobile - only visible when sidebar is open on mobile */}
      <div 
        className={cn(
          "fixed inset-0 bg-black/50 z-10 lg:hidden transition-opacity duration-300",
          sidebarOpen ? "opacity-100" : "opacity-0 pointer-events-none"
        )}
        onClick={() => setSidebarOpen(false)}
        aria-hidden="true"
      />

      {/* Main content - adjusts width when sidebar is open */}
      <main className="pt-16 min-h-screen transition-all duration-300 ease-out">
        <div className={cn(
          "w-full transition-all duration-300 ease-out",
          sidebarOpen ? "lg:pr-64" : ""
        )}>
          {children}
        </div>
      </main>
    </div>
  );
}
