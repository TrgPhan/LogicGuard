-- WRITING_TYPE mặc định
INSERT INTO "WRITING_TYPE" (id, name, display_name, description)
VALUES
  (gen_random_uuid(), 'essay',      'Essay',      'Chuẩn bài luận'),
  (gen_random_uuid(), 'proposal',   'Proposal',   'Đề xuất'),
  (gen_random_uuid(), 'report',     'Report',     'Báo cáo'),
  (gen_random_uuid(), 'pitch',      'Pitch',      'Thuyết trình'),
  (gen_random_uuid(), 'blog_post',  'Blog Post',  'Bài blog')
ON CONFLICT DO NOTHING;

-- USER test
INSERT INTO "USER"(id, email, password_hash)
VALUES (gen_random_uuid(), 'demo@logicguard.ai', '$2b$12$examplehash')
ON CONFLICT DO NOTHING;