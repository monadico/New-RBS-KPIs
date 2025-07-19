'use client'

import { useEffect } from 'react'

export function ChunkErrorHandler() {
  useEffect(() => {
    let hasReloaded = false;

    // Handle unhandled promise rejections (chunk errors)
    const handleUnhandledRejection = (event: PromiseRejectionEvent) => {
      if (event.reason?.name === 'ChunkLoadError' && !hasReloaded) {
        console.warn('Chunk load error detected, will reload page once:', event.reason);
        hasReloaded = true;
        
        // Reload page after a delay, but only once
        setTimeout(() => {
          window.location.reload();
        }, 3000);
      }
    };

    // Handle general script errors
    const handleError = (event: ErrorEvent) => {
      if (event.error?.name === 'ChunkLoadError' && !hasReloaded) {
        console.warn('Script error detected, will reload page once:', event.error);
        hasReloaded = true;
        
        // Reload page after a delay, but only once
        setTimeout(() => {
          window.location.reload();
        }, 3000);
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