import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  fullScreen?: boolean;
  className?: string;
}

/**
 * LoadingSpinner Component
 * 
 * Componente visual para indicador de carga.
 * Puramente presentacional, sin lógica.
 * 
 * Ejemplo:
 * <LoadingSpinner size="md" message="Cargando..." />
 * <LoadingSpinner size="lg" fullScreen />
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  message,
  fullScreen = false,
  className = ''
}) => {
  const sizeClasses = {
    sm: '32px',
    md: '48px',
    lg: '64px'
  };

  const spinnerSize = sizeClasses[size];

  const containerClass = fullScreen
    ? 'fixed inset-0 flex items-center justify-center bg-black/5 backdrop-blur-sm z-50'
    : 'flex items-center justify-center py-8';

  return (
    <div className={`${containerClass} ${className}`}>
      <div className="flex flex-col items-center gap-3">
        <div
          className="loading-spinner"
          style={{
            width: spinnerSize,
            height: spinnerSize,
            borderWidth: '4px',
            borderStyle: 'solid',
            borderColor: '#e5e7eb',
            borderTopColor: '#3b82f6',
            borderRadius: '50%',
            animation: 'spin 0.8s linear infinite'
          }}
        />
        {message && (
          <p className="text-sm text-gray-600 font-medium">
            {message}
          </p>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner;
