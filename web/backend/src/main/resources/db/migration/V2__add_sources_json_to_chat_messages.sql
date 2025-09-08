-- Add sources_json column to chat_messages table to store AI response sources
-- This allows persisting source references and metadata beyond page refreshes

ALTER TABLE chat_messages 
ADD COLUMN sources_json TEXT DEFAULT NULL 
COMMENT 'JSON string containing AI response sources and metadata';

-- Add index for better performance when querying messages with sources
CREATE INDEX idx_chat_messages_sources ON chat_messages(sources_json(100));
