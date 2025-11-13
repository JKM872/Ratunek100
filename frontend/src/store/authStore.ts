// ============================================================================
// AUTH STORE - Zustand State Management for Authentication
// ============================================================================
//
// Manages user authentication state with Supabase and local storage persistence
// Features:
// - Login/logout/signup
// - Session persistence
// - Token refresh
// - User preferences & subscription
//
// Usage:
//   import { useAuthStore } from '@/store/authStore';
//   
//   const { user, login, logout, isAuthenticated } = useAuthStore();
//
// ============================================================================

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import axios from 'axios';

// ============================================================================
// TYPES
// ============================================================================

interface User {
  id: string;
  email: string;
  name?: string;
  email_confirmed_at?: string;
  created_at?: string;
}

interface Preferences {
  email_notifications_enabled?: boolean;
  daily_email_time?: string;
  send_on_weekends?: boolean;
  preferred_sports?: string[];
  min_odds?: number;
  max_odds?: number;
  preferred_bookmakers?: string[];
  show_all_bookmakers?: boolean;
  only_qualifying_matches?: boolean;
  min_win_percentage?: number;
  language?: string;
  timezone?: string;
  subscription_type?: 'free' | 'premium' | 'pro';
}

interface Subscription {
  id?: string;
  user_id?: string;
  email?: string;
  is_active?: boolean;
  verified?: boolean;
  subscription_type?: 'free' | 'premium' | 'pro';
  daily_match_limit?: number;
  stripe_customer_id?: string;
  stripe_subscription_id?: string;
  current_period_start?: string;
  current_period_end?: string;
  expires_at?: string;
  cancel_at_period_end?: boolean;
  created_at?: string;
}

interface AuthState {
  // State
  user: User | null;
  preferences: Preferences | null;
  subscription: Subscription | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name?: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  updatePreferences: (preferences: Partial<Preferences>) => Promise<void>;
  updateSubscription: (subscription_type: 'free' | 'premium' | 'pro') => Promise<void>;
  clearError: () => void;
  
  // Helpers
  isPremiumUser: () => boolean;
  getDailyMatchLimit: () => number;
}

// ============================================================================
// AXIOS INSTANCE
// ============================================================================

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors (token expired)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - logout
      useAuthStore.getState().logout();
    }
    return Promise.reject(error);
  }
);

// ============================================================================
// ZUSTAND STORE
// ============================================================================

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      preferences: null,
      subscription: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,
      
      // ========================================================================
      // LOGIN
      // ========================================================================
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await axios.post('/api/auth/login', {
            email,
            password,
          });
          
          const { user, session } = response.data;
          
          set({
            user,
            token: session.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          
          // Fetch preferences and subscription
          await get().checkAuth();
          
        } catch (error: any) {
          const errorMessage = error.response?.data?.error || 'Login failed';
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: errorMessage,
          });
          throw new Error(errorMessage);
        }
      },
      
      // ========================================================================
      // SIGNUP
      // ========================================================================
      signup: async (email: string, password: string, name?: string) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await axios.post('/api/auth/signup', {
            email,
            password,
            name,
          });
          
          const { user, session } = response.data;
          
          set({
            user,
            token: session?.access_token || null,
            isAuthenticated: !!session,
            isLoading: false,
            error: null,
          });
          
          // If session available (email confirmation disabled), fetch data
          if (session) {
            await get().checkAuth();
          }
          
        } catch (error: any) {
          const errorMessage = error.response?.data?.error || 'Signup failed';
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: errorMessage,
          });
          throw new Error(errorMessage);
        }
      },
      
      // ========================================================================
      // LOGOUT
      // ========================================================================
      logout: async () => {
        const token = get().token;
        
        if (token) {
          try {
            await api.post('/auth/logout');
          } catch (error) {
            console.warn('Logout request failed:', error);
          }
        }
        
        // Clear state
        set({
          user: null,
          preferences: null,
          subscription: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },
      
      // ========================================================================
      // CHECK AUTH (Fetch user data with token)
      // ========================================================================
      checkAuth: async () => {
        const token = get().token;
        
        if (!token) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
          });
          return;
        }
        
        set({ isLoading: true });
        
        try {
          const response = await api.get('/auth/user');
          
          const { user, preferences, subscription } = response.data;
          
          set({
            user,
            preferences,
            subscription,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          
        } catch (error: any) {
          console.error('Auth check failed:', error);
          
          // Token invalid - logout
          set({
            user: null,
            preferences: null,
            subscription: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },
      
      // ========================================================================
      // UPDATE PREFERENCES
      // ========================================================================
      updatePreferences: async (updates: Partial<Preferences>) => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await api.put('/preferences', updates);
          
          const { preferences } = response.data;
          
          set({
            preferences,
            isLoading: false,
            error: null,
          });
          
        } catch (error: any) {
          const errorMessage = error.response?.data?.error || 'Failed to update preferences';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw new Error(errorMessage);
        }
      },
      
      // ========================================================================
      // UPDATE SUBSCRIPTION
      // ========================================================================
      updateSubscription: async (subscription_type: 'free' | 'premium' | 'pro') => {
        set({ isLoading: true, error: null });
        
        try {
          const response = await api.post('/subscription', {
            email: get().user?.email,
            subscription_type,
          });
          
          const { subscription } = response.data;
          
          set({
            subscription,
            preferences: {
              ...get().preferences,
              subscription_type,
            },
            isLoading: false,
            error: null,
          });
          
        } catch (error: any) {
          const errorMessage = error.response?.data?.error || 'Failed to update subscription';
          set({
            isLoading: false,
            error: errorMessage,
          });
          throw new Error(errorMessage);
        }
      },
      
      // ========================================================================
      // CLEAR ERROR
      // ========================================================================
      clearError: () => {
        set({ error: null });
      },
      
      // ========================================================================
      // HELPERS
      // ========================================================================
      
      isPremiumUser: () => {
        const subscription = get().subscription;
        return subscription?.subscription_type === 'premium' || subscription?.subscription_type === 'pro';
      },
      
      getDailyMatchLimit: () => {
        const subscription = get().subscription;
        return subscription?.daily_match_limit || 10;
      },
      
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      // Only persist essential auth data
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

// ============================================================================
// EXPORTS
// ============================================================================

export default useAuthStore;
