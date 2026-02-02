// import { type ReactNode } from 'react';  // DEV: Unused in bypass mode
// import { Navigate } from 'react-router-dom';  // DEV: Unused in bypass mode
// import { useAuth } from '../../hooks/useAuth';  // DEV: Unused in bypass mode
import { type ReactNode } from 'react';

interface PrivateRouteProps {
    children: ReactNode;
}

export const PrivateRoute = ({ children }: PrivateRouteProps) => {
    // DEV BYPASS: ALWAYS ALLOW ACCESS
    return <>{children}</>;

    /* 
    if (import.meta.env.DEV) {
        return <>{children}</>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" replace />;
    }

    return <>{children}</>;
    */
};
