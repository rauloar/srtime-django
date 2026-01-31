import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface ConfirmationModalProps {
    isOpen: boolean;
    title: string;
    message: string;
    variant?: 'danger' | 'warning';
    onConfirm: () => void;
    onCancel: () => void;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
    isOpen,
    title,
    message,
    variant = 'warning',
    onConfirm,
    onCancel
}) => {
    if (!isOpen) return null;

    const getVariantColor = () => {
        return variant === 'danger' ? 'var(--status-error)' : 'var(--status-warning)';
    };

    return (
        <div
            style={{
                position: 'fixed',
                inset: 0,
                backgroundColor: 'var(--modal-overlay)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000
            }}
            onClick={onCancel}
        >
            <div
                className="card"
                style={{
                    width: '450px',
                    padding: '24px',
                    maxHeight: '85vh',
                    overflowY: 'auto'
                }}
                onClick={(e) => e.stopPropagation()}
            >
                {/* Icon and Title */}
                <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px', marginBottom: '16px' }}>
                    <div style={{
                        padding: '12px',
                        borderRadius: '8px',
                        backgroundColor: variant === 'danger' ? 'rgba(218, 54, 51, 0.15)' : 'rgba(210, 153, 34, 0.15)'
                    }}>
                        <AlertTriangle size={28} color={getVariantColor()} />
                    </div>
                    <div style={{ flex: 1 }}>
                        <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: 600 }}>
                            {title}
                        </h3>
                        <p style={{
                            margin: 0,
                            color: 'var(--text-secondary)',
                            fontSize: '14px',
                            lineHeight: '1.5'
                        }}>
                            {message}
                        </p>
                    </div>
                </div>

                {/* Action Buttons */}
                <div style={{
                    display: 'flex',
                    justifyContent: 'flex-end',
                    gap: '12px',
                    marginTop: '24px'
                }}>
                    <button
                        className="secondary"
                        onClick={onCancel}
                        style={{ minWidth: '100px' }}
                    >
                        Cancelar
                    </button>
                    <button
                        className={variant === 'danger' ? 'danger' : 'warning'}
                        onClick={() => {
                            onConfirm();
                            onCancel(); // Close modal after confirming
                        }}
                        style={{ minWidth: '100px' }}
                    >
                        OK
                    </button>
                </div>
            </div>
        </div>
    );
};
