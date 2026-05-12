"""
Run this SQL in Supabase SQL Editor to update the schema.
This replaces the old pgvector table with a simpler plain text table.
"""

SQL = """
-- Drop old table if exists
DROP TABLE IF EXISTS pr_reviews;

-- Create simple reviews table (no embeddings needed)
CREATE TABLE pr_reviews (
    id TEXT PRIMARY KEY,
    repo TEXT NOT NULL,
    pr_number INTEGER NOT NULL,
    diff TEXT,
    review TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Index for fast repo lookups
CREATE INDEX pr_reviews_repo_idx ON pr_reviews(repo);
CREATE INDEX pr_reviews_created_at_idx ON pr_reviews(created_at DESC);
"""

print(SQL)
"""

Now update `agents.py` to pass repo to memory context:
"""
