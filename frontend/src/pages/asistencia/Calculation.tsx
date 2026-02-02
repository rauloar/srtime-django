
import React, { useState, useEffect } from 'react';
import { calculateAttendance, getDepartments, type Department } from '../../api';
import { Play, CheckCircle, AlertCircle } from 'lucide-react';

export const Calculation: React.FC = () => {
    const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
    const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);
    const [departmentId, setDepartmentId] = useState<string>("");
    const [departments, setDepartments] = useState<Department[]>([]);

    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<{ count: number, message: string } | null>(null);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        getDepartments().then(setDepartments).catch(console.error);
    }, []);

    const handleCalculate = async () => {
        setLoading(true);
        setResult(null);
        setError(null);
        try {
            const res = await calculateAttendance(startDate, endDate, departmentId ? parseInt(departmentId) : undefined);
            setResult(res);
        } catch (e: any) {
            setError(e.response?.data?.detail || "Calculation failed");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ maxWidth: '600px', margin: '0 auto', padding: '20px' }}>
            <div className="card">
                <h2>Cálculo de Asistencia</h2>
                <p className="text-muted">Procesar marcaciones y generar reporte diario.</p>

                <div className="flex-col gap-4" style={{ marginTop: '20px' }}>
                    <div className="flex-col gap-2">
                        <label>Rango de Fechas</label>
                        <div className="flex-row gap-2">
                            <input
                                type="date"
                                value={startDate}
                                onChange={e => setStartDate(e.target.value)}
                                className="form-control"
                            />
                            <span style={{ alignSelf: 'center' }}>a</span>
                            <input
                                type="date"
                                value={endDate}
                                onChange={e => setEndDate(e.target.value)}
                                className="form-control"
                            />
                        </div>
                    </div>

                    <div className="flex-col gap-2">
                        <label>Departamento (Opcional)</label>
                        <select
                            className="form-control"
                            value={departmentId}
                            onChange={e => setDepartmentId(e.target.value)}
                        >
                            <option value="">Todos</option>
                            {departments.map(d => (
                                <option key={d.id} value={d.id}>{d.name}</option>
                            ))}
                        </select>
                    </div>

                    <button
                        className="primary flex-row gap-2 center"
                        style={{ marginTop: '10px' }}
                        onClick={handleCalculate}
                        disabled={loading}
                    >
                        {loading ? "Procesando..." : <><Play size={18} /> Calcular</>}
                    </button>

                    {result && (
                        <div style={{ background: '#e8f5e9', color: '#2e7d32', padding: '15px', borderRadius: '4px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <CheckCircle size={20} />
                            <div>
                                <strong>Éxito</strong><br />
                                {result.message}
                            </div>
                        </div>
                    )}

                    {error && (
                        <div style={{ background: '#ffebee', color: '#c62828', padding: '15px', borderRadius: '4px', display: 'flex', gap: '10px', alignItems: 'center' }}>
                            <AlertCircle size={20} />
                            <div>
                                <strong>Error</strong><br />
                                {error}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
