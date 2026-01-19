import React from 'react';
import { 
    RefreshCw, Database, Download, Fingerprint 
} from 'lucide-react';

// ============ COMMAND CARD (Generic) ============
interface CommandCardProps {
    icon: React.ReactNode;
    title: string;
    description: string;
    action: () => void;
    variant?: 'primary' | 'danger' | 'warning';
    loading?: boolean;
    warning?: string; // Optional warning message
}

export const CommandCard = ({ 
    icon, 
    title, 
    description, 
    action, 
    variant = 'primary', 
    loading,
    warning
}: CommandCardProps) => {
    const getBorderColor = () => {
        switch (variant) {
            case 'danger': return '#da3633';
            case 'warning': return '#d29922';
            default: return 'var(--accent)';
        }
    };

    const getButtonClass = () => {
        switch (variant) {
            case 'danger': return 'danger';
            case 'warning': return 'warning';
            default: return 'primary';
        }
    };

    return (
        <div 
            className="card" 
            style={{ 
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                minHeight: '280px',
                borderLeft: `4px solid ${getBorderColor()}`,
                backgroundColor: warning ? (variant === 'danger' ? 'rgba(218, 54, 51, 0.05)' : 'rgba(210, 153, 34, 0.05)') : undefined
            }}
        >
            {warning && (
                <div style={{
                    width: '100%',
                    padding: '10px',
                    marginBottom: '15px',
                    backgroundColor: variant === 'danger' ? 'rgba(218, 54, 51, 0.15)' : 'rgba(210, 153, 34, 0.15)',
                    border: `1px solid ${variant === 'danger' ? '#da3633' : '#d29922'}`,
                    borderRadius: '4px',
                    fontSize: '12px',
                    color: variant === 'danger' ? '#ff6b6b' : '#d29922',
                    fontWeight: '600'
                }}>
                    ⚠️ {warning}
                </div>
            )}
            
            <div style={{ fontSize: '48px', marginBottom: '15px', color: 'var(--accent)' }}>
                {icon}
            </div>
            <h3 style={{ marginBottom: '10px', fontSize: '16px', fontWeight: '600' }}>
                {title}
            </h3>
            <p style={{ color: '#8b949e', fontSize: '13px', marginBottom: '20px', flexGrow: 1 }}>
                {description}
            </p>
            <button 
                onClick={action} 
                disabled={loading}
                className={getButtonClass()}
                style={{ width: '100%' }}
            >
                {loading ? (
                    <>
                        <RefreshCw size={16} className="spin" style={{ marginRight: '8px' }} />
                        Procesando...
                    </>
                ) : (
                    'Ejecutar'
                )}
            </button>
        </div>
    );
};

// ============ PROGRESS BAR (Helper) ============
interface ProgressBarProps {
    label: string;
    used: number;
    total: number;
}

const ProgressBar = ({ label, used, total }: ProgressBarProps) => {
    const percentage = total > 0 ? (used / total) * 100 : 0;
    const color = percentage > 90 ? '#da3633' : percentage > 70 ? '#d29922' : '#2ea043';
    
    return (
        <div style={{ marginBottom: '15px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '5px' }}>
                <span>{label}</span>
                <span style={{ color: '#8b949e' }}>{used}/{total} ({percentage.toFixed(1)}%)</span>
            </div>
            <div style={{ background: '#21262d', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ 
                    width: `${percentage}%`, 
                    height: '100%', 
                    background: color,
                    transition: 'width 0.3s'
                }} />
            </div>
        </div>
    );
};

// ============ MEMORY CARD ============
interface MemoryCardProps {
    memoryInfo: any | null;
    onLoad: () => void;
    loading?: boolean;
}

export const MemoryCard = ({ memoryInfo, onLoad, loading }: MemoryCardProps) => {
    return (
        <div className="card" style={{ 
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            minHeight: '280px',
            borderLeft: '4px solid var(--accent)'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
                <Database size={24} color="var(--accent)" />
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>Información de Memoria</h3>
            </div>
            
            {!memoryInfo ? (
                <>
                    <p style={{ color: '#8b949e', fontSize: '13px', marginBottom: '20px', flexGrow: 1 }}>
                        Ver capacidad de usuarios, huellas y registros
                    </p>
                    <button onClick={onLoad} disabled={loading} style={{ width: '100%' }}>
                        {loading ? (
                            <>
                                <Database size={16} className="spin" style={{ marginRight: '8px' }} />
                                Cargando...
                            </>
                        ) : (
                            <>
                                <Database size={16} style={{ marginRight: '8px' }} />
                                Cargar Memoria
                            </>
                        )}
                    </button>
                </>
            ) : (
                <>
                    <div style={{ flexGrow: 1 }}>
                        <ProgressBar 
                            label="Usuarios" 
                            used={memoryInfo.users} 
                            total={memoryInfo.users_cap} 
                        />
                        <ProgressBar 
                            label="Huellas" 
                            used={memoryInfo.fingers} 
                            total={memoryInfo.fingers_cap} 
                        />
                        <ProgressBar 
                            label="Registros" 
                            used={memoryInfo.records} 
                            total={memoryInfo.records_cap} 
                        />
                    </div>
                    <button onClick={onLoad} disabled={loading} style={{ width: '100%' }}>
                        {loading ? (
                            <>
                                <RefreshCw size={16} className="spin" style={{ marginRight: '8px' }} />
                                Actualizando...
                            </>
                        ) : (
                            <>
                                <RefreshCw size={16} style={{ marginRight: '8px' }} />
                                Actualizar
                            </>
                        )}
                    </button>
                </>
            )}
        </div>
    );
};

// ============ RECENT LOGS CARD ============
interface RecentLogsCardProps {
    logs: any[];
    onLoad: () => void;
    loading?: boolean;
}

export const RecentLogsCard = ({ logs, onLoad, loading }: RecentLogsCardProps) => {
    return (
        <div className="card" style={{ 
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            minHeight: '280px',
            borderLeft: '4px solid var(--accent)',
            justifyContent: 'center',
            alignItems: 'center'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px', width: '100%', justifyContent: 'space-between' }}>
                <div>
                    <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>Últimas Fichadas</h3>
                </div>
                <button 
                    onClick={onLoad} 
                    disabled={loading}
                    style={{ padding: '5px 10px', minWidth: 'auto' }}
                >
                    <RefreshCw size={16} className={loading ? 'spin' : ''} />
                </button>
            </div>
            
            <p style={{ color: '#8b949e', fontSize: '13px', marginBottom: '20px', textAlign: 'center' }}>
                Registros de asistencia disponibles
            </p>
            
            <div style={{ 
                textAlign: 'center',
                flexGrow: 1,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center'
            }}>
                <div style={{
                    fontSize: '48px',
                    fontWeight: 'bold',
                    color: 'var(--accent)',
                    marginBottom: '10px'
                }}>
                    {logs.length}
                </div>
                <p style={{ margin: 0, color: '#8b949e', fontSize: '12px' }}>
                    registros disponibles
                </p>
            </div>
        </div>
    );
};

// ============ TEMPLATES CARD ============
interface TemplatesCardProps {
    templates: any[] | null;
    onLoad: () => void;
    loading?: boolean;
}

export const TemplatesCard = ({ templates, onLoad, loading }: TemplatesCardProps) => {
    return (
        <div className="card" style={{ 
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            minHeight: '280px',
            borderLeft: '4px solid var(--accent)'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '15px' }}>
                <Fingerprint size={24} color="var(--accent)" />
                <h3 style={{ margin: 0, fontSize: '16px', fontWeight: '600' }}>Templates de Huellas</h3>
            </div>
            
            <p style={{ color: '#8b949e', fontSize: '13px', marginBottom: '15px', flexGrow: templates === null ? 1 : 0 }}>
                Descargar y visualizar templates biométricos
            </p>
            
            {templates === null ? (
                <button onClick={onLoad} disabled={loading} style={{ width: '100%' }}>
                    {loading ? (
                        <>
                            <RefreshCw size={16} className="spin" style={{ marginRight: '8px' }} />
                            Cargando...
                        </>
                    ) : (
                        <>
                            <Download size={16} style={{ marginRight: '8px' }} />
                            Descargar Templates
                        </>
                    )}
                </button>
            ) : (
                <>
                    <div style={{ 
                        textAlign: 'center', 
                        padding: '20px',
                        background: '#0d1117',
                        borderRadius: '6px',
                        marginBottom: '15px',
                        flexGrow: 1,
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center'
                    }}>
                        <div style={{ fontSize: '48px', fontWeight: 'bold', color: 'var(--accent)', marginBottom: '10px' }}>
                            {templates.length}
                        </div>
                        <div style={{ color: '#8b949e', fontSize: '13px' }}>
                            Templates descargados
                        </div>
                    </div>
                    <button onClick={onLoad} disabled={loading} style={{ width: '100%' }}>
                        {loading ? (
                            <>
                                <RefreshCw size={16} className="spin" style={{ marginRight: '8px' }} />
                                Actualizando...
                            </>
                        ) : (
                            <>
                                <RefreshCw size={16} style={{ marginRight: '8px' }} />
                                Actualizar
                            </>
                        )}
                    </button>
                </>
            )}
        </div>
    );
};
