-- các index hữu ích cho truy vấn realtime
CREATE INDEX IF NOT EXISTS idx_paragraph_doc ON paragraph (document_id, p_index);
CREATE INDEX IF NOT EXISTS idx_sentence_para ON sentence (paragraph_id, s_index);
CREATE INDEX IF NOT EXISTS idx_logic_error_doc ON logic_error (document_id, is_resolved, created_at);
CREATE INDEX IF NOT EXISTS idx_term_trgm ON term_definition USING gin (term gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_doc_updated ON document (user_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_cov_unique ON criterion_coverage (document_id, criterion_id);
CREATE INDEX IF NOT EXISTS idx_goal_criteria_gin ON goal USING gin (extracted_criteria);
CREATE INDEX IF NOT EXISTS idx_link_by_doc ON claim_evidence_link (document_id, link_type);

-- Vector search (chọn 1, tuỳ pgvector version):
-- IVF Flat:
-- CREATE INDEX sentence_emb_ivf ON sentence USING ivfflat (emb vector_cosine_ops) WITH (lists = 100);
-- HNSW (pgvector >= 0.7):
-- CREATE INDEX sentence_emb_hnsw ON sentence USING hnsw (emb vector_cosine_ops);
