-- ============================================================================
-- SUPABASE AUTH SCHEMA for Sports Betting Analytics Platform
-- ============================================================================
-- 
-- This schema extends Supabase's built-in auth.users table with:
-- 1. User preferences (email notifications, sport filters, odds ranges)
-- 2. Email subscriptions (free/premium/pro tiers + Stripe integration)
-- 3. User activity logging (login, preferences changes, etc.)
--
-- Usage:
--   1. Go to Supabase Dashboard > SQL Editor
--   2. Paste this entire file
--   3. Click "Run"
--
-- Revenue Model:
--   FREE:    €0.00/month  - 10 matches/day, basic email
--   PREMIUM: €4.99/month  - 50 matches/day, advanced filters
--   PRO:     €9.99/month  - Unlimited, analytics, priority support
--
-- ============================================================================

-- ============================================================================
-- TABLE: user_preferences
-- ============================================================================
-- Stores user-specific settings for match filtering and email delivery

CREATE TABLE IF NOT EXISTS user_preferences (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key to Supabase Auth
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Email notification settings
    email_notifications_enabled BOOLEAN DEFAULT TRUE,
    daily_email_time TIME DEFAULT '21:00:00',  -- Default 9 PM
    send_on_weekends BOOLEAN DEFAULT TRUE,
    
    -- Sport preferences (array of sport names)
    preferred_sports TEXT[] DEFAULT ARRAY['Football', 'Volleyball', 'Handball'],
    
    -- Odds range filters
    min_odds DECIMAL(6,2) DEFAULT 1.37,
    max_odds DECIMAL(6,2) DEFAULT 10.00,
    
    -- Bookmaker preferences
    preferred_bookmakers TEXT[] DEFAULT ARRAY['Fortuna', 'Superbet', 'STS'],
    show_all_bookmakers BOOLEAN DEFAULT FALSE,  -- Show non-Polish bookmakers too
    
    -- Match filters
    only_qualifying_matches BOOLEAN DEFAULT TRUE,  -- Only matches that meet criteria
    min_win_percentage DECIMAL(5,2) DEFAULT 50.00,
    
    -- Localization
    language TEXT DEFAULT 'pl',  -- pl, en
    timezone TEXT DEFAULT 'Europe/Warsaw',
    
    -- Subscription info (denormalized for quick access)
    subscription_type TEXT DEFAULT 'free' CHECK (subscription_type IN ('free', 'premium', 'pro')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id)  -- One preference row per user
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_user_preferences_subscription_type ON user_preferences(subscription_type);

-- Comment
COMMENT ON TABLE user_preferences IS 'User-specific settings for match filtering and email notifications';

-- ============================================================================
-- TABLE: email_subscriptions
-- ============================================================================
-- Tracks email subscription status and Stripe billing

CREATE TABLE IF NOT EXISTS email_subscriptions (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign key
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Email
    email TEXT NOT NULL,
    
    -- Subscription status
    is_active BOOLEAN DEFAULT TRUE,
    verified BOOLEAN DEFAULT FALSE,
    verification_token TEXT,
    verification_sent_at TIMESTAMP WITH TIME ZONE,
    
    -- Subscription tier
    subscription_type TEXT DEFAULT 'free' CHECK (subscription_type IN ('free', 'premium', 'pro')),
    
    -- Stripe integration
    stripe_customer_id TEXT,  -- Stripe Customer ID (cus_...)
    stripe_subscription_id TEXT,  -- Stripe Subscription ID (sub_...)
    stripe_price_id TEXT,  -- Stripe Price ID (price_...)
    
    -- Billing
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,  -- For trial or cancellation
    
    -- Cancellation
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    cancellation_reason TEXT,
    
    -- Limits based on tier
    daily_match_limit INTEGER DEFAULT 10,  -- 10 for free, 50 for premium, unlimited (-1) for pro
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id),  -- One subscription per user
    UNIQUE(email)  -- One email per subscription
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_email_subscriptions_user_id ON email_subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_email_subscriptions_email ON email_subscriptions(email);
CREATE INDEX IF NOT EXISTS idx_email_subscriptions_stripe_customer ON email_subscriptions(stripe_customer_id);
CREATE INDEX IF NOT EXISTS idx_email_subscriptions_subscription_type ON email_subscriptions(subscription_type);
CREATE INDEX IF NOT EXISTS idx_email_subscriptions_is_active ON email_subscriptions(is_active);

-- Comment
COMMENT ON TABLE email_subscriptions IS 'Email subscription tracking with Stripe billing integration';

-- ============================================================================
-- TABLE: user_activity
-- ============================================================================
-- Logs user actions for analytics and debugging

CREATE TABLE IF NOT EXISTS user_activity (
    -- Primary key
    id BIGSERIAL PRIMARY KEY,
    
    -- Foreign key (nullable - can log anonymous actions)
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    
    -- Activity details
    action TEXT NOT NULL,  -- 'login', 'signup', 'update_preferences', 'view_matches', etc.
    details JSONB,  -- Flexible JSON for additional data
    
    -- Request metadata
    ip_address INET,
    user_agent TEXT,
    referer TEXT,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity(user_id);
CREATE INDEX IF NOT EXISTS idx_user_activity_action ON user_activity(action);
CREATE INDEX IF NOT EXISTS idx_user_activity_created_at ON user_activity(created_at DESC);

-- Partitioning hint (for large-scale apps)
COMMENT ON TABLE user_activity IS 'User action logs. Consider partitioning by created_at for production.';

-- ============================================================================
-- TABLE: subscription_history
-- ============================================================================
-- Tracks subscription changes over time (upgrades, downgrades, cancellations)

CREATE TABLE IF NOT EXISTS subscription_history (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign keys
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    subscription_id UUID REFERENCES email_subscriptions(id) ON DELETE SET NULL,
    
    -- Change details
    action TEXT NOT NULL CHECK (action IN ('created', 'upgraded', 'downgraded', 'canceled', 'renewed', 'expired')),
    old_subscription_type TEXT,
    new_subscription_type TEXT,
    
    -- Stripe event
    stripe_event_id TEXT,  -- evt_... from Stripe webhook
    
    -- Metadata
    reason TEXT,
    metadata JSONB,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_subscription_history_user_id ON subscription_history(user_id);
CREATE INDEX IF NOT EXISTS idx_subscription_history_created_at ON subscription_history(created_at DESC);

COMMENT ON TABLE subscription_history IS 'Historical log of subscription changes for analytics';

-- ============================================================================
-- TRIGGER: Update updated_at timestamp automatically
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to user_preferences
DROP TRIGGER IF EXISTS update_user_preferences_updated_at ON user_preferences;
CREATE TRIGGER update_user_preferences_updated_at
    BEFORE UPDATE ON user_preferences
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to email_subscriptions
DROP TRIGGER IF EXISTS update_email_subscriptions_updated_at ON email_subscriptions;
CREATE TRIGGER update_email_subscriptions_updated_at
    BEFORE UPDATE ON email_subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_activity ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_history ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- RLS POLICY: user_preferences
-- ============================================================================

-- Users can view their own preferences
DROP POLICY IF EXISTS "Users can view own preferences" ON user_preferences;
CREATE POLICY "Users can view own preferences"
    ON user_preferences FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own preferences
DROP POLICY IF EXISTS "Users can insert own preferences" ON user_preferences;
CREATE POLICY "Users can insert own preferences"
    ON user_preferences FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own preferences
DROP POLICY IF EXISTS "Users can update own preferences" ON user_preferences;
CREATE POLICY "Users can update own preferences"
    ON user_preferences FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own preferences
DROP POLICY IF EXISTS "Users can delete own preferences" ON user_preferences;
CREATE POLICY "Users can delete own preferences"
    ON user_preferences FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- RLS POLICY: email_subscriptions
-- ============================================================================

-- Users can view their own subscription
DROP POLICY IF EXISTS "Users can view own subscription" ON email_subscriptions;
CREATE POLICY "Users can view own subscription"
    ON email_subscriptions FOR SELECT
    USING (auth.uid() = user_id);

-- Users can insert their own subscription
DROP POLICY IF EXISTS "Users can insert own subscription" ON email_subscriptions;
CREATE POLICY "Users can insert own subscription"
    ON email_subscriptions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can update their own subscription
DROP POLICY IF EXISTS "Users can update own subscription" ON email_subscriptions;
CREATE POLICY "Users can update own subscription"
    ON email_subscriptions FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Users can delete their own subscription
DROP POLICY IF EXISTS "Users can delete own subscription" ON email_subscriptions;
CREATE POLICY "Users can delete own subscription"
    ON email_subscriptions FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- RLS POLICY: user_activity
-- ============================================================================

-- Users can view their own activity
DROP POLICY IF EXISTS "Users can view own activity" ON user_activity;
CREATE POLICY "Users can view own activity"
    ON user_activity FOR SELECT
    USING (auth.uid() = user_id);

-- Service role can insert any activity (for system logging)
DROP POLICY IF EXISTS "Service role can insert activity" ON user_activity;
CREATE POLICY "Service role can insert activity"
    ON user_activity FOR INSERT
    WITH CHECK (true);  -- Backend will use service role key

-- ============================================================================
-- RLS POLICY: subscription_history
-- ============================================================================

-- Users can view their own subscription history
DROP POLICY IF EXISTS "Users can view own history" ON subscription_history;
CREATE POLICY "Users can view own history"
    ON subscription_history FOR SELECT
    USING (auth.uid() = user_id);

-- Service role can insert history (for system logging)
DROP POLICY IF EXISTS "Service role can insert history" ON subscription_history;
CREATE POLICY "Service role can insert history"
    ON subscription_history FOR INSERT
    WITH CHECK (true);

-- ============================================================================
-- INITIAL DATA: Default preferences for new users
-- ============================================================================

-- Function to create default preferences on user signup
CREATE OR REPLACE FUNCTION create_default_preferences()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert default preferences for new user
    INSERT INTO user_preferences (user_id)
    VALUES (NEW.id)
    ON CONFLICT (user_id) DO NOTHING;
    
    -- Insert default email subscription
    INSERT INTO email_subscriptions (user_id, email, subscription_type, daily_match_limit)
    VALUES (NEW.id, NEW.email, 'free', 10)
    ON CONFLICT (user_id) DO NOTHING;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger on auth.users signup
DROP TRIGGER IF EXISTS create_user_preferences_on_signup ON auth.users;
CREATE TRIGGER create_user_preferences_on_signup
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION create_default_preferences();

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function: Check if user has active premium/pro subscription
CREATE OR REPLACE FUNCTION is_premium_user(user_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
    sub_type TEXT;
BEGIN
    SELECT subscription_type INTO sub_type
    FROM email_subscriptions
    WHERE user_id = user_uuid
      AND is_active = TRUE
      AND (expires_at IS NULL OR expires_at > NOW());
    
    RETURN sub_type IN ('premium', 'pro');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Get user's daily match limit
CREATE OR REPLACE FUNCTION get_daily_match_limit(user_uuid UUID)
RETURNS INTEGER AS $$
DECLARE
    match_limit INTEGER;
BEGIN
    SELECT daily_match_limit INTO match_limit
    FROM email_subscriptions
    WHERE user_id = user_uuid
      AND is_active = TRUE;
    
    RETURN COALESCE(match_limit, 10);  -- Default to 10 if not found
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Log user activity
CREATE OR REPLACE FUNCTION log_user_activity(
    p_user_id UUID,
    p_action TEXT,
    p_details JSONB DEFAULT NULL,
    p_ip_address INET DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO user_activity (user_id, action, details, ip_address)
    VALUES (p_user_id, p_action, p_details, p_ip_address);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- VIEWS for Analytics
-- ============================================================================

-- View: Active subscribers by tier
CREATE OR REPLACE VIEW active_subscribers_by_tier AS
SELECT
    subscription_type,
    COUNT(*) as subscriber_count,
    COUNT(*) FILTER (WHERE verified = TRUE) as verified_count
FROM email_subscriptions
WHERE is_active = TRUE
  AND (expires_at IS NULL OR expires_at > NOW())
GROUP BY subscription_type
ORDER BY subscription_type;

-- View: Revenue projection (MRR - Monthly Recurring Revenue)
CREATE OR REPLACE VIEW monthly_recurring_revenue AS
SELECT
    subscription_type,
    COUNT(*) as subscribers,
    CASE
        WHEN subscription_type = 'free' THEN 0.00
        WHEN subscription_type = 'premium' THEN 4.99
        WHEN subscription_type = 'pro' THEN 9.99
    END as price_per_month,
    COUNT(*) * CASE
        WHEN subscription_type = 'free' THEN 0.00
        WHEN subscription_type = 'premium' THEN 4.99
        WHEN subscription_type = 'pro' THEN 9.99
    END as total_revenue
FROM email_subscriptions
WHERE is_active = TRUE
  AND subscription_type IN ('premium', 'pro')
  AND (expires_at IS NULL OR expires_at > NOW())
GROUP BY subscription_type;

-- View: User engagement metrics
CREATE OR REPLACE VIEW user_engagement_metrics AS
SELECT
    DATE_TRUNC('day', created_at) as activity_date,
    action,
    COUNT(*) as event_count,
    COUNT(DISTINCT user_id) as unique_users
FROM user_activity
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', created_at), action
ORDER BY activity_date DESC, event_count DESC;

-- ============================================================================
-- GRANTS (Optional - adjust based on your security model)
-- ============================================================================

-- Grant select on views to authenticated users
GRANT SELECT ON active_subscribers_by_tier TO authenticated;
GRANT SELECT ON user_engagement_metrics TO authenticated;

-- Only service_role can see revenue
-- GRANT SELECT ON monthly_recurring_revenue TO service_role;

-- ============================================================================
-- SUCCESS MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE '✅ AUTH SCHEMA CREATED SUCCESSFULLY';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Tables created:';
    RAISE NOTICE '  - user_preferences';
    RAISE NOTICE '  - email_subscriptions';
    RAISE NOTICE '  - user_activity';
    RAISE NOTICE '  - subscription_history';
    RAISE NOTICE '';
    RAISE NOTICE 'RLS Policies: ✅ Enabled';
    RAISE NOTICE 'Triggers: ✅ Configured';
    RAISE NOTICE 'Functions: ✅ Created';
    RAISE NOTICE 'Views: ✅ Created';
    RAISE NOTICE '';
    RAISE NOTICE 'Next steps:';
    RAISE NOTICE '  1. Test signup flow (auth.users → user_preferences)';
    RAISE NOTICE '  2. Implement backend auth endpoints';
    RAISE NOTICE '  3. Build frontend Login/Register pages';
    RAISE NOTICE '========================================';
END $$;
