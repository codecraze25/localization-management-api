-- Sample data for testing
-- Run this after the schema is created

-- Insert a sample project
INSERT INTO projects (id, name, description) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'Demo App', 'A sample project for demonstration')
ON CONFLICT (id) DO NOTHING;

-- Link languages to the project
INSERT INTO project_languages (project_id, language_code) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'en'),
    ('550e8400-e29b-41d4-a716-446655440000', 'es'),
    ('550e8400-e29b-41d4-a716-446655440000', 'fr')
ON CONFLICT (project_id, language_code) DO NOTHING;

-- Insert sample translation keys
INSERT INTO translation_keys (id, key, category, description, project_id) VALUES
    ('660e8400-e29b-41d4-a716-446655440001', 'button.save', 'buttons', 'Save button text', '550e8400-e29b-41d4-a716-446655440000'),
    ('660e8400-e29b-41d4-a716-446655440002', 'button.cancel', 'buttons', 'Cancel button text', '550e8400-e29b-41d4-a716-446655440000'),
    ('660e8400-e29b-41d4-a716-446655440003', 'greeting.welcome', 'messages', 'Welcome message', '550e8400-e29b-41d4-a716-446655440000'),
    ('660e8400-e29b-41d4-a716-446655440004', 'error.notFound', 'errors', 'Not found error message', '550e8400-e29b-41d4-a716-446655440000'),
    ('660e8400-e29b-41d4-a716-446655440005', 'nav.dashboard', 'navigation', 'Dashboard navigation item', '550e8400-e29b-41d4-a716-446655440000')
ON CONFLICT (project_id, key) DO NOTHING;

-- Insert sample translations
INSERT INTO translations (translation_key_id, language_code, value, updated_by) VALUES
    -- English translations
    ('660e8400-e29b-41d4-a716-446655440001', 'en', 'Save', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440002', 'en', 'Cancel', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440003', 'en', 'Welcome to our application!', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440004', 'en', 'The requested resource was not found.', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440005', 'en', 'Dashboard', 'admin'),

    -- Spanish translations
    ('660e8400-e29b-41d4-a716-446655440001', 'es', 'Guardar', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440002', 'es', 'Cancelar', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440003', 'es', '¡Bienvenido a nuestra aplicación!', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440004', 'es', 'El recurso solicitado no fue encontrado.', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440005', 'es', 'Panel de Control', 'admin'),

    -- French translations
    ('660e8400-e29b-41d4-a716-446655440001', 'fr', 'Enregistrer', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440002', 'fr', 'Annuler', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440003', 'fr', 'Bienvenue dans notre application!', 'admin'),
    ('660e8400-e29b-41d4-a716-446655440004', 'fr', 'La ressource demandée n''a pas été trouvée.', 'admin')
    -- Note: Dashboard translation missing in French (to test missing translations feature)
ON CONFLICT (translation_key_id, language_code) DO NOTHING;
