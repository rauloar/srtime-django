import React, { useEffect, useMemo, useState } from 'react';
import { ChevronLeft, ChevronRight, ChevronsLeft, ChevronsRight } from 'lucide-react';

export interface Column<T> {
    field: keyof T | string;
    header: string;
    width?: string;
    render?: (row: T) => React.ReactNode;
    align?: 'left' | 'center' | 'right';
}

interface DataGridProps<T> {
    columns: Column<T>[];
    data: T[];
    loading?: boolean;
    onRowClick?: (row: T) => void;
    selectable?: boolean;
    onSelectionChange?: (selected: T[]) => void;
    placeholder?: string;
    pageSize?: number;
}

export function DataGrid<T extends { id?: number | string }>({
    columns,
    data,
    loading = false,
    onRowClick,
    placeholder = "No data available",
    pageSize = 15
}: DataGridProps<T>) {

    const [page, setPage] = useState(1);

    const totalPages = useMemo(() => {
        if (data.length === 0) return 1;
        return Math.max(1, Math.ceil(data.length / pageSize));
    }, [data.length, pageSize]);

    useEffect(() => {
        if (page > totalPages) {
            setPage(totalPages);
        }
        if (data.length === 0 && page !== 1) {
            setPage(1);
        }
    }, [data.length, page, totalPages]);

    const pageData = useMemo(() => {
        const start = (page - 1) * pageSize;
        const end = start + pageSize;
        return data.slice(start, end);
    }, [data, page, pageSize]);

    const startRecord = data.length === 0 ? 0 : (page - 1) * pageSize + 1;
    const endRecord = data.length === 0 ? 0 : Math.min(page * pageSize, data.length);

    return (
        <div className="zk-datagrid-container">
            <table className="zk-table">
                <thead>
                    <tr>
                        {columns.map((col, index) => (
                            <th key={index} style={{ width: col.width, textAlign: col.align || 'left' }}>
                                {col.header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {loading ? (
                        <tr>
                            <td colSpan={columns.length} className="loading-cell">
                                <div className="loading-spinner"></div>
                                Loading data...
                            </td>
                        </tr>
                    ) : data.length === 0 ? (
                        <tr>
                            <td colSpan={columns.length} className="empty-cell">
                                {placeholder}
                            </td>
                        </tr>
                    ) : (
                        pageData.map((row, rowIndex) => (
                            <tr
                                key={row.id || rowIndex}
                                onClick={() => onRowClick && onRowClick(row)}
                                className={onRowClick ? 'clickable-row' : ''}
                            >
                                {columns.map((col, colIndex) => (
                                    <td key={colIndex} style={{ textAlign: col.align || 'left' }}>
                                        {col.render ? col.render(row) : (row as any)[col.field]}
                                    </td>
                                ))}
                            </tr>
                        ))
                    )}
                </tbody>
            </table>

            {/* Pagination Placeholder - mimicking ZK's bottom bar */}
            {!loading && data.length > 0 && (
                <div className="zk-pagination">
                    <div className="page-info">
                        Showing {startRecord}-{endRecord} of {data.length}
                    </div>
                    <div className="page-controls">
                        <button
                            className="icon-btn"
                            onClick={() => setPage(1)}
                            disabled={page === 1}
                        ><ChevronsLeft size={16} /></button>
                        <button
                            className="icon-btn"
                            onClick={() => setPage(prev => Math.max(1, prev - 1))}
                            disabled={page === 1}
                        ><ChevronLeft size={16} /></button>
                        <span className="page-number">{page} / {totalPages}</span>
                        <button
                            className="icon-btn"
                            onClick={() => setPage(prev => Math.min(totalPages, prev + 1))}
                            disabled={page === totalPages}
                        ><ChevronRight size={16} /></button>
                        <button
                            className="icon-btn"
                            onClick={() => setPage(totalPages)}
                            disabled={page === totalPages}
                        ><ChevronsRight size={16} /></button>
                    </div>
                </div>
            )}
        </div>
    );
}
