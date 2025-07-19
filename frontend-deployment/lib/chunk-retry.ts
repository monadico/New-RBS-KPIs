// lib/chunk-retry.ts
'use client'

interface ChunkRetryConfig {
  maxRetries?: number;
  retryDelay?: number;
}

class ChunkRetryManager {
  private retryCount = new Map<string, number>();
  private maxRetries: number;
  private retryDelay: number;

  constructor(config: ChunkRetryConfig = {}) {
    this.maxRetries = config.maxRetries || 3;
    this.retryDelay = config.retryDelay || 1000;
  }

  async retryChunkLoad(chunkId: string, loadFunction: () => Promise<any>): Promise<any> {
    const currentRetries = this.retryCount.get(chunkId) || 0;

    try {
      const result = await loadFunction();
      // Reset retry count on success
      this.retryCount.delete(chunkId);
      return result;
    } catch (error) {
      console.warn(`Chunk ${chunkId} failed to load (attempt ${currentRetries + 1}):`, error);

      if (currentRetries < this.maxRetries) {
        this.retryCount.set(chunkId, currentRetries + 1);
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, this.retryDelay));
        
        // Retry with exponential backoff
        const backoffDelay = this.retryDelay * Math.pow(2, currentRetries);
        await new Promise(resolve => setTimeout(resolve, backoffDelay));
        
        return this.retryChunkLoad(chunkId, loadFunction);
      } else {
        console.error(`Chunk ${chunkId} failed to load after ${this.maxRetries} attempts`);
        // Reset retry count
        this.retryCount.delete(chunkId);
        throw error;
      }
    }
  }

  handleChunkError(error: any): void {
    if (error?.name === 'ChunkLoadError') {
      console.warn('Chunk load error detected:', error.message);
      
      // Try to reload the page as a last resort
      if (typeof window !== 'undefined') {
        console.log('Attempting page reload due to chunk load error...');
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    }
  }
}

// Global instance
export const chunkRetryManager = new ChunkRetryManager({
  maxRetries: 3,
  retryDelay: 1000,
});

// Error handler for chunk loading
export function setupChunkErrorHandler(): void {
  if (typeof window === 'undefined') return;

  // Handle unhandled promise rejections (chunk errors)
  window.addEventListener('unhandledrejection', (event) => {
    if (event.reason?.name === 'ChunkLoadError') {
      console.warn('Chunk load error caught:', event.reason);
      event.preventDefault(); // Prevent default error handling
      chunkRetryManager.handleChunkError(event.reason);
    }
  });

  // Handle general errors
  window.addEventListener('error', (event) => {
    if (event.error?.name === 'ChunkLoadError') {
      console.warn('Chunk load error caught:', event.error);
      event.preventDefault();
      chunkRetryManager.handleChunkError(event.error);
    }
  });
}

// Hook for React components
export function useChunkErrorHandler(): void {
  if (typeof window === 'undefined') return;

  React.useEffect(() => {
    setupChunkErrorHandler();
  }, []);
}

// Fallback for missing React import
declare global {
  var React: any;
} 