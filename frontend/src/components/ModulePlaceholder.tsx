import React from 'react';

const ModulePlaceholder: React.FC<{ title: string }> = ({ title }) => {
    return (
        <div className="card" style={{ textAlign: 'center', padding: '50px' }}>
            <h2 style={{ color: 'var(--primary)' }}>{title}</h2>
            <p className="text-muted">Módulo en construcción</p>
            <div style={{ marginTop: '20px', fontSize: '48px', color: '#eee' }}>
                🚧
            </div>
        </div>
    );
};

export default ModulePlaceholder;
