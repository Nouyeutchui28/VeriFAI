-- Create users table
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  oauth_provider VARCHAR(50),
  oauth_id VARCHAR(255) UNIQUE,
  oauth_token TEXT,
  picture_url VARCHAR(512),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create scans table
CREATE TABLE IF NOT EXISTS scans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  project_name VARCHAR(255),
  repo_url VARCHAR(2048),
  status VARCHAR(50) DEFAULT 'pending',
  file_count INTEGER,
  repo_size_mb FLOAT,
  primary_language VARCHAR(50),
  start_time TIMESTAMP WITH TIME ZONE,
  end_time TIMESTAMP WITH TIME ZONE,
  error_message VARCHAR(512),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create results table
CREATE TABLE IF NOT EXISTS results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id UUID NOT NULL UNIQUE REFERENCES scans(id),
  code_snippet TEXT,
  semgrep_json JSONB,
  llm_analysis TEXT,
  patches TEXT,
  severity_count JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create chat_messages table
CREATE TABLE IF NOT EXISTS chat_messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scan_id UUID NOT NULL REFERENCES scans(id),
  role VARCHAR(50),
  content TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_oauth_id ON users(oauth_id);
CREATE INDEX idx_scans_user_id ON scans(user_id);
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_results_scan_id ON results(scan_id);
CREATE INDEX idx_chat_messages_scan_id ON chat_messages(scan_id);

-- Insert sample user
INSERT INTO users (email, name, oauth_provider, oauth_id, picture_url)
VALUES (
  'demo@verifai-llm.com',
  'Demo User',
  'google',
  'google_123456789',
  'https://lh3.googleusercontent.com/a/default-user=s96'
) ON CONFLICT (email) DO NOTHING;

-- Insert sample scans
INSERT INTO scans (user_id, project_name, repo_url, status, file_count, repo_size_mb, primary_language, start_time, end_time)
SELECT
  id,
  'TripBook',
  'https://github.com/zDjangoBay/TripBook.git',
  'complete',
  73,
  0.27,
  'Kotlin',
  CURRENT_TIMESTAMP - INTERVAL '1 day',
  CURRENT_TIMESTAMP - INTERVAL '1 day' + INTERVAL '5 minutes'
FROM users WHERE email = 'demo@verifai-llm.com'
ON CONFLICT DO NOTHING;

INSERT INTO scans (user_id, project_name, repo_url, status, file_count, repo_size_mb, primary_language, start_time, end_time)
SELECT
  id,
  'golang/go',
  'https://github.com/golang/go.git',
  'complete',
  4250,
  150.5,
  'Go',
  CURRENT_TIMESTAMP - INTERVAL '2 days',
  CURRENT_TIMESTAMP - INTERVAL '2 days' + INTERVAL '45 minutes'
FROM users WHERE email = 'demo@verifai-llm.com'
ON CONFLICT DO NOTHING;

-- Insert sample results
INSERT INTO results (scan_id, code_snippet, llm_analysis, severity_count)
SELECT
  id,
  'func login(username, password string) { query := "SELECT * FROM users WHERE username='\''" + username + "'\''" }',
  'SQL Injection vulnerability detected in login function. User input is directly concatenated into SQL query without sanitization.',
  '{"critical": 1, "high": 2, "medium": 3, "low": 0}'::jsonb
FROM scans WHERE project_name = 'TripBook' LIMIT 1
ON CONFLICT DO NOTHING;

-- Insert sample chat messages
INSERT INTO chat_messages (scan_id, role, content)
SELECT
  id,
  'user',
  'What vulnerabilities were found in this scan?'
FROM scans WHERE project_name = 'TripBook' LIMIT 1
ON CONFLICT DO NOTHING;

INSERT INTO chat_messages (scan_id, role, content)
SELECT
  id,
  'assistant',
  'The scan identified 6 vulnerabilities: 1 Critical, 2 High, and 3 Medium severity issues. The most critical is an SQL injection vulnerability in the login function.'
FROM scans WHERE project_name = 'TripBook' LIMIT 1
ON CONFLICT DO NOTHING;
