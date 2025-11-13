// ============================================================================
// SETTINGS PAGE
// ============================================================================
//
// User settings & preferences management
// Sections:
// 1. Email Notifications (enable/disable, delivery time, weekends)
// 2. Sport Preferences (checkboxes for sports, odds range)
// 3. Bookmaker Preferences (Fortuna/Superbet/STS)
// 4. Account (change email, change password, delete account)
// 5. Subscription (current plan, upgrade/downgrade)
//
// ============================================================================

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Settings as SettingsIcon,
  Bell,
  Trophy,
  DollarSign,
  User,
  Mail,
  Lock,
  Save,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Trash2,
} from 'lucide-react';

export default function Settings() {
  const {
    user,
    preferences: initialPreferences,
    subscription,
    updatePreferences,
    isLoading,
    error,
    clearError,
  } = useAuthStore();
  
  const [preferences, setPreferences] = useState(initialPreferences || {});
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  const [activeTab, setActiveTab] = useState<'notifications' | 'sports' | 'bookmakers' | 'account' | 'subscription'>('notifications');
  
  // Update local state when preferences change
  useEffect(() => {
    if (initialPreferences) {
      setPreferences(initialPreferences);
    }
  }, [initialPreferences]);
  
  // Clear errors on mount
  useEffect(() => {
    clearError();
  }, [clearError]);
  
  // Handle save
  const handleSave = async () => {
    setSaveStatus('saving');
    clearError();
    
    try {
      await updatePreferences(preferences);
      setSaveStatus('success');
      
      // Reset success message after 3 seconds
      setTimeout(() => {
        setSaveStatus('idle');
      }, 3000);
      
    } catch (error) {
      setSaveStatus('error');
      console.error('Save preferences error:', error);
    }
  };
  
  // Handle checkbox change
  const handleCheckboxChange = (field: string, value: any) => {
    setPreferences(prev => ({
      ...prev,
      [field]: value,
    }));
  };
  
  // Handle array toggle (sports, bookmakers)
  const toggleArrayItem = (field: string, item: string) => {
    const array = preferences[field as keyof typeof preferences] as string[] || [];
    const newArray = array.includes(item)
      ? array.filter(i => i !== item)
      : [...array, item];
    
    setPreferences(prev => ({
      ...prev,
      [field]: newArray,
    }));
  };
  
  // Tabs
  const tabs = [
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'sports', label: 'Sports', icon: Trophy },
    { id: 'bookmakers', label: 'Bookmakers', icon: DollarSign },
    { id: 'account', label: 'Account', icon: User },
    { id: 'subscription', label: 'Subscription', icon: CheckCircle2 },
  ];
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <SettingsIcon className="w-8 h-8 text-blue-400" />
            <h1 className="text-3xl font-bold text-white">Settings</h1>
          </div>
          <p className="text-gray-400">
            Manage your preferences and account settings
          </p>
        </div>
        
        {/* Status messages */}
        {saveStatus === 'success' && (
          <div className="mb-6 p-4 bg-green-500/10 border border-green-500/30 rounded-lg flex items-center gap-3">
            <CheckCircle2 className="w-5 h-5 text-green-400" />
            <p className="text-green-400">Settings saved successfully!</p>
          </div>
        )}
        
        {(error || saveStatus === 'error') && (
          <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-400" />
            <p className="text-red-400">{error || 'Failed to save settings'}</p>
          </div>
        )}
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar tabs */}
          <Card className="lg:col-span-1 bg-white/5 backdrop-blur-lg border-white/10 p-4 h-fit">
            <nav className="space-y-2">
              {tabs.map(tab => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`
                      w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-colors
                      ${isActive
                        ? 'bg-blue-500/20 text-blue-400'
                        : 'text-gray-400 hover:bg-white/5 hover:text-white'
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </Card>
          
          {/* Content */}
          <Card className="lg:col-span-3 bg-white/5 backdrop-blur-lg border-white/10 p-6">
            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h2 className="text-xl font-bold text-white mb-4">Email Notifications</h2>
                
                {/* Enable notifications */}
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-white">Daily email notifications</p>
                    <p className="text-sm text-gray-400">Receive daily match recommendations</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={preferences.email_notifications_enabled || false}
                    onChange={(e) => handleCheckboxChange('email_notifications_enabled', e.target.checked)}
                    className="w-5 h-5 rounded accent-blue-500"
                  />
                </div>
                
                <hr className="border-white/10" />
                
                {/* Email time */}
                <div>
                  <label className="block font-medium text-white mb-2">
                    Delivery time
                  </label>
                  <input
                    type="time"
                    value={preferences.daily_email_time || '21:00:00'}
                    onChange={(e) => handleCheckboxChange('daily_email_time', e.target.value)}
                    disabled={!preferences.email_notifications_enabled}
                    className="px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white disabled:opacity-50"
                  />
                  <p className="mt-2 text-sm text-gray-400">
                    Default: 21:00 (9 PM)
                  </p>
                </div>
                
                <hr className="border-white/10" />
                
                {/* Send on weekends */}
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-white">Send on weekends</p>
                    <p className="text-sm text-gray-400">Receive emails on Saturday and Sunday</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={preferences.send_on_weekends !== false}
                    onChange={(e) => handleCheckboxChange('send_on_weekends', e.target.checked)}
                    disabled={!preferences.email_notifications_enabled}
                    className="w-5 h-5 rounded accent-blue-500 disabled:opacity-50"
                  />
                </div>
              </div>
            )}
            
            {/* Sports Tab */}
            {activeTab === 'sports' && (
              <div className="space-y-6">
                <h2 className="text-xl font-bold text-white mb-4">Sport Preferences</h2>
                
                {/* Sports checkboxes */}
                <div>
                  <p className="font-medium text-white mb-3">Select sports to track</p>
                  <div className="grid grid-cols-2 gap-3">
                    {['Football', 'Volleyball', 'Handball', 'Basketball', 'Rugby', 'Tennis'].map(sport => (
                      <label
                        key={sport}
                        className="flex items-center gap-2 px-4 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={(preferences.preferred_sports as string[] || []).includes(sport)}
                          onChange={() => toggleArrayItem('preferred_sports', sport)}
                          className="w-5 h-5 rounded accent-blue-500"
                        />
                        <span className="text-white">{sport}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                <hr className="border-white/10" />
                
                {/* Odds range */}
                <div>
                  <p className="font-medium text-white mb-3">Odds range</p>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Min odds</label>
                      <input
                        type="number"
                        step="0.01"
                        min="1.01"
                        max="100"
                        value={preferences.min_odds || 1.37}
                        onChange={(e) => handleCheckboxChange('min_odds', parseFloat(e.target.value))}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Max odds</label>
                      <input
                        type="number"
                        step="0.01"
                        min="1.01"
                        max="100"
                        value={preferences.max_odds || 10.00}
                        onChange={(e) => handleCheckboxChange('max_odds', parseFloat(e.target.value))}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-white"
                      />
                    </div>
                  </div>
                  <p className="mt-2 text-sm text-gray-400">
                    Only show matches with odds in this range
                  </p>
                </div>
                
                <hr className="border-white/10" />
                
                {/* Only qualifying matches */}
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-white">Only qualifying matches</p>
                    <p className="text-sm text-gray-400">Show only matches meeting quality criteria</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={preferences.only_qualifying_matches !== false}
                    onChange={(e) => handleCheckboxChange('only_qualifying_matches', e.target.checked)}
                    className="w-5 h-5 rounded accent-blue-500"
                  />
                </div>
              </div>
            )}
            
            {/* Bookmakers Tab */}
            {activeTab === 'bookmakers' && (
              <div className="space-y-6">
                <h2 className="text-xl font-bold text-white mb-4">Bookmaker Preferences</h2>
                
                {/* Polish bookmakers */}
                <div>
                  <p className="font-medium text-white mb-3">Polish bookmakers</p>
                  <div className="space-y-3">
                    {['Fortuna', 'Superbet', 'STS'].map(bookmaker => (
                      <label
                        key={bookmaker}
                        className="flex items-center gap-3 px-4 py-3 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 cursor-pointer"
                      >
                        <input
                          type="checkbox"
                          checked={(preferences.preferred_bookmakers as string[] || []).includes(bookmaker)}
                          onChange={() => toggleArrayItem('preferred_bookmakers', bookmaker)}
                          className="w-5 h-5 rounded accent-blue-500"
                        />
                        <span className="text-white font-medium">{bookmaker}</span>
                        <Badge className={
                          bookmaker === 'Fortuna' ? 'bg-red-500/20 text-red-400' :
                          bookmaker === 'Superbet' ? 'bg-blue-500/20 text-blue-400' :
                          'bg-green-500/20 text-green-400'
                        }>
                          {bookmaker === 'Fortuna' ? '🔴' : bookmaker === 'Superbet' ? '🔵' : '🟢'}
                        </Badge>
                      </label>
                    ))}
                  </div>
                </div>
                
                <hr className="border-white/10" />
                
                {/* Show all bookmakers */}
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-white">Show all bookmakers</p>
                    <p className="text-sm text-gray-400">Include international bookmakers (Bet365, Nordic, etc.)</p>
                  </div>
                  <input
                    type="checkbox"
                    checked={preferences.show_all_bookmakers || false}
                    onChange={(e) => handleCheckboxChange('show_all_bookmakers', e.target.checked)}
                    className="w-5 h-5 rounded accent-blue-500"
                  />
                </div>
              </div>
            )}
            
            {/* Account Tab */}
            {activeTab === 'account' && (
              <div className="space-y-6">
                <h2 className="text-xl font-bold text-white mb-4">Account</h2>
                
                {/* Email */}
                <div>
                  <label className="block font-medium text-white mb-2">
                    Email
                  </label>
                  <div className="flex items-center gap-3">
                    <input
                      type="email"
                      value={user?.email || ''}
                      disabled
                      className="flex-1 px-4 py-2 bg-white/5 border border-white/10 rounded-lg text-gray-400 cursor-not-allowed"
                    />
                    <Badge className="bg-green-500/20 text-green-400">
                      Verified
                    </Badge>
                  </div>
                </div>
                
                <hr className="border-white/10" />
                
                {/* Change password */}
                <div>
                  <p className="font-medium text-white mb-2">Password</p>
                  <Button className="bg-white/10 hover:bg-white/20 text-white">
                    <Lock className="w-4 h-4 mr-2" />
                    Change Password
                  </Button>
                </div>
                
                <hr className="border-white/10" />
                
                {/* Delete account */}
                <div>
                  <p className="font-medium text-white mb-2">Danger Zone</p>
                  <Button className="bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/30">
                    <Trash2 className="w-4 h-4 mr-2" />
                    Delete Account
                  </Button>
                  <p className="mt-2 text-sm text-gray-500">
                    This action cannot be undone. All your data will be permanently deleted.
                  </p>
                </div>
              </div>
            )}
            
            {/* Subscription Tab */}
            {activeTab === 'subscription' && (
              <div className="space-y-6">
                <h2 className="text-xl font-bold text-white mb-4">Subscription</h2>
                
                {/* Current plan */}
                <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-400">Current Plan</span>
                    <Badge className="bg-blue-500/20 text-blue-400 uppercase">
                      {subscription?.subscription_type || 'FREE'}
                    </Badge>
                  </div>
                  <p className="text-2xl font-bold text-white">
                    {subscription?.subscription_type === 'free' && '€0.00'}
                    {subscription?.subscription_type === 'premium' && '€4.99'}
                    {subscription?.subscription_type === 'pro' && '€9.99'}
                    <span className="text-sm text-gray-400 font-normal">/month</span>
                  </p>
                  <p className="text-sm text-gray-400 mt-1">
                    Daily limit: {subscription?.daily_match_limit === -1 ? 'Unlimited' : subscription?.daily_match_limit || 10} matches
                  </p>
                </div>
                
                {/* Plans */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { type: 'free', price: '€0.00', limit: 10, features: ['10 matches/day', 'Basic email', 'Limited support'] },
                    { type: 'premium', price: '€4.99', limit: 50, features: ['50 matches/day', 'Advanced filters', 'Email support'] },
                    { type: 'pro', price: '€9.99', limit: -1, features: ['Unlimited matches', 'Analytics', 'Priority support'] },
                  ].map(plan => (
                    <div
                      key={plan.type}
                      className={`
                        p-4 rounded-lg border
                        ${subscription?.subscription_type === plan.type
                          ? 'bg-blue-500/10 border-blue-500/30'
                          : 'bg-white/5 border-white/10'
                        }
                      `}
                    >
                      <h3 className="text-lg font-bold text-white uppercase mb-2">{plan.type}</h3>
                      <p className="text-2xl font-bold text-white mb-4">
                        {plan.price}
                        <span className="text-sm text-gray-400 font-normal">/mo</span>
                      </p>
                      <ul className="space-y-2 mb-4">
                        {plan.features.map(feature => (
                          <li key={feature} className="text-sm text-gray-400 flex items-center gap-2">
                            <CheckCircle2 className="w-4 h-4 text-green-400" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                      {subscription?.subscription_type !== plan.type && (
                        <Button className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                          Upgrade to {plan.type.toUpperCase()}
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Save button */}
            {activeTab !== 'account' && activeTab !== 'subscription' && (
              <div className="mt-8 pt-6 border-t border-white/10">
                <Button
                  onClick={handleSave}
                  disabled={isLoading || saveStatus === 'saving'}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-8"
                >
                  {saveStatus === 'saving' ? (
                    <>
                      <Loader2 className="w-5 h-5 animate-spin mr-2" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="w-5 h-5 mr-2" />
                      Save Changes
                    </>
                  )}
                </Button>
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  );
}
