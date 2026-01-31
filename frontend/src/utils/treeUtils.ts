import type { Department } from '../api';

export interface DepartmentNode extends Department {
    level: number;
    path: string;
    children?: DepartmentNode[];
}

/**
 * Sorts departments into a flat list respecting hierarchy (Parent -> Children).
 * Adds 'level' and 'path' properties for display.
 */
export const sortDepartmentsTree = (allDepts: Department[]): DepartmentNode[] => {
    const result: DepartmentNode[] = [];

    // Map for easy lookup
    const deptMap = new Map<number, DepartmentNode>();
    allDepts.forEach(d => {
        deptMap.set(d.id!, { ...d, level: 0, path: d.name, children: [] });
    });

    // Build Tree Structure
    const roots: DepartmentNode[] = [];
    deptMap.forEach(node => {
        if (node.parent_id && deptMap.has(node.parent_id)) {
            const parent = deptMap.get(node.parent_id)!;
            parent.children?.push(node);
        } else {
            roots.push(node);
        }
    });

    // Recursive Flatten
    const traverse = (nodes: DepartmentNode[], level: number, parentPath: string) => {
        // Sort siblings by name
        nodes.sort((a, b) => a.name.localeCompare(b.name));

        nodes.forEach(node => {
            node.level = level;
            node.path = parentPath ? `${parentPath} > ${node.name}` : node.name;
            result.push(node);
            if (node.children && node.children.length > 0) {
                traverse(node.children, level + 1, node.path);
            }
        });
    };

    traverse(roots, 0, '');
    return result;
};
