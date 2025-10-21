-- các index hữu ích cho truy vấn realtime
CREATE INDEX IF NOT EXISTS idx_paragraph_doc ON "PARAGRAPH" (document_id, p_index);
CREATE INDEX IF NOT EXISTS idx_sentence_para ON "SENTENCE" (paragraph_id, s_index);
CREATE INDEX IF NOT EXISTS idx_logic_error_doc ON "LOGIC_ERROR" (document_id, is_resolved, created_at);
CREATE INDEX IF NOT EXISTS idx_term_trgm ON "TERM_DEFINITION" USING gin (term gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_doc_updated ON "DOCUMENT" (user_id, updated_at);
CREATE INDEX IF NOT EXISTS idx_cov_unique ON "CRITERION_COVERAGE" (document_id, criterion_id);
CREATE INDEX IF NOT EXISTS idx_goal_criteria_gin ON "GOAL" USING gin (extracted_criteria);
CREATE INDEX IF NOT EXISTS idx_link_by_doc ON "CLAIM_EVIDENCE_LINK" (document_id, link_type);

-- Vector search (chọn 1, tuỳ pgvector version):
-- IVF Flat:
-- CREATE INDEX sentence_emb_ivf ON "SENTENCE" USING ivfflat (emb vector_cosine_ops) WITH (lists = 100);
-- HNSW (pgvector >= 0.7):
-- CREATE INDEX sentence_emb_hnsw ON "SENTENCE" USING hnsw (emb vector_cosine_ops);
