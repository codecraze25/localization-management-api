-- Localization Management Database Schema
-- Run this in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL
);

-- Languages table
CREATE TABLE IF NOT EXISTS languages (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    flag VARCHAR(10)
);

-- Project languages junction table
CREATE TABLE IF NOT EXISTS project_languages (
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    language_code VARCHAR(10) REFERENCES languages(code) ON DELETE CASCADE,
    PRIMARY KEY (project_id, language_code)
);

-- Translation keys table
CREATE TABLE IF NOT EXISTS translation_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    UNIQUE(project_id, key)
);

-- Translations table
CREATE TABLE IF NOT EXISTS translations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    translation_key_id UUID REFERENCES translation_keys(id) ON DELETE CASCADE,
    language_code VARCHAR(10) REFERENCES languages(code) ON DELETE CASCADE,
    value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW()) NOT NULL,
    updated_by VARCHAR(255) DEFAULT 'system',
    UNIQUE(translation_key_id, language_code)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_translation_keys_project_id ON translation_keys(project_id);
CREATE INDEX IF NOT EXISTS idx_translation_keys_category ON translation_keys(category);
CREATE INDEX IF NOT EXISTS idx_translations_key_id ON translations(translation_key_id);
CREATE INDEX IF NOT EXISTS idx_translations_language ON translations(language_code);

-- Insert some default languages
INSERT INTO languages (code, name, flag) VALUES
    ('en', 'English', '🇺🇸'),
    ('es', 'Spanish', '🇪🇸'),
    ('fr', 'French', '🇫🇷'),
    ('de', 'German', '🇩🇪'),
    ('it', 'Italian', '🇮🇹'),
    ('pt', 'Portuguese', '🇵🇹'),
    ('ja', 'Japanese', '🇯🇵'),
    ('ko', 'Korean', '🇰🇷'),
    ('zh', 'Chinese', '🇨🇳')
ON CONFLICT (code) DO NOTHING;

-- Create a function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = TIMEZONE('utc'::text, NOW());
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers to automatically update updated_at
CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_translation_keys_updated_at BEFORE UPDATE ON translation_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_translations_updated_at BEFORE UPDATE ON translations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();