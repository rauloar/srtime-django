import { useContext } from 'react';
import { ToastContext, type ToastType } from '../contexts/ToastContext';

export const useToast = () => {
  const context = useContext(ToastContext);

  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }

  return {
    success: (message: string, duration?: number) =>
      context.addToast({ type: 'success', message, duration }),
    error: (message: string, duration?: number) =>
      context.addToast({ type: 'error', message, duration }),
    warning: (message: string, duration?: number) =>
      context.addToast({ type: 'warning', message, duration }),
    info: (message: string, duration?: number) =>
      context.addToast({ type: 'info', message, duration }),
    custom: (type: ToastType, message: string, duration?: number) =>
      context.addToast({ type, message, duration }),
    dismiss: context.removeToast,
    clearAll: context.clearAll,
  };
};
