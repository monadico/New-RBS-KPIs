'use client'

import { useEffect } from 'react'

export function ChunkErrorHandler() {
  useEffect(() => {
    // Handle unhandled promise rejections (chunk errors)
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      if (event.reason?.name === 'ChunkLoadError') {
        console.warn('Chunk load error caught:', event.reason);
        event.preventDefault(); // Prevent default error handling
        
        // Show user-friendly message
        console.log('A loading error occurred. The page will refresh automatically...');
        
        // Reload page after a short delay
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    };

    // Handle general script errors
    const handleError = (event: ErrorEvent) => {
      if (event.error?.name === 'ChunkLoadError') {
        console.warn('Chunk load error caught:', event.error);
        event.preventDefault();
        
        // Reload page after a short delay
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    };

    // Add event listeners
    window.addEventListener('unhandledrejection', handleUnhandledRejection);
    window.addEventListener('error', handleError);

    // Cleanup on unmount
    return () => {
      window.removeEventListener('unhandledrejection', handleUnhandledRejection);
      window.removeEventListener('error', handleError);
    };
  }, []);

  return null; // This component doesn't render anything
} 