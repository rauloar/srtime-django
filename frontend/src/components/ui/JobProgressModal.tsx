import React, { useEffect, useState, useRef } from 'react';
import { X, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { getJob, getJobLogs } from '../../api';

// ... imports

interface JobProgressModalProps {
    jobId: string;
    isOpen: boolean;
    onClose: () => void;
    title?: string;
}

interface JobState {
    id: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    progress: number;
    error?: string;
    logs: { timestamp: string, message: string, level: string }[];
}

export const JobProgressModal: React.FC<JobProgressModalProps> = ({ jobId, isOpen, onClose, title = "Procesando Importación..." }) => {
    const [job, setJob] = useState<JobState | null>(null);
    const [isFinished, setIsFinished] = useState(false);
    const logsEndRef = useRef<HTMLDivElement>(null);

    // Poll for status
    useEffect(() => {
        if (!isOpen || !jobId) return;

        setIsFinished(false);
        setJob(null);

        const interval = setInterval(async () => {
            try {
                const [status, logs] = await Promise.all([
                    getJob(jobId),
                    getJobLogs(jobId)
                ]);

                // Ensure logs is always an array
                const logsArray = Array.isArray(logs) ? logs : [];

                setJob({
                    ...status,
                    status: status.status as any, // Cast string to enum
                    logs: logsArray
                });

                if (status.status === 'completed' || status.status === 'failed') {
                    setIsFinished(true);
                    clearInterval(interval);
                }
            } catch (error) {
                setJob(prev => prev || {
                    id: jobId,
                    status: 'failed',
                    progress: 0,
                    error: 'No se pudo consultar el estado del proceso.',
                    logs: []
                });
                setIsFinished(true);
                clearInterval(interval);
            }
        }, 1000);

        return () => clearInterval(interval);
    }, [jobId, isOpen]);

    // Auto-scroll logs
    useEffect(() => {
        logsEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [job?.logs]);

    if (!isOpen) return null;

    return (
        <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 9999
        }}>
            <div style={{
                width: '600px',
                backgroundColor: 'var(--bg-card)',
                borderRadius: '8px',
                boxShadow: 'var(--shadow-md)',
                display: 'flex',
                flexDirection: 'column',
                maxHeight: '80vh',
                border: '1px solid var(--border-color)'
            }}>
                {/* Header */}
                <div style={{
                    padding: '16px 20px',
                    borderBottom: '1px solid var(--border-color)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    backgroundColor: 'var(--header-bg)',
                    color: 'var(--header-text)',
                    borderTopLeftRadius: '8px',
                    borderTopRightRadius: '8px'
                }}>
                    <h3 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>{title}</h3>
                    {isFinished && (
                        <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'white', cursor: 'pointer' }}>
                            <X size={20} />
                        </button>
                    )}
                </div>

                {/* Body */}
                <div style={{ padding: '20px', overflowY: 'auto', flex: 1, display: 'flex', flexDirection: 'column', gap: '20px' }}>

                    {/* Status Icon & Text */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '10px' }}>
                        {!isFinished && <Loader size={40} className="spin" style={{ color: 'var(--primary)' }} />}
                        {job?.status === 'completed' && <CheckCircle size={48} style={{ color: 'var(--status-ok)' }} />}
                        {job?.status === 'failed' && <AlertCircle size={48} style={{ color: 'var(--status-error)' }} />}

                        <div style={{ fontSize: '18px', fontWeight: 500, color: 'var(--text-main)' }}>
                            {job?.status === 'pending' && 'Iniciando...'}
                            {job?.status === 'running' && 'En Progreso...'}
                            {job?.status === 'completed' && 'Finalizado con Éxito'}
                            {job?.status === 'failed' && 'Error en el Proceso'}
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div style={{ width: '100%', height: '10px', backgroundColor: 'var(--border-color)', borderRadius: '5px', overflow: 'hidden' }}>
                        <div style={{
                            width: `${job?.progress || 0}%`,
                            height: '100%',
                            backgroundColor: job?.status === 'failed' ? 'var(--status-error)' : 'var(--primary)',
                            transition: 'width 0.5s ease'
                        }}></div>
                    </div>
                    <div style={{ textAlign: 'right', fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {job?.progress || 0}%
                    </div>

                    {/* Logs Console */}
                    <div style={{
                        backgroundColor: '#000',
                        color: '#0f0',
                        padding: '10px',
                        borderRadius: '4px',
                        height: '200px',
                        overflowY: 'auto',
                        fontSize: '12px',
                        fontFamily: 'monospace'
                    }}>
                        {job?.logs?.map((log: { timestamp: string, message: string, level: string }, i: number) => (
                            <div key={i} style={{ marginBottom: '4px', color: log.level === 'ERROR' ? '#f55' : '#0f0' }}>
                                <span style={{ opacity: 0.7 }}>[{new Date(log.timestamp).toLocaleTimeString()}]</span> {log.message}
                            </div>
                        ))}
                        {!job?.logs?.length && <div style={{ opacity: 0.5 }}>Esperando logs...</div>}
                        <div ref={logsEndRef} />
                    </div>

                    {/* Error Message */}
                    {job?.error && (
                        <div style={{ padding: '10px', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid var(--status-error)', borderRadius: '4px', color: 'var(--status-error)' }}>
                            <strong>Error:</strong> {job.error}
                        </div>
                    )}

                </div>

                {/* Footer */}
                <div style={{ padding: '16px 20px', borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                        onClick={onClose}
                        disabled={!isFinished}
                        className={isFinished ? 'primary' : ''}
                        style={{ minWidth: '100px' }}
                    >
                        {isFinished ? 'Cerrar' : 'Procesando...'}
                    </button>
                </div>
            </div>
            <style>{`
                .spin { animation: spin 1s linear infinite; }
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            `}</style>
        </div>
    );
};
