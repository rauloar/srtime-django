import React, { type ReactNode } from 'react';
import { Search } from 'lucide-react';

interface PageToolbarProps {
    title: string;
    subtitle?: string;
    onSearch?: (term: string) => void;
    searchPlaceholder?: string;
    actions?: ReactNode;
    children?: ReactNode; // Extra filters
}

export const PageToolbar: React.FC<PageToolbarProps> = ({ title, subtitle, onSearch, searchPlaceholder, actions, children }) => {
    return (
        <div className="flex-col gap-4" style={{ marginBottom: '20px' }}>
            <div className="flex-row space-between wrap">
                <div className="flex-col">
                    <h2 style={{ margin: 0, fontSize: '24px', fontWeight: 600, color: '#333' }}>{title}</h2>
                    {subtitle && <span style={{ fontSize: '14px', color: '#666' }}>{subtitle}</span>}
                </div>
                <div className="flex-row gap-2">
                    {actions}
                </div>
            </div>

            <div className="card" style={{ padding: '15px', background: 'white', border: '1px solid #eee', display: 'flex', gap: '15px', alignItems: 'center', flexWrap: 'wrap' }}>
                {onSearch && (
                    <div style={{ position: 'relative', width: '300px', maxWidth: '100%' }}>
                        <Search size={16} style={{ position: 'absolute', left: '10px', top: '9px', color: '#999' }} />
                        <input
                            type="text"
                            placeholder={searchPlaceholder || "Buscar..."}
                            onChange={(e) => onSearch(e.target.value)}
                            style={{ paddingLeft: '32px', width: '100%', height: '36px', border: '1px solid #ddd', borderRadius: '4px' }}
                        />
                    </div>
                )}
                {children}
            </div>
        </div>
    );
};
