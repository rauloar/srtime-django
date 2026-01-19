import React, { useEffect, useState } from 'react';
import { Plus, Trash2, Shield, User, Key } from 'lucide-react';
import { getAuthUsers, deleteAuthUser, updateAuthUserPassword, type AuthUser } from '../../api';

export const Users: React.FC = () => {
    const [users, setUsers] = useState<AuthUser[]>([]);
    const [loading, setLoading] = useState(true);
    const [passwordModalUser, setPasswordModalUser] = useState<AuthUser | null>(null);
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [savingPassword, setSavingPassword] = useState(false);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const data = await getAuthUsers();
            setUsers(data);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleDelete = async (user: AuthUser) => {
        if (!confirm(`¿Eliminar usuario ${user.username}?`)) return;
        try {
            await deleteAuthUser(user.id);
            fetchUsers();
        } catch (error) {
            alert('Error al eliminar usuario');
        }
    };

    const openPasswordModal = (user: AuthUser) => {
        setPasswordModalUser(user);
        setNewPassword('');
        setConfirmPassword('');
    };

    const closePasswordModal = () => {
        setPasswordModalUser(null);
        setNewPassword('');
        setConfirmPassword('');
        setSavingPassword(false);
    };

    const handleSavePassword = async () => {
        if (!passwordModalUser) return;
        if (!newPassword.trim() || newPassword.trim().length < 4) {
            alert('La contraseña debe tener al menos 4 caracteres.');
            return;
        }
        if (newPassword !== confirmPassword) {
            alert('Las contraseñas no coinciden.');
            return;
        }
        setSavingPassword(true);
        try {
            await updateAuthUserPassword(passwordModalUser.id, newPassword.trim());
            alert('Contraseña actualizada correctamente');
            closePasswordModal();
        } catch (error) {
            console.error(error);
            alert('Error al actualizar la contraseña');
            setSavingPassword(false);
        }
    };

    return (
        <div className="flex-col gap-4">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ fontSize: '20px', fontWeight: 600 }}>Usuarios de Aplicación</h2>
                <button className="primary flex-row gap-2" title="Agregar Usuario">
                    <Plus size={14} /> Nuevo Usuario
                </button>
            </div>

            <div className="card" style={{ padding: '0' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                    <thead style={{ backgroundColor: '#f9fafc', color: '#5c6b77', textAlign: 'left' }}>
                        <tr>
                            <th style={{ padding: '10px 15px', borderBottom: '1px solid var(--border-color)' }}>ID</th>
                            <th style={{ padding: '10px 15px', borderBottom: '1px solid var(--border-color)' }}>Usuario</th>
                            <th style={{ padding: '10px 15px', borderBottom: '1px solid var(--border-color)' }}>Rol</th>
                            <th style={{ padding: '10px 15px', borderBottom: '1px solid var(--border-color)' }}>Estado</th>
                            <th style={{ padding: '10px 15px', borderBottom: '1px solid var(--border-color)', textAlign: 'right' }}>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? <tr><td colSpan={5} style={{ padding: '20px', textAlign: 'center' }}>Cargando...</td></tr> :
                            users.length === 0 ? <tr><td colSpan={5} style={{ padding: '20px', textAlign: 'center' }}>No hay usuarios definidos.</td></tr> :
                                users.map(user => (
                                    <tr key={user.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                                        <td style={{ padding: '10px 15px' }}>{user.id}</td>
                                        <td style={{ padding: '10px 15px', fontWeight: 500, display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <User size={16} color="#888" /> {user.username}
                                        </td>
                                        <td style={{ padding: '10px 15px' }}>
                                            {user.role === 'admin' ?
                                                <span className="status-badge status-ok"><Shield size={10} style={{ marginRight: 4 }} /> Admin</span> :
                                                <span className="status-badge">{user.role}</span>
                                            }
                                        </td>
                                        <td style={{ padding: '10px 15px' }}>
                                            <span style={{ color: user.active ? 'var(--status-ok)' : 'var(--status-error)' }}>
                                                {user.active ? 'Activo' : 'Inactivo'}
                                            </span>
                                        </td>
                                        <td style={{ padding: '10px 15px', textAlign: 'right' }}>
                                            <button
                                                style={{ padding: '4px', color: 'var(--text-muted)', background: 'none', border: 'none', cursor: 'pointer', marginRight: '8px' }}
                                                title="Cambiar contraseña"
                                                onClick={() => openPasswordModal(user)}
                                            >
                                                <Key size={14} />
                                            </button>
                                            <button style={{ padding: '4px', color: 'var(--status-error)', background: 'none', border: 'none', cursor: 'pointer' }} onClick={() => handleDelete(user)}>
                                                <Trash2 size={14} />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                    </tbody>
                </table>
            </div>

            {passwordModalUser && (
                <div className="modal-backdrop" style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999 }}>
                    <div className="card" style={{ width: '400px', padding: '20px', background: 'var(--card-bg)', color: 'var(--text-primary)', boxShadow: '0 10px 30px rgba(0,0,0,0.3)' }}>
                        <h3 style={{ marginBottom: '12px' }}>Cambiar contraseña</h3>
                        <p style={{ marginTop: 0, marginBottom: '12px', color: 'var(--text-muted)' }}>Usuario: <strong>{passwordModalUser.username}</strong></p>
                        <div className="auth-field" style={{ marginBottom: '12px' }}>
                            <label>Nueva contraseña</label>
                            <input
                                type="password"
                                className="auth-input"
                                value={newPassword}
                                onChange={e => setNewPassword(e.target.value)}
                                placeholder="••••••"
                                disabled={savingPassword}
                            />
                        </div>
                        <div className="auth-field" style={{ marginBottom: '12px' }}>
                            <label>Confirmar contraseña</label>
                            <input
                                type="password"
                                className="auth-input"
                                value={confirmPassword}
                                onChange={e => setConfirmPassword(e.target.value)}
                                placeholder="••••••"
                                disabled={savingPassword}
                            />
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                            <button className="secondary" onClick={closePasswordModal} disabled={savingPassword}>Cancelar</button>
                            <button className="primary" onClick={handleSavePassword} disabled={savingPassword}>
                                {savingPassword ? 'Guardando...' : 'Guardar'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};
