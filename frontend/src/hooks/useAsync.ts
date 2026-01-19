import { useState, useEffect, useCallback, useRef } from 'react';
import { useToast } from './useToast';

interface UseAsyncOptions {
  retry?: number;
  timeout?: number;
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
  showToast?: boolean;
  toastMessages?: {
    loading?: string;
    success?: string;
    error?: string;
  };
}

export function useAsync<T>(
  asyncFn: () => Promise<T>,
  options: UseAsyncOptions = {}
) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const toast = useToast();
  const retryCountRef = useRef(0);

  const {
    retry = 0,
    timeout = 30000,
    onSuccess,
    onError,
    showToast = false,
    toastMessages = {},
  } = options;

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const timeoutPromise = new Promise<never>((_, reject) =>
        setTimeout(() => reject(new Error('Request timeout')), timeout)
      );

      const result = await Promise.race([asyncFn(), timeoutPromise]);

      setData(result);
      retryCountRef.current = 0;

      if (showToast && toastMessages.success) {
        toast.success(toastMessages.success);
      }

      onSuccess?.(result);
      return result;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));

      if (retryCountRef.current < retry) {
        retryCountRef.current += 1;
        const delay = Math.pow(2, retryCountRef.current) * 1000;
        if (showToast) {
          toast.warning(`Reintentando en ${delay / 1000}s...`);
        }
        setTimeout(execute, delay);
        return;
      }

      setError(error);

      if (showToast && toastMessages.error) {
        toast.error(toastMessages.error);
      }

      onError?.(error);
      throw error;
    } finally {
      setLoading(false);
    }
  }, [asyncFn, retry, timeout, onSuccess, onError, showToast, toastMessages, toast]);

  // Auto-fetch on mount
  useEffect(() => {
    execute();
  }, [execute]);

  const refetch = useCallback(() => {
    retryCountRef.current = 0;
    return execute();
  }, [execute]);

  return { data, loading, error, refetch, execute };
}
