-- Create application user with limited privileges
CREATE USER ai_agent_app WITH PASSWORD 'ai_agent_app_password';

-- Grant connection to database
GRANT CONNECT ON DATABASE ai_agent_hub TO ai_agent_app;

-- Grant schema usage and create privileges
GRANT USAGE, CREATE ON SCHEMA public TO ai_agent_app;

-- Grant table privileges (for all current and future tables)
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ai_agent_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ai_agent_app;

-- Grant sequence privileges (for auto-increment IDs)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ai_agent_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO ai_agent_app;

-- Grant function/procedure privileges
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO ai_agent_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON FUNCTIONS TO ai_agent_app;
