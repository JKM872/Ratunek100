// ============================================================================
// REGISTER PAGE
// ============================================================================
//
// User registration with email/password/name
// Features:
// - Form validation
// - Password confirmation
// - Error handling
// - Loading states
// - Link to login page
// - Email verification message
//
// ============================================================================

import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { UserPlus, Mail, Lock, User, AlertCircle, Loader2, CheckCircle2 } from 'lucide-react';

export default function Register() {
  const navigate = useNavigate();
  const { signup, isAuthenticated, isLoading, error, clearError } = useAuthStore();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  
  const [validationErrors, setValidationErrors] = useState<{
    name?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});
  
  const [showSuccess, setShowSuccess] = useState(false);
  
  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !showSuccess) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, showSuccess, navigate]);
  
  // Clear errors on component mount
  useEffect(() => {
    clearError();
  }, [clearError]);
  
  // Validate form
  const validate = (): boolean => {
    const errors: {
      name?: string;
      email?: string;
      password?: string;
      confirmPassword?: string;
    } = {};
    
    if (!formData.name.trim()) {
      errors.name = 'Name is required';
    } else if (formData.name.trim().length < 2) {
      errors.name = 'Name must be at least 2 characters';
    }
    
    if (!formData.email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      errors.email = 'Invalid email address';
    }
    
    if (!formData.password) {
      errors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])/.test(formData.password)) {
      errors.password = 'Password must contain uppercase and lowercase letters';
    }
    
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };
  
  // Handle submit
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();
    
    if (!validate()) {
      return;
    }
    
    try {
      await signup(formData.email, formData.password, formData.name);
      
      // Show success message (email verification required)
      setShowSuccess(true);
      
      // Redirect after 5 seconds
      setTimeout(() => {
        navigate('/login');
      }, 5000);
      
    } catch (error) {
      // Error handled by authStore
      console.error('Signup error:', error);
    }
  };
  
  // Handle input change
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear validation error for this field
    if (validationErrors[name as keyof typeof validationErrors]) {
      setValidationErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };
  
  // Success message
  if (showSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
        <Card className="w-full max-w-md bg-white/10 backdrop-blur-lg border-white/20 shadow-2xl">
          <div className="p-8 text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500/20 rounded-full mb-4">
              <CheckCircle2 className="w-8 h-8 text-green-400" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-4">
              Registration Successful!
            </h2>
            <p className="text-gray-400 mb-6">
              We've sent a verification email to <strong className="text-white">{formData.email}</strong>.
              Please check your inbox and click the verification link to activate your account.
            </p>
            <p className="text-sm text-gray-500 mb-6">
              Redirecting to login page in 5 seconds...
            </p>
            <Button
              onClick={() => navigate('/login')}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white"
            >
              Go to Login
            </Button>
          </div>
        </Card>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 right-1/4 w-96 h-96 bg-green-500/10 rounded-full blur-3xl" />
        <div className="absolute bottom-1/4 left-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
      </div>
      
      {/* Register card */}
      <Card className="w-full max-w-md bg-white/10 backdrop-blur-lg border-white/20 shadow-2xl relative z-10">
        <div className="p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500/20 rounded-full mb-4">
              <UserPlus className="w-8 h-8 text-green-400" />
            </div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Create Account
            </h1>
            <p className="text-gray-400">
              Start analyzing sports betting opportunities
            </p>
          </div>
          
          {/* Error alert */}
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            </div>
          )}
          
          {/* Register form */}
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name field */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="name"
                  name="name"
                  type="text"
                  autoComplete="name"
                  value={formData.name}
                  onChange={handleChange}
                  disabled={isLoading}
                  className={`
                    w-full pl-11 pr-4 py-3 bg-white/5 border rounded-lg
                    text-white placeholder-gray-500
                    focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent
                    disabled:opacity-50 disabled:cursor-not-allowed
                    ${validationErrors.name ? 'border-red-500' : 'border-white/10'}
                  `}
                  placeholder="John Doe"
                />
              </div>
              {validationErrors.name && (
                <p className="mt-2 text-sm text-red-400">{validationErrors.name}</p>
              )}
            </div>
            
            {/* Email field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
                  disabled={isLoading}
                  className={`
                    w-full pl-11 pr-4 py-3 bg-white/5 border rounded-lg
                    text-white placeholder-gray-500
                    focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent
                    disabled:opacity-50 disabled:cursor-not-allowed
                    ${validationErrors.email ? 'border-red-500' : 'border-white/10'}
                  `}
                  placeholder="your@email.com"
                />
              </div>
              {validationErrors.email && (
                <p className="mt-2 text-sm text-red-400">{validationErrors.email}</p>
              )}
            </div>
            
            {/* Password field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  value={formData.password}
                  onChange={handleChange}
                  disabled={isLoading}
                  className={`
                    w-full pl-11 pr-4 py-3 bg-white/5 border rounded-lg
                    text-white placeholder-gray-500
                    focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent
                    disabled:opacity-50 disabled:cursor-not-allowed
                    ${validationErrors.password ? 'border-red-500' : 'border-white/10'}
                  `}
                  placeholder="••••••••"
                />
              </div>
              {validationErrors.password && (
                <p className="mt-2 text-sm text-red-400">{validationErrors.password}</p>
              )}
              <p className="mt-2 text-xs text-gray-500">
                At least 6 characters with uppercase and lowercase letters
              </p>
            </div>
            
            {/* Confirm password field */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  disabled={isLoading}
                  className={`
                    w-full pl-11 pr-4 py-3 bg-white/5 border rounded-lg
                    text-white placeholder-gray-500
                    focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent
                    disabled:opacity-50 disabled:cursor-not-allowed
                    ${validationErrors.confirmPassword ? 'border-red-500' : 'border-white/10'}
                  `}
                  placeholder="••••••••"
                />
              </div>
              {validationErrors.confirmPassword && (
                <p className="mt-2 text-sm text-red-400">{validationErrors.confirmPassword}</p>
              )}
            </div>
            
            {/* Submit button */}
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-medium py-3 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  Creating account...
                </>
              ) : (
                'Create Account'
              )}
            </Button>
          </form>
          
          {/* Login link */}
          <div className="mt-6 pt-6 border-t border-white/10 text-center">
            <p className="text-gray-400">
              Already have an account?{' '}
              <Link
                to="/login"
                className="text-green-400 hover:text-green-300 font-medium transition-colors"
              >
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
