"""
Setup Supabase for PR review memory:

1. Go to https://supabase.com → Sign up (free tier)
2. Create a new project
3. Get your:
   - Project URL → SUPABASE_URL in .env
   - Project API key (anon public) → SUPABASE_KEY in .env

4. Run this SQL in the Supabase SQL editor:
"""
SQL_SETUP = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table for PR reviews
CREATE TABLE IF NOT EXISTS pr_reviews (
    id BIGSERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc', NOW())
);

-- Create index for similarity search
CREATE INDEX IF NOT EXISTS pr_reviews_embedding_idx 
    ON pr_reviews USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Create function for similarity search
CREATE OR REPLACE FUNCTION match_pr_reviews(
    query_embedding vector(1536),
    match_count int DEFAULT 5
)
RETURNS TABLE(
    id BIGINT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        pr_reviews.id,
        pr_reviews.content,
        pr_reviews.metadata,
        1 - (pr_reviews.embedding <=> query_embedding) AS similarity
    FROM pr_reviews
    ORDER BY pr_reviews.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
"""

print(SQL_SETUP)
print("\nAfter setting up Supabase, add these to your .env:")
print("SUPABASE_URL=https://your-project-ref.supabase.co")
print("SUPABASE_KEY=your-anon-key")
