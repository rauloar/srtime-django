import React from 'react';

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
    getRowId?: (row: T, index: number) => string | number;
}

export function DataGrid<T = any>({
    columns,
    data,
    loading = false,
    onRowClick,
    placeholder = "No data available",
    getRowId
}: DataGridProps<T>) {
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
                        data.map((row, rowIndex) => {
                            const rowKey = getRowId 
                                ? getRowId(row, rowIndex)
                                : (row as any).id || rowIndex;
                            
                            return (
                                <tr
                                    key={rowKey}
                                    onClick={() => onRowClick && onRowClick(row)}
                                    className={onRowClick ? 'clickable-row' : ''}
                                >
                                    {columns.map((col, colIndex) => (
                                        <td key={colIndex} style={{ textAlign: col.align || 'left' }}>
                                            {col.render ? col.render(row) : (row as any)[col.field]}
                                        </td>
                                    ))}
                                </tr>
                            );
                        })
                    )}
                </tbody>
            </table>
        </div>
    );
}
