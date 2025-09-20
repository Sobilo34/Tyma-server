-- 1. Create the database (only once)
CREATE DATABASE tymdb;

-- 2. Create user if it does not exist
DO $$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'bilal'
   ) THEN
      CREATE ROLE bilal LOGIN PASSWORD 'yesitissobil#34';
   END IF;
END
$$;

-- Note: The following commands must be run connected to tymdb database.
-- You cannot switch database inside a single SQL script.
-- The \c command is a psql client command, not SQL.

-- So after creating tymdb and user, reconnect to tymdb database manually or via separate command:
-- psql -U postgres -d tymdb

-- 3. Then, grant privileges on the tymdb database and its schema
GRANT ALL PRIVILEGES ON DATABASE tymdb TO bilal;

-- After connecting to tymdb database, run:
GRANT ALL ON SCHEMA public TO bilal;
ALTER SCHEMA public OWNER TO bilal;
