import React, { useEffect, useState } from 'react';
import { Save, Database, Download, Upload, TestTube } from 'lucide-react';
import { getSettings, updateSetting, type Setting, backupDatabase, listBackups, restoreDatabase, testDatabase, importDatabase, type BackupFile, type DatabaseTestResponse } from '../../api';
import { useAuth } from '../../hooks/useAuth';
import { useToast } from '../../hooks/useToast';

export const Settings: React.FC = () => {
    const [settings, setSettings] = useState<Setting[]>([]);
    const [loading, setLoading] = useState(true);
    const [backups, setBackups] = useState<BackupFile[]>([]);
    const [testResult, setTestResult] = useState<DatabaseTestResponse | null>(null);
    const [operationLoading, setOperationLoading] = useState(false);
    const [importing, setImporting] = useState(false);
    const [importFile, setImportFile] = useState<File | null>(null);
    const { role } = useAuth();
    const { success: showSuccess, error: showError } = useToast();

    useEffect(() => {
        fetchSettings();
        if (role === 'admin') {
            fetchBackups();
        }
    }, [role]);

    const fetchSettings = async () => {
        try {
            const data = await getSettings();
            setSettings(data || []); // Asegurar que siempre sea array
        } catch (error) {
            console.error('Error fetching settings:', error);
            setSettings([]); // Establecer array vacío en caso de error
        } finally {
            setLoading(false);
        }
    };

    const fetchBackups = async () => {
        try {
            const data = await listBackups();
            setBackups(data.backups || []);
        } catch (error) {
            console.error('Error fetching backups:', error);
            setBackups([]); // No fallar si el endpoint no existe
        }
    };

    const handleBackup = async () => {
        setOperationLoading(true);
        try {
            const result = await backupDatabase();
            showSuccess(`Backup creado: ${result.file} (${result.size_mb} MB)`);
            fetchBackups();
        } catch (error: any) {
            showError(`Error al crear backup: ${error.response?.data?.detail || error.message}`);
        } finally {
            setOperationLoading(false);
        }
    };

    const handleRestore = async (filename: string) => {
        if (!confirm(`¿Está seguro de restaurar la base de datos desde ${filename}? Esta acción sobrescribirá todos los datos actuales.`)) {
            return;
        }

        setOperationLoading(true);
        try {
            const result = await restoreDatabase(filename);
            showSuccess(result.message);
        } catch (error: any) {
            showError(`Error al restaurar: ${error.response?.data?.detail || error.message}`);
        } finally {
            setOperationLoading(false);
        }
    };

    const handleTest = async () => {
        setOperationLoading(true);
        try {
            const result = await testDatabase();
            setTestResult(result);
            showSuccess('Test de base de datos completado');
        } catch (error: any) {
            showError(`Error al probar BD: ${error.response?.data?.detail || error.message}`);
        } finally {
            setOperationLoading(false);
        }
    };

    const handleImport = async () => {
        if (!importFile) {
            showError('Seleccione un archivo .sql para importar');
            return;
        }
        setImporting(true);
        try {
            const result = await importDatabase(importFile);
            showSuccess(result.message || 'Importación completada');
        } catch (error: any) {
            showError(`Error al importar: ${error.response?.data?.detail || error.message}`);
        } finally {
            setImporting(false);
        }
    };

    const handleSave = async (key: string, value: string) => {
        try {
            await updateSetting({ key, value });
            // Optimistic update of specific setting or refresh all
            fetchSettings();
            alert('Configuración guardada.');
        } catch (error) {
            alert('Error al guardar.');
        }
    };

    // Asegurar que settings siempre sea un array antes de agrupar
    const safeSettings = Array.isArray(settings) ? settings : [];

    const groupedSettings = {
        'General': safeSettings.filter(s => s.key.startsWith('app_') || s.key.startsWith('company_')),
        'Asistencia': safeSettings.filter(s => s.key.startsWith('att_')),
        'Base de Datos': safeSettings.filter(s => s.key.startsWith('db_')),
        'Otros': safeSettings.filter(s => !s.key.match(/^(app|company|att|db)_/))
    };

    return (
        <div className="flex-col gap-4">
            <h2 style={{ fontSize: '20px', fontWeight: 600 }}>Configuración del Sistema</h2>

            {loading ? <p>Cargando...</p> : (
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
                    {Object.entries(groupedSettings).map(([category, items]) => (
                        items.length > 0 && (
                            <div key={category} className="card">
                                <div className="card-header">{category}</div>
                                <div className="flex-col gap-4">
                                    {items.map(s => (
                                        <div key={s.key} className="flex-col gap-2">
                                            <label style={{ fontSize: '12px', fontWeight: 500 }}>
                                                {s.description || s.key}
                                            </label>
                                            <div className="flex-row gap-2">
                                                <input
                                                    defaultValue={s.value}
                                                    id={`input-${s.key}`}
                                                    style={{ flex: 1 }}
                                                />
                                                <button
                                                    className="primary"
                                                    onClick={() => {
                                                        const el = document.getElementById(`input-${s.key}`) as HTMLInputElement;
                                                        handleSave(s.key, el.value);
                                                    }}
                                                >
                                                    <Save size={14} /> Guardar
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    ))}
                    {settings.length === 0 && <p className="text-muted">No se encontraron configuraciones.</p>}

                    {/* Herramientas de Base de Datos - Solo Admin */}
                    {role === 'admin' && (
                        <div className="card">
                            <div className="card-header">
                                <Database size={18} /> Herramientas de Base de Datos
                            </div>
                            <div className="flex-col gap-4">
                                {/* Acciones principales */}
                                <div className="flex-row gap-2" style={{ flexWrap: 'wrap' }}>
                                    <button
                                        className="primary"
                                        onClick={handleBackup}
                                        disabled={operationLoading}
                                    >
                                        <Download size={16} /> Crear Backup
                                    </button>
                                    <button
                                        className="secondary"
                                        onClick={handleTest}
                                        disabled={operationLoading}
                                    >
                                        <TestTube size={16} /> Probar Conexión
                                    </button>
                                    <div className="flex-row gap-2" style={{ alignItems: 'center' }}>
                                        <input
                                            type="file"
                                            accept=".sql"
                                            onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                                            style={{ fontSize: '12px', maxWidth: '220px' }}
                                        />
                                        <button
                                            className="secondary"
                                            onClick={handleImport}
                                            disabled={importing}
                                        >
                                            <Upload size={16} /> Importar BD
                                        </button>
                                    </div>
                                </div>

                                {/* Resultado del test */}
                                {testResult && (
                                    <div style={{
                                        padding: '12px',
                                        backgroundColor: 'var(--bg-highlight)',
                                        borderRadius: '6px',
                                        border: '1px solid var(--primary)'
                                    }}>
                                        <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                                            Estado de la Base de Datos
                                        </h4>
                                        <div style={{ fontSize: '12px', display: 'grid', gap: '4px' }}>
                                            <p><strong>Database:</strong> {testResult.database}</p>
                                            <p><strong>Conexión:</strong> {testResult.connection}</p>
                                            <p><strong>Tablas:</strong> {testResult.tables_count}</p>
                                            <p><strong>Tamaño:</strong> {testResult.size_mb} MB</p>
                                            <details style={{ marginTop: '8px' }}>
                                                <summary style={{ cursor: 'pointer', fontWeight: 500 }}>
                                                    Ver registros por tabla
                                                </summary>
                                                <div style={{ marginTop: '8px', paddingLeft: '12px' }}>
                                                    {Object.entries(testResult.records).map(([table, count]) => (
                                                        <p key={table}>{table}: {count} registros</p>
                                                    ))}
                                                </div>
                                            </details>
                                        </div>
                                    </div>
                                )}

                                {/* Lista de backups */}
                                {backups.length > 0 && (
                                    <div>
                                        <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '8px' }}>
                                            Backups Disponibles
                                        </h4>
                                        <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                                            {backups.map((backup) => (
                                                <div
                                                    key={backup.filename}
                                                    style={{
                                                        display: 'flex',
                                                        justifyContent: 'space-between',
                                                        alignItems: 'center',
                                                        padding: '8px',
                                                        borderBottom: '1px solid #e5e7eb',
                                                        fontSize: '12px'
                                                    }}
                                                >
                                                    <div>
                                                        <p style={{ fontWeight: 500 }}>{backup.filename}</p>
                                                        <p style={{ color: '#6b7280' }}>
                                                            {new Date(backup.created_at).toLocaleString()} - {backup.size_mb} MB
                                                        </p>
                                                    </div>
                                                    <button
                                                        className="danger"
                                                        onClick={() => handleRestore(backup.filename)}
                                                        disabled={operationLoading}
                                                        style={{ fontSize: '12px', padding: '4px 8px' }}
                                                    >
                                                        <Upload size={14} /> Restaurar
                                                    </button>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};
