import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getDeviceUsers, type DeviceUser } from '../api';


const getRoleName = (privilege: number) => {
    switch (privilege) {
        case 0: return 'User';
        case 2: return 'Enroller';
        case 6: return 'Manager';
        case 14: return 'Administrator';
        default: return `Unknown (${privilege})`;
    }
};

export const Users: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [users, setUsers] = useState<DeviceUser[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string>('');

    useEffect(() => {
        if (!id) return;
        const fetchUsers = async () => {
            try {
                const data = await getDeviceUsers(Number(id));
                setUsers(data);
            } catch (e) {
                setError('Failed to load users');
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchUsers();
    }, [id]);

    if (loading) return <div>Loading users...</div>;
    if (error) return <div>{error}</div>;

    return (
        <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">Device {id} Users</h2>
            {users.length === 0 ? (
                <p>No users found for this device.</p>
            ) : (
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
                        <thead>
                            <tr style={{ borderBottom: '2px solid #30363d', textAlign: 'left' }}>
                                <th style={{ padding: '10px' }}>User ID</th>
                                <th style={{ padding: '10px' }}>UID</th>
                                <th style={{ padding: '10px' }}>Name</th>
                                <th style={{ padding: '10px' }}>Role</th>
                                <th style={{ padding: '10px' }}>Card</th>
                                <th style={{ padding: '10px' }}>Password</th>
                            </tr>
                        </thead>
                        <tbody>
                            {users.map((user) => (
                                <tr key={user.uid} style={{ borderBottom: '1px solid #30363d' }}>
                                    <td style={{ padding: '10px' }}>{user.user_id}</td>
                                    <td style={{ padding: '10px', color: '#8b949e' }}>{user.uid}</td>
                                    <td style={{ padding: '10px', fontWeight: 'bold' }}>{user.name}</td>
                                    <td style={{ padding: '10px' }}>
                                        <span className={`status-badge ${user.privilege === 14 ? 'status-error' : 'status-ok'}`}>
                                            {getRoleName(user.privilege || 0)}
                                        </span>
                                    </td>
                                    <td style={{ padding: '10px' }}>{user.card || '-'}</td>
                                    <td style={{ padding: '10px' }}>{user.password ? '******' : '-'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};
