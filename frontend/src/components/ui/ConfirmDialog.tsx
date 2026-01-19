import React from 'react';
import { AlertTriangle } from 'lucide-react';

interface ConfirmDialogProps {
    isOpen: boolean;
    title: string;
    message: string;
    confirmText?: string;
    cancelText?: string;
    type?: 'danger' | 'warning' | 'info';
    onConfirm: () => void;
    onCancel: () => void;
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
    isOpen, title, message, confirmText = 'Confirmar', cancelText = 'Cancelar', type = 'warning', onConfirm, onCancel
}) => {
    if (!isOpen) return null;

    const color = type === 'danger' ? '#d32f2f' : '#f57c00';

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 2000
        }}>
            <div className="card" style={{ width: '400px', padding: '0', overflow: 'hidden' }}>
                <div style={{ padding: '20px', display: 'flex', gap: '15px' }}>
                    <div style={{
                        minWidth: '40px', height: '40px', borderRadius: '50%',
                        background: type === 'danger' ? '#ffebee' : '#fff3e0',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        color: color
                    }}>
                        <AlertTriangle size={24} />
                    </div>
                    <div>
                        <h3 style={{ margin: '0 0 10px 0' }}>{title}</h3>
                        <p style={{ margin: 0, color: '#666', fontSize: '14px', lineHeight: '1.5' }}>{message}</p>
                    </div>
                </div>
                <div style={{ padding: '15px 20px', background: '#f9fafb', display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                    <button className="secondary" onClick={onCancel}>{cancelText}</button>
                    <button
                        style={{
                            background: color, color: 'white', border: 'none',
                            padding: '8px 16px', borderRadius: '4px', cursor: 'pointer', fontWeight: 500
                        }}
                        onClick={onConfirm}
                    >
                        {confirmText}
                    </button>
                </div>
            </div>
        </div>
    );
};
