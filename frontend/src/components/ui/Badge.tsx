import React from 'react';

type BadgeStatus = 'active' | 'inactive' | 'pending' | 'error' | 'success' | 'info' | 'warning';
type BadgeSize = 'sm' | 'md' | 'lg';

interface BadgeProps {
  status: BadgeStatus;
  label: string;
  size?: BadgeSize;
  className?: string;
}

/**
 * Badge Component
 * 
 * Componente visual pasivo para mostrar estados.
 * NO contiene lógica de negocio, solo presentación.
 * 
 * Ejemplo:
 * <Badge status="active" label="Activo" size="md" />
 * <Badge status="inactive" label="Inactivo" size="sm" />
 */
export const Badge: React.FC<BadgeProps> = ({ 
  status, 
  label, 
  size = 'md',
  className = ''
}) => {
  const statusStyles: Record<BadgeStatus, { bg: string; text: string; border: string }> = {
    active: {
      bg: 'bg-green-50',
      text: 'text-green-700',
      border: 'border-green-200'
    },
    inactive: {
      bg: 'bg-gray-50',
      text: 'text-gray-700',
      border: 'border-gray-200'
    },
    pending: {
      bg: 'bg-yellow-50',
      text: 'text-yellow-700',
      border: 'border-yellow-200'
    },
    error: {
      bg: 'bg-red-50',
      text: 'text-red-700',
      border: 'border-red-200'
    },
    success: {
      bg: 'bg-blue-50',
      text: 'text-blue-700',
      border: 'border-blue-200'
    },
    info: {
      bg: 'bg-cyan-50',
      text: 'text-cyan-700',
      border: 'border-cyan-200'
    },
    warning: {
      bg: 'bg-orange-50',
      text: 'text-orange-700',
      border: 'border-orange-200'
    }
  };

  const sizeStyles: Record<BadgeSize, string> = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  const colors = statusStyles[status];
  const sizes = sizeStyles[size];

  return (
    <span
      className={`
        inline-block rounded-full border
        ${colors.bg} ${colors.text} ${colors.border}
        ${sizes}
        font-semibold whitespace-nowrap
        ${className}
      `}
      style={{
        backfaceVisibility: 'hidden'
      }}
    >
      {label}
    </span>
  );
};

export default Badge;
