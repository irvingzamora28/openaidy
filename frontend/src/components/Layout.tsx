import * as React from 'react';
import { useState, useEffect } from 'react';
import { DarkModeToggle } from './DarkModeToggle';
// Removed unused imports
import { Menu, Home, Settings, User } from 'lucide-react';
import { cn } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
  sidebarOpen?: boolean;
  setSidebarOpen?: (open: boolean) => void;
}

// Define sidebar navigation items in one place
const sidebarItems = [
  { icon: Home, label: 'Dashboard' },
  { icon: Settings, label: 'Settings' },
  { icon: User, label: 'Profile' }
];

// Sidebar content component to reuse in both desktop and mobile
const SidebarContent = () => (
  <>
    <div className="flex-1">
      <nav className="space-y-2">
        {sidebarItems.map((item, index) => (
          <div 
            key={index} 
            className="flex items-center gap-2 p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 cursor-pointer"
          >
            <item.icon className="h-5 w-5" />
            <span>{item.label}</span>
          </div>
        ))}
      </nav>
    </div>
    <div className="mt-auto pt-4 border-t border-gray-200 dark:border-gray-700">
      <DarkModeToggle />
    </div>
  </>
);

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
      <header className="fixed top-0 left-0 right-0 z-30 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 h-16 flex items-center px-4">
        <div className="flex items-center justify-between w-full max-w-7xl mx-auto">
          <h1 className="text-xl font-bold text-gray-800 dark:text-white">OpenAIDY Chat</h1>
          
          {/* Sidebar toggle button - on the right side */}
          <div className="flex items-center gap-4">
            <button
              className="p-2 rounded-md hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
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
          "fixed z-20 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 transition-transform duration-300 ease-out will-change-transform",
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
              className="p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
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
          "fixed z-20 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 transition-transform duration-300 ease-out will-change-transform",
          "top-16 bottom-0 right-0 w-64",
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
