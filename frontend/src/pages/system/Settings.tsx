import React, { useEffect, useState } from 'react';
import { Save, Database, Download, Upload, TestTube, Users, Plus, Trash2, Key } from 'lucide-react';
import {
    getSettings, updateSetting, type Setting,
    backupDatabase, listBackups, restoreDatabase, testDatabase, importDatabase,
    type BackupFile, type DatabaseTestResponse,
    getAuthUsers, createAuthUser, deleteAuthUser, updateAuthUserPassword,
    type AuthUser
} from '../../api';
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

    // Users management state
    const [users, setUsers] = useState<AuthUser[]>([]);
    const [showUserModal, setShowUserModal] = useState(false);
    const [showPasswordModal, setShowPasswordModal] = useState(false);
    const [selectedUser, setSelectedUser] = useState<AuthUser | null>(null);
    const [newUser, setNewUser] = useState({ username: '', password: '', email: '', first_name: '', last_name: '', is_staff: false, is_superuser: false });
    const [newPassword, setNewPassword] = useState('');

    const { role } = useAuth();
    const { success: showSuccess, error: showError } = useToast();

    useEffect(() => {
        fetchSettings();
        if (role === 'admin') {
            fetchBackups();
            fetchUsers();
        }
    }, [role]);

    const fetchSettings = async () => {
        try {
            const data = await getSettings();
            setSettings(data || []); // Asegurar que siempre sea array
        } catch (error) {
            showError('No se pudieron cargar las configuraciones');
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
            showError('No se pudieron cargar los backups');
            setBackups([]); // No fallar si el endpoint no existe
        }
    };

    const fetchUsers = async () => {
        try {
            const data = await getAuthUsers();
            setUsers(data || []);
        } catch (error) {
            showError('No se pudieron cargar los usuarios');
            setUsers([]);
        }
    };

    const handleCreateUser = async () => {
        if (!newUser.username || !newUser.password) {
            showError('Username y password son requeridos');
            return;
        }
        try {
            await createAuthUser(newUser);
            showSuccess('Usuario creado exitosamente');
            setShowUserModal(false);
            setNewUser({ username: '', password: '', email: '', first_name: '', last_name: '', is_staff: false, is_superuser: false });
            fetchUsers();
        } catch (error: any) {
            showError(`Error al crear usuario: ${error.response?.data?.detail || error.message}`);
        }
    };

    const handleDeleteUser = async (userId: number) => {
        if (!confirm('¿Está seguro de eliminar este usuario?')) return;
        try {
            await deleteAuthUser(userId);
            showSuccess('Usuario eliminado');
            fetchUsers();
        } catch (error: any) {
            showError(`Error al eliminar: ${error.response?.data?.detail || error.message}`);
        }
    };

    const handleChangePassword = async () => {
        if (!selectedUser || !newPassword) {
            showError('Ingrese una nueva contraseña');
            return;
        }
        try {
            await updateAuthUserPassword(selectedUser.id, newPassword);
            showSuccess('Contraseña actualizada');
            setShowPasswordModal(false);
            setNewPassword('');
            setSelectedUser(null);
        } catch (error: any) {
            showError(`Error al cambiar contraseña: ${error.response?.data?.detail || error.message}`);
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
            <h2 className="text-lg font-semibold">Configuración del Sistema</h2>

            {loading ? <p>Cargando...</p> : (
                <div className="grid-1col">
                    {Object.entries(groupedSettings).map(([category, items]) => (
                        items.length > 0 && (
                            <div key={category} className="card">
                                <div className="card-header">{category}</div>
                                <div className="flex-col gap-4">
                                    {items.map(s => (
                                        <div key={s.key} className="flex-col gap-2">
                                            <label className="form-label font-medium">
                                                {s.description || s.key}
                                            </label>
                                            <div className="flex-row gap-2">
                                                <input
                                                    defaultValue={s.value}
                                                    id={`input-${s.key}`}
                                                    className="flex-1"
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
                                <div className="flex-row gap-2 flex-wrap">
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
                                    <div className="flex-row gap-2">
                                        <input
                                            type="file"
                                            accept=".sql"
                                            onChange={(e) => setImportFile(e.target.files?.[0] || null)}
                                            className="text-xs max-w-220"
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
                                    <div className="card p-3 border-primary-highlight">
                                        <h4 className="text-md font-semibold mb-2">
                                            Estado de la Base de Datos
                                        </h4>
                                        <div className="text-xs grid-1col gap-1">
                                            <p><strong>Database:</strong> {testResult.database}</p>
                                            <p><strong>Conexión:</strong> {testResult.connection}</p>
                                            <p><strong>Tablas:</strong> {testResult.tables_count}</p>
                                            <p><strong>Tamaño:</strong> {testResult.size_mb} MB</p>
                                            <details className="mt-2">
                                                <summary className="cursor-pointer font-medium">
                                                    Ver registros por tabla
                                                </summary>
                                                <div className="mt-2 pl-3">
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
                                        <h4 className="text-md font-semibold mb-2">
                                            Backups Disponibles
                                        </h4>
                                        <div className="max-h-300">
                                            {backups.map((backup) => (
                                                <div
                                                    key={backup.filename}
                                                    className="flex-row space-between backup-item"
                                                >
                                                    <div>
                                                        <p className="font-medium">{backup.filename}</p>
                                                        <p className="text-gray">
                                                            {new Date(backup.created_at).toLocaleString()} - {backup.size_mb} MB
                                                        </p>
                                                    </div>
                                                    <button
                                                        className="danger text-xs p-1"
                                                        onClick={() => handleRestore(backup.filename)}
                                                        disabled={operationLoading}
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

                    {/* Gestión de Usuarios de Django - Solo Admin */}
                    {role === 'admin' && (
                        <div className="card">
                            <div className="card-header">
                                <Users size={18} /> Usuarios de Django
                            </div>
                            <div className="flex-col gap-4">
                                <div className="flex-row gap-2 flex-end">
                                    <button
                                        className="primary"
                                        onClick={() => setShowUserModal(true)}
                                    >
                                        <Plus size={16} /> Crear Usuario
                                    </button>
                                </div>

                                {users.length > 0 ? (
                                    <div className="max-h-300">
                                        {users.map((user) => (
                                            <div
                                                key={user.id}
                                                className="flex-row space-between backup-item"
                                            >
                                                <div>
                                                    <p className="font-medium">{user.username}</p>
                                                    <p className="text-gray text-xs">
                                                        {user.email || 'Sin email'} •
                                                        {user.is_superuser ? ' Superuser' : user.is_staff ? ' Staff' : ' Usuario'}
                                                        {user.is_active ? '' : ' (Inactivo)'}
                                                    </p>
                                                </div>
                                                <div className="flex-row gap-2">
                                                    <button
                                                        className="secondary text-xs p-1"
                                                        onClick={() => {
                                                            setSelectedUser(user);
                                                            setShowPasswordModal(true);
                                                        }}
                                                        title="Cambiar contraseña"
                                                    >
                                                        <Key size={14} />
                                                    </button>
                                                    <button
                                                        className="danger text-xs p-1"
                                                        onClick={() => handleDeleteUser(user.id)}
                                                        title="Eliminar usuario"
                                                    >
                                                        <Trash2 size={14} />
                                                    </button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-muted">No hay usuarios disponibles.</p>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Modal: Crear Usuario */}
            {showUserModal && (
                <div className="modal-overlay" onClick={() => setShowUserModal(false)}>
                    <div className="modal-dialog max-w-700" onClick={(e) => e.stopPropagation()}>
                        <div className="card">
                            <div className="card-header">
                                <Plus size={18} /> Crear Nuevo Usuario
                            </div>
                            <div className="flex-col gap-4">
                                <div className="flex-col gap-2">
                                    <label className="form-label">Username *</label>
                                    <input
                                        className="w-full"
                                        value={newUser.username}
                                        onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                                        placeholder="Nombre de usuario"
                                    />
                                </div>
                                <div className="flex-col gap-2">
                                    <label className="form-label">Password *</label>
                                    <input
                                        type="password"
                                        className="w-full"
                                        value={newUser.password}
                                        onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                                        placeholder="Contraseña"
                                    />
                                </div>
                                <div className="flex-col gap-2">
                                    <label className="form-label">Email</label>
                                    <input
                                        type="email"
                                        className="w-full"
                                        value={newUser.email}
                                        onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                                        placeholder="correo@ejemplo.com"
                                    />
                                </div>
                                <div className="flex-row gap-4">
                                    <div className="flex-col gap-2 flex-1">
                                        <label className="form-label">Nombre</label>
                                        <input
                                            className="w-full"
                                            value={newUser.first_name}
                                            onChange={(e) => setNewUser({ ...newUser, first_name: e.target.value })}
                                            placeholder="Nombre"
                                        />
                                    </div>
                                    <div className="flex-col gap-2 flex-1">
                                        <label className="form-label">Apellido</label>
                                        <input
                                            className="w-full"
                                            value={newUser.last_name}
                                            onChange={(e) => setNewUser({ ...newUser, last_name: e.target.value })}
                                            placeholder="Apellido"
                                        />
                                    </div>
                                </div>
                                <div className="flex-col gap-2">
                                    <label className="flex-row gap-2">
                                        <input
                                            type="checkbox"
                                            checked={newUser.is_staff}
                                            onChange={(e) => setNewUser({ ...newUser, is_staff: e.target.checked })}
                                        />
                                        <span className="form-label">Staff (acceso al admin de Django)</span>
                                    </label>
                                    <label className="flex-row gap-2">
                                        <input
                                            type="checkbox"
                                            checked={newUser.is_superuser}
                                            onChange={(e) => setNewUser({ ...newUser, is_superuser: e.target.checked })}
                                        />
                                        <span className="form-label">Superuser (todos los permisos)</span>
                                    </label>
                                </div>
                                <div className="flex-row gap-2 flex-end border-t pt-4">
                                    <button className="secondary" onClick={() => setShowUserModal(false)}>
                                        Cancelar
                                    </button>
                                    <button className="primary" onClick={handleCreateUser}>
                                        <Plus size={16} /> Crear Usuario
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Modal: Cambiar Contraseña */}
            {showPasswordModal && selectedUser && (
                <div className="modal-overlay" onClick={() => setShowPasswordModal(false)}>
                    <div className="modal-dialog max-w-700" onClick={(e) => e.stopPropagation()}>
                        <div className="card">
                            <div className="card-header">
                                <Key size={18} /> Cambiar Contraseña - {selectedUser.username}
                            </div>
                            <div className="flex-col gap-4">
                                <div className="flex-col gap-2">
                                    <label className="form-label">Nueva Contraseña *</label>
                                    <input
                                        type="password"
                                        className="w-full"
                                        value={newPassword}
                                        onChange={(e) => setNewPassword(e.target.value)}
                                        placeholder="Ingrese nueva contraseña"
                                    />
                                </div>
                                <div className="flex-row gap-2 flex-end border-t pt-4">
                                    <button className="secondary" onClick={() => setShowPasswordModal(false)}>
                                        Cancelar
                                    </button>
                                    <button className="primary" onClick={handleChangePassword}>
                                        <Key size={16} /> Cambiar Contraseña
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
