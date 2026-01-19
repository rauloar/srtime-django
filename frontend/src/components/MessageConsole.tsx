import { useEffect, useState, useRef } from 'react';

interface LogMessage {
    type: string;
    job_id: string;
    device_id?: number;
    level?: string;
    message?: string;
    status?: string;
    progress?: number;
    error?: string;
    job_type?: string;
    ts: string;
}

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/logs';

export function MessageConsole() {
    const [logs, setLogs] = useState<LogMessage[]>([]);
    const [connected, setConnected] = useState(false);
    const ws = useRef<WebSocket | null>(null);
    const endRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        const connect = () => {
            ws.current = new WebSocket(WS_URL);

            ws.current.onopen = () => {
                setConnected(true);
                // setLogs(prev => [...prev, { type: 'system', message: 'Connected to Realtime Logs', ts: new Date().toISOString(), job_id: 'sys', level: 'INFO' }]);
            };

            ws.current.onclose = () => {
                setConnected(false);
                setTimeout(connect, 3000); // Reconnect
            };

            ws.current.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    setLogs(prev => {
                        const newLogs = [...prev, data];
                        if (newLogs.length > 500) return newLogs.slice(-500); // Keep last 500
                        return newLogs;
                    });
                } catch (e) {
                    console.error("WS Parse error", e);
                }
            };
        };

        connect();

        return () => {
            ws.current?.close();
        };
    }, []);

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    const clearLogs = () => setLogs([]);

    return (
        <div style={{
            position: 'fixed',
            bottom: 0,
            right: 0,
            width: '600px',
            height: '300px',
            background: '#0d1117',
            borderTopLeftRadius: '8px',
            border: '1px solid #30363d',
            display: 'flex',
            flexDirection: 'column',
            boxShadow: '-2px -2px 10px rgba(0,0,0,0.5)',
            zIndex: 1000,
            fontFamily: 'monospace',
            fontSize: '12px'
        }}>
            <div style={{
                padding: '8px',
                background: '#161b22',
                borderBottom: '1px solid #30363d',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderTopLeftRadius: '8px',
                color: '#c9d1d9'
            }}>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <strong>Message Console</strong>
                    <span style={{
                        width: '8px', height: '8px', borderRadius: '50%',
                        background: connected ? '#2ea043' : '#da3633',
                        display: 'inline-block'
                    }} title={connected ? "Connected" : "Disconnected"} />
                </div>
                <button onClick={clearLogs} style={{ background: 'transparent', border: 'none', color: '#8b949e', cursor: 'pointer' }}>Clear</button>
            </div>

            <div style={{
                flex: 1,
                overflowY: 'auto',
                padding: '10px',
                color: '#e6edf3'
            }}>
                {logs.map((log, i) => (
                    <div key={i} style={{ marginBottom: '4px', borderBottom: '1px solid #21262d', paddingBottom: '2px' }}>
                        <span style={{ color: '#8b949e', marginRight: '8px' }}>[{new Date(log.ts).toLocaleTimeString()}]</span>
                        {log.device_id && <span style={{ color: '#58a6ff', marginRight: '8px' }}>[Dev:{log.device_id}]</span>}
                        {log.type === 'job_created' && <span style={{ color: '#a371f7' }}>Job Created: {log.job_id} ({log.message || log.job_type})</span>}
                        {log.type === 'job_started' && <span style={{ color: '#ebbbf2' }}>Job Started: {log.job_id}</span>}
                        {log.type === 'job_finished' && (
                            <span style={{ color: log.status === 'completed' ? '#2ea043' : '#da3633' }}>
                                Job Finished: {log.job_id} - {log.status} {log.error && `(${log.error})`}
                            </span>
                        )}
                        {log.type === 'log' && (
                            <span style={{ color: log.level === 'ERROR' ? '#da3633' : log.level === 'WARNING' ? '#d29922' : '#e6edf3' }}>
                                {log.message}
                            </span>
                        )}
                        {log.type === 'progress' && (
                            <span style={{ color: '#79c0ff' }}>Progress {log.job_id}: {log.progress}%</span>
                        )}
                    </div>
                ))}
                <div ref={endRef} />
            </div>
        </div>
    );
}
