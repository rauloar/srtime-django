import React from 'react';

interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
    disabled?: boolean;
  };
  className?: string;
}

/**
 * EmptyState Component
 * 
 * Componente visual pasivo para mostrar estados vacíos.
 * NO contiene lógica de negocio, solo presentación.
 * Las acciones (si existen) se pueden deshabilitar.
 * 
 * Ejemplo:
 * <EmptyState 
 *   title="Sin empleados"
 *   description="No hay empleados registrados"
 *   icon={<Users size={48} />}
 * />
 */
export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon,
  action,
  className = ''
}) => {
  return (
    <div className={`empty-state-container ${className}`}>
      <div className="empty-state-content">
        {icon && (
          <div className="empty-state-icon">
            {icon}
          </div>
        )}
        
        <h3 className="empty-state-title">
          {title}
        </h3>
        
        {description && (
          <p className="empty-state-description">
            {description}
          </p>
        )}
        
        {action && (
          <button
            className="empty-state-button"
            onClick={action.onClick}
            disabled={action.disabled ?? false}
            style={{
              opacity: action.disabled ? 0.5 : 1,
              cursor: action.disabled ? 'not-allowed' : 'pointer'
            }}
          >
            {action.label}
          </button>
        )}
      </div>
    </div>
  );
};

export default EmptyState;
