import React, { useState } from 'react';
import type { Company } from '../../api';
import type { DepartmentNode } from '../../utils/treeUtils';

interface CompanyModalProps {
    company: Company | null;
    departments: DepartmentNode[];
    onClose: () => void;
    onSave: (company: Company, deptIds: number[]) => Promise<void>;
}

export const CompanyModal: React.FC<CompanyModalProps> = ({ company, departments, onClose, onSave }) => {
    const [name, setName] = useState(company?.name || '');
    const [code, setCode] = useState(company?.code || '');
    const [address, setAddress] = useState(company?.address || '');
    const [website, setWebsite] = useState(company?.website || '');
    const [selectedDepts, setSelectedDepts] = useState<number[]>(
        company ? departments.filter(d => d.company === company.id).map(d => d.id!) : []
    );
    const [saving, setSaving] = useState(false);
    const [showDepts, setShowDepts] = useState(false);

    const toggleDept = (deptId: number) => {
        setSelectedDepts(prev =>
            prev.includes(deptId)
                ? prev.filter(id => id !== deptId)
                : [...prev, deptId]
        );
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="card modal-dialog" onClick={(e) => e.stopPropagation()}>
                <h3>{company ? 'Editar Empresa' : 'Nueva Empresa'}</h3>

                <div className="flex-col gap-4">
                    <div className="flex-col gap-2">
                        <label className="form-label">Nombre *</label>
                        <input
                            value={name}
                            onChange={e => setName(e.target.value)}
                            placeholder="Ej: Acme Corp"
                            autoFocus
                        />
                    </div>

                    <div className="flex-col gap-2">
                        <label className="form-label">Código</label>
                        <input
                            value={code}
                            onChange={e => setCode(e.target.value)}
                            placeholder="Ej: ACME"
                        />
                    </div>

                    <div className="flex-col gap-2">
                        <label className="form-label">Dirección</label>
                        <input
                            value={address}
                            onChange={e => setAddress(e.target.value)}
                            placeholder="Ej: Av. Siempre Viva 123"
                        />
                    </div>

                    <div className="flex-col gap-2">
                        <label className="form-label">Sitio Web</label>
                        <input
                            value={website}
                            onChange={e => setWebsite(e.target.value)}
                            placeholder="Ej: https://acmecorp.com"
                        />
                    </div>

                    <div className="flex-col gap-2 border-t pt-4">
                        <button
                            type="button"
                            className="flex-row gap-2 text-left"
                            onClick={() => setShowDepts(!showDepts)}
                        >
                            <span className="form-label font-semibold">
                                📁 Departamentos Asociados ({selectedDepts.length})
                            </span>
                            <span>{showDepts ? '▲' : '▼'}</span>
                        </button>

                        {showDepts && (
                            <div className="border p-2" style={{ maxHeight: '200px', overflowY: 'auto' }}>
                                {departments.length === 0 ? (
                                    <p className="text-muted text-xs">No hay departamentos disponibles</p>
                                ) : (
                                    departments.map(dept => (
                                        <label
                                            key={dept.id}
                                            className="flex-row gap-2"
                                            style={{ padding: '4px 0', cursor: 'pointer', paddingLeft: `${dept.level * 12}px` }}
                                        >
                                            <input
                                                type="checkbox"
                                                checked={selectedDepts.includes(dept.id!)}
                                                onChange={() => toggleDept(dept.id!)}
                                            />
                                            <span className="text-sm">{dept.name}</span>
                                        </label>
                                    ))
                                )}
                            </div>
                        )}
                        <small className="text-muted text-xxs">
                            Selecciona los departamentos que pertenecen a esta empresa
                        </small>
                    </div>

                    <div className="flex-row gap-2 mt-3 flex-end">
                        <button onClick={onClose} disabled={saving}>Cancelar</button>
                        <button
                            className="primary"
                            disabled={saving || !name.trim()}
                            onClick={async () => {
                                setSaving(true);
                                try {
                                    await onSave(
                                        { id: company?.id, name, code, address, website },
                                        selectedDepts
                                    );
                                } catch (error) {
                                    setSaving(false);
                                }
                            }}
                        >
                            {saving ? 'Guardando...' : 'Guardar'}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
