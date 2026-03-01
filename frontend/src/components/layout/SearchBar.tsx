import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import { searchEmployees, type Employee } from '../../api';

export const SearchBar: React.FC = () => {
    const navigate = useNavigate();
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<Employee[]>([]);
    const [showResults, setShowResults] = useState(false);
    const [loading, setLoading] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Debounced search
    useEffect(() => {
        if (query.length < 2) {
            setResults([]);
            setShowResults(false);
            return;
        }

        const timer = setTimeout(async () => {
            try {
                setLoading(true);
                const employees = await searchEmployees(query);
                setResults(employees.slice(0, 5)); // Max 5 results
                setShowResults(true);
            } catch (err) {
                setResults([]);
            } finally {
                setLoading(false);
            }
        }, 300); // 300ms debounce

        return () => clearTimeout(timer);
    }, [query]);

    // Click outside to close
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(event.target as Node) &&
                inputRef.current &&
                !inputRef.current.contains(event.target as Node)
            ) {
                setShowResults(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSelectEmployee = (employee: Employee) => {
        if (!employee.id) return;
        // Navigate to employee's last 7 days
        const today = new Date().toISOString().split('T')[0];
        navigate(`/asistencia/empleado/${employee.id}/dia/${today}`);
        setQuery('');
        setShowResults(false);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && results.length > 0) {
            handleSelectEmployee(results[0]);
        }
        if (e.key === 'Escape') {
            setShowResults(false);
        }
    };

    return (
        <div style={{ position: 'relative', width: '100%', maxWidth: '400px' }}>
            <div style={{ position: 'relative' }}>
                <Search
                    size={18}
                    style={{
                        position: 'absolute',
                        left: '12px',
                        top: '50%',
                        transform: 'translateY(-50%)',
                        color: 'var(--text-muted)',
                        pointerEvents: 'none'
                    }}
                />
                <input
                    ref={inputRef}
                    type="text"
                    placeholder="Buscar empleado..."
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    onFocus={() => {
                        if (query.length >= 2) setShowResults(true);
                    }}
                    style={{
                        width: '100%',
                        padding: '10px 12px 10px 40px',
                        border: '1px solid var(--border-color)',
                        borderRadius: '6px',
                        fontSize: '14px',
                        background: 'var(--bg-main)',
                        color: 'var(--text-main)',
                        outline: 'none',
                        transition: 'border-color 0.2s'
                    }}
                    className="search-input"
                />
            </div>

            {/* Results Dropdown */}
            {showResults && (
                <div
                    ref={dropdownRef}
                    style={{
                        position: 'absolute',
                        top: 'calc(100% + 4px)',
                        left: 0,
                        right: 0,
                        background: 'var(--bg-main)',
                        border: '1px solid var(--border-color)',
                        borderRadius: '6px',
                        boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                        maxHeight: '300px',
                        overflowY: 'auto',
                        zIndex: 1000
                    }}
                >
                    {loading && (
                        <div style={{
                            padding: '16px',
                            textAlign: 'center',
                            color: 'var(--text-muted)',
                            fontSize: '14px'
                        }}>
                            Buscando...
                        </div>
                    )}

                    {!loading && results.length === 0 && query.length >= 2 && (
                        <div style={{
                            padding: '16px',
                            textAlign: 'center',
                            color: 'var(--text-muted)',
                            fontSize: '14px'
                        }}>
                            No se encontraron empleados
                        </div>
                    )}

                    {!loading && results.length > 0 && results.map((employee) => (
                        <div
                            key={employee.id ?? employee.user_id}
                            onClick={() => handleSelectEmployee(employee)}
                            style={{
                                padding: '12px 16px',
                                cursor: 'pointer',
                                borderBottom: '1px solid var(--border-color)',
                                transition: 'background 0.2s'
                            }}
                            className="search-result-item"
                        >
                            <div style={{ fontWeight: 500, marginBottom: '4px' }}>
                                {employee.name || employee.user_id}
                            </div>
                            <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                                {employee.user_id && `ID: ${employee.user_id}`}
                                {employee.department_name && ` • ${employee.department_name}`}
                            </div>
                        </div>
                    ))}
                </div>
            )}

            <style>{`
                .search-input:focus {
                    border-color: var(--primary-color);
                }
                .search-result-item:hover {
                    background-color: var(--sidebar-hover-bg);
                }
            `}</style>
        </div>
    );
};
