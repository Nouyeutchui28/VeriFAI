-- 1. Enable RLS and Force RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users FORCE ROW LEVEL SECURITY;

ALTER TABLE public.scans ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.scans FORCE ROW LEVEL SECURITY;

ALTER TABLE public.results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.results FORCE ROW LEVEL SECURITY;

ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages FORCE ROW LEVEL SECURITY;

-- 2. Create missing performance indexes
CREATE INDEX IF NOT EXISTS idx_scans_user_id ON public.scans(user_id);
CREATE INDEX IF NOT EXISTS idx_results_scan_id ON public.results(scan_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_scan_id ON public.chat_messages(scan_id);

-- 3. Create RLS Policies

-- Users: A user can only see and update their own record
CREATE POLICY "Users can view their own record" ON public.users
    FOR SELECT USING (id = auth.uid());

CREATE POLICY "Users can update their own record" ON public.users
    FOR UPDATE USING (id = auth.uid());

-- Scans: A user can only see, create, and update their own scans
CREATE POLICY "Users can view their own scans" ON public.scans
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own scans" ON public.scans
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own scans" ON public.scans
    FOR UPDATE USING (user_id = auth.uid());

-- Results: A user can only see results for their own scans
CREATE POLICY "Users can view results for their own scans" ON public.results
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.scans
            WHERE public.scans.id = public.results.scan_id
            AND public.scans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert results for their own scans" ON public.results
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.scans
            WHERE public.scans.id = public.results.scan_id
            AND public.scans.user_id = auth.uid()
        )
    );

-- Chat Messages: A user can only see chat messages for their own scans
CREATE POLICY "Users can view messages for their own scans" ON public.chat_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.scans
            WHERE public.scans.id = public.chat_messages.scan_id
            AND public.scans.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert messages for their own scans" ON public.chat_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.scans
            WHERE public.scans.id = public.chat_messages.scan_id
            AND public.scans.user_id = auth.uid()
        )
    );
