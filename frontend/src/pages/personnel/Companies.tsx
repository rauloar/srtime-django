import React, { useEffect, useState } from 'react';
import { Building2, Plus, Edit2, Trash2 } from 'lucide-react';
import { getCompanies, createCompany, updateCompany, deleteCompany, getDepartments, updateDepartment, type Company } from '../../api';
import { DataGrid, type Column } from '../../components/ui/DataGrid';
import { PageToolbar } from '../../components/ui/PageToolbar';
import { CompanyModal } from '../../components/personnel/CompanyModal';
import { sortDepartmentsTree, type DepartmentNode } from '../../utils/treeUtils';
import { useToast } from '../../hooks/useToast';

export const Companies: React.FC = () => {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [departments, setDepartments] = useState<DepartmentNode[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [editingCompany, setEditingCompany] = useState<Company | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const { error: showError } = useToast();

    const fetchData = async () => {
        setLoading(true);
        try {
            const [companiesList, depts] = await Promise.all([
                getCompanies(),
                getDepartments()
            ]);
            setCompanies(companiesList);
            setDepartments(sortDepartmentsTree(depts));
        } catch (error) {
            showError('No se pudieron cargar datos');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const getDepartmentCount = (companyId: number) => {
        return departments.filter(d => d.company === companyId).length;
    };

    const handleSave = async (company: Company, deptIds: number[]) => {
        try {
            let savedCompany: Company;
            if (company.id) {
                savedCompany = await updateCompany(company.id, company);
            } else {
                savedCompany = await createCompany(company);
            }

            if (savedCompany.id) {
                const currentDepts = departments.filter(d => d.company === savedCompany.id);
                const currentDeptIds = currentDepts.map(d => d.id!);
                const toUnassign = currentDeptIds.filter(id => !deptIds.includes(id));
                const toAssign = deptIds.filter(id => !currentDeptIds.includes(id));

                const updates = [
                    ...toUnassign.map(id => {
                        const dept = departments.find(d => d.id === id);
                        return updateDepartment(id, { name: dept!.name, company: undefined });
                    }),
                    ...toAssign.map(id => {
                        const dept = departments.find(d => d.id === id);
                        return updateDepartment(id, { name: dept!.name, company: savedCompany.id });
                    })
                ];
                await Promise.all(updates);
            }

            setIsModalOpen(false);
            fetchData();
        } catch (error: any) {
            showError(error.message || 'Error al guardar empresa');
        }
    };

    const handleDelete = async (id: number) => {
        const deptCount = getDepartmentCount(id);
        if (deptCount > 0) {
            alert(`No se puede eliminar: La empresa tiene ${deptCount} departamentos asociados.`);
            return;
        }
        if (!confirm('¿Está seguro de eliminar esta empresa?')) return;

        try {
            await deleteCompany(id);
            fetchData();
        } catch (error: any) {
            showError('Error al eliminar empresa');
        }
    };

    const columns: Column<Company>[] = [
        {
            field: 'name',
            header: 'Nombre',
            render: (company) => (
                <div className="flex-row gap-2">
                    <Building2 size={16} color="var(--primary)" />
                    <span className="font-medium">{company.name}</span>
                </div>
            )
        },
        {
            field: 'code',
            header: 'Código',
            width: '120px',
            render: (c) => c.code || '-'
        },
        {
            field: 'address',
            header: 'Dirección',
            render: (c) => c.address || '-'
        },
        {
            field: 'website',
            header: 'Web',
            width: '180px',
            render: (c) => c.website ? (
                <a href={c.website} target="_blank" rel="noopener noreferrer" className="text-link">
                    {c.website}
                </a>
            ) : '-'
        },
        {
            field: 'departments',
            header: 'Departamentos',
            width: '130px',
            align: 'center',
            render: (company) => {
                const count = getDepartmentCount(company.id!);
                return (
                    <span className="badge" style={{
                        background: count > 0 ? 'var(--info-bg)' : 'var(--border)',
                        color: count > 0 ? 'var(--info)' : 'var(--text-muted)'
                    }}>
                        {count}
                    </span>
                );
            }
        },
        {
            field: 'actions',
            header: 'Acciones',
            align: 'right',
            width: '100px',
            render: (company) => (
                <div className="flex-row gap-2 flex-end">
                    <button
                        className="icon-btn"
                        onClick={(e) => {
                            e.stopPropagation();
                            setEditingCompany(company);
                            setIsModalOpen(true);
                        }}
                        title="Editar"
                    >
                        <Edit2 size={16} />
                    </button>
                    <button
                        className="icon-btn danger"
                        onClick={(e) => {
                            e.stopPropagation();
                            company.id && handleDelete(company.id);
                        }}
                        title="Eliminar"
                    >
                        <Trash2 size={16} />
                    </button>
                </div>
            )
        }
    ];

    const filteredCompanies = companies.filter(c =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (c.code && c.code.toLowerCase().includes(searchTerm.toLowerCase()))
    );

    return (
        <div className="w-full">
            <PageToolbar
                title="Empresas"
                subtitle="Gestión de empresas y organizaciones"
                onSearch={setSearchTerm}
                searchPlaceholder="Buscar empresa..."
                actions={
                    <button className="primary flex-row gap-2" onClick={() => {
                        setEditingCompany(null);
                        setIsModalOpen(true);
                    }}>
                        <Plus size={16} /> Nueva Empresa
                    </button>
                }
            />

            <div className="page-card">
                <DataGrid
                    columns={columns}
                    data={filteredCompanies}
                    loading={loading}
                    placeholder="No hay empresas definidas"
                />
            </div>

            {isModalOpen && (
                <CompanyModal
                    company={editingCompany}
                    departments={departments}
                    onClose={() => setIsModalOpen(false)}
                    onSave={handleSave}
                />
            )}
        </div>
    );
};
