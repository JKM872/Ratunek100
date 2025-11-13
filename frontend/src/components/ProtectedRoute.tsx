// ============================================================================
// PROTECTED ROUTE COMPONENT
// ============================================================================
//
// HOC (Higher-Order Component) that wraps routes requiring authentication
// Redirects to /login if user is not authenticated
//
// Usage:
//   <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
//
// ============================================================================

import { ReactNode, useEffect } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children: ReactNode;
}

export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const location = useLocation();
  
  // Check authentication on mount
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);
  
  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-blue-500 mx-auto mb-4" />
          <p className="text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }
  
  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    // Save intended destination
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  // Render protected content
  return <>{children}</>;
}
