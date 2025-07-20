-- Core user management with future pod leader capabilities
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    is_admin BOOLEAN DEFAULT FALSE,
    is_pod_leader BOOLEAN DEFAULT FALSE,
    notification_preference VARCHAR(20) DEFAULT 'high_touch', -- 'high_touch', 'low_touch'
    device_id VARCHAR(255), -- For offline sync before login
    
    -- Metrics for future pod assignment AI
    commitment_success_rate DECIMAL(3,2), -- 0.00 to 1.00
    attendance_rate DECIMAL(3,2),
    communication_style VARCHAR(50) -- For future personality matching
);

COMMENT ON TABLE users IS 'Core user table supporting both regular users and pod leaders';
COMMENT ON COLUMN users.device_id IS 'Temporary identifier for offline commitment capture before authentication';
COMMENT ON COLUMN users.commitment_success_rate IS 'Rolling average of commitment completion for AI pod matching';

-- Pod management with health tracking
CREATE TABLE pods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    leader_id UUID REFERENCES users(id),
    max_size INTEGER DEFAULT 5,
    call_day VARCHAR(10), -- 'monday', 'tuesday', etc.
    call_time TIME,
    jitsi_room_id VARCHAR(100) UNIQUE,
    
    -- Health metrics for AI monitoring
    health_score DECIMAL(3,2) DEFAULT 1.00, -- 0.00 to 1.00
    last_health_check TIMESTAMPTZ,
    
    -- Future revenue sharing
    revenue_share_enabled BOOLEAN DEFAULT FALSE,
    revenue_share_percentage DECIMAL(3,2) DEFAULT 0.10
);

COMMENT ON TABLE pods IS 'Accountability groups with health tracking and future revenue capabilities';
COMMENT ON COLUMN pods.health_score IS 'Composite score of attendance, completion, and engagement for AI interventions';

-- User-pod membership with performance tracking
CREATE TABLE pod_memberships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    left_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Individual performance within pod
    weeks_active INTEGER DEFAULT 0,
    
    CONSTRAINT unique_active_membership UNIQUE(user_id, pod_id, is_active)
);

COMMENT ON TABLE pod_memberships IS 'Tracks user participation in pods with historical data for rebalancing algorithms';

-- Commitments with full lifecycle tracking
CREATE TABLE commitments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pod_id UUID REFERENCES pods(id) ON DELETE SET NULL,
    text TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    week_number INTEGER NOT NULL, -- ISO week number
    year INTEGER NOT NULL,
    
    -- Completion tracking
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ,
    
    -- For offline sync
    device_created_at TIMESTAMPTZ,
    synced_at TIMESTAMPTZ,
    
    -- Future planning horizons
    planning_horizon VARCHAR(20) DEFAULT 'week' -- 'week', 'month', 'quarter', 'year'
);

CREATE INDEX idx_user_week ON commitments (user_id, year, week_number);
CREATE INDEX idx_pod_week ON commitments (pod_id, year, week_number);

COMMENT ON TABLE commitments IS 'User commitments with offline support and future planning horizon expansion';
COMMENT ON COLUMN commitments.planning_horizon IS 'Unlocked progressively: 4 weeks->month, 3 months->quarter, etc.';

-- Call attendance for health metrics
CREATE TABLE call_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    pod_id UUID REFERENCES pods(id) ON DELETE CASCADE,
    scheduled_at TIMESTAMPTZ NOT NULL,
    attended BOOLEAN DEFAULT FALSE,
    video_update_url VARCHAR(500) -- For async updates
);

CREATE INDEX idx_pod_scheduled ON call_attendance (pod_id, scheduled_at);

COMMENT ON TABLE call_attendance IS 'Tracks attendance for pod health calculations and AI interventions';

-- Notifications and AI touchpoints
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'midweek_checkin', '24hr_reminder', 'completion_celebration'
    sent_at TIMESTAMPTZ DEFAULT NOW(),
    opened_at TIMESTAMPTZ,
    
    -- AI personalization
    ai_generated_content TEXT,
    sentiment_score DECIMAL(3,2) -- For A/B testing different tones
);

COMMENT ON TABLE notifications IS 'Tracks all user touchpoints for engagement optimization';

-- Enable Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE pods ENABLE ROW LEVEL SECURITY;
ALTER TABLE pod_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE commitments ENABLE ROW LEVEL SECURITY;
ALTER TABLE call_attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Basic RLS policies (to be expanded)
CREATE POLICY "Users can view their own data" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own data" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view their commitments" ON commitments
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their commitments" ON commitments
    FOR ALL USING (auth.uid() = user_id);