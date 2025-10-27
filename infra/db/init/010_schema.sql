CREATE TYPE "WRITING_TYPE_NAME" AS ENUM (
  'essay',
  'proposal',
  'report',
  'pitch',
  'blog_post'
);

CREATE TYPE "SECTION_TYPE" AS ENUM (
  'intro',
  'body',
  'conclusion',
  'custom'
);

CREATE TYPE "SENTENCE_ROLE" AS ENUM (
  'claim',
  'evidence',
  'neutral',
  'definition',
  'transition'
);

CREATE TYPE "TERM_TYPE" AS ENUM (
  'technical',
  'domain_specific',
  'general',
  'pronoun'
);

CREATE TYPE "TERM_CLARITY" AS ENUM (
  'clear',
  'needs_context',
  'needs_definition',
  'ambiguous',
  'vague'
);

CREATE TYPE "LINK_TYPE" AS ENUM (
  'supports',
  'contradicts',
  'elaborates'
);

CREATE TYPE "EVIDENCE_QUALITY" AS ENUM (
  'strong',
  'moderate',
  'weak',
  'missing'
);

CREATE TYPE "ANALYSIS_TYPE" AS ENUM (
  'full',
  'incremental',
  'goal_alignment'
);

CREATE TYPE "ANALYSIS_STATUS" AS ENUM (
  'queued',
  'running',
  'completed',
  'failed'
);

CREATE TYPE "ERROR_TYPE" AS ENUM (
  'unclear_term',
  'undefined_technical_term',
  'ambiguous_reference',
  'vague_language',
  'contradiction',
  'unsupported_claim',
  'logic_gap',
  'off_topic',
  'missing_rubric_element',
  'weak_evidence'
);

CREATE TYPE "ERROR_CATEGORY" AS ENUM (
  'clarity',
  'logic',
  'structure',
  'goal_alignment'
);

CREATE TYPE "SEVERITY" AS ENUM (
  'critical',
  'medium',
  'minor'
);

CREATE TYPE "USER_ACTION" AS ENUM (
  'accepted',
  'dismissed',
  'ignored',
  'applied'
);

CREATE TABLE "USER" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "email" text UNIQUE NOT NULL,
  "password_hash" text NOT NULL,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "WRITING_TYPE" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "name" "WRITING_TYPE_NAME" UNIQUE NOT NULL,
  "display_name" text NOT NULL,
  "description" text,
  "default_checks" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "structure_template" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "GOAL" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "user_id" uuid NOT NULL,
  "writing_type_id" uuid,
  "writing_type_custom" text,
  "rubric_text" text NOT NULL,
  "extracted_criteria" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "key_constraints" text[],  -- Array of constraint strings
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "RUBRIC_CRITERION" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "goal_id" uuid NOT NULL,
  "label" text NOT NULL,
  "description" text,
  "weight" double precision NOT NULL DEFAULT 1 CHECK (weight >= 0 AND weight <= 1),
  "order_index" int NOT NULL DEFAULT 0,
  "is_mandatory" boolean NOT NULL DEFAULT true
);

CREATE TABLE "DOCUMENT" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "user_id" uuid NOT NULL,
  "goal_id" uuid,
  "title" text NOT NULL DEFAULT 'Untitled',
  "content_full" text NOT NULL DEFAULT '',
  "structure_json" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "version" int NOT NULL DEFAULT 1,
  "word_count" int NOT NULL DEFAULT 0,
  "created_at" timestamptz NOT NULL DEFAULT (now()),
  "updated_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "DOCUMENT_SECTION" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "document_id" uuid NOT NULL,
  "section_type" "SECTION_TYPE" NOT NULL,
  "section_label" text,
  "is_complete" boolean NOT NULL DEFAULT false,
  "order_index" int NOT NULL DEFAULT 0
);

CREATE TABLE "PARAGRAPH" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "document_id" uuid NOT NULL,
  "section_id" uuid,
  "p_index" int NOT NULL,
  "text" text NOT NULL DEFAULT '',
  "hash" text NOT NULL,
  "emb" real[],
  "word_count" int NOT NULL DEFAULT 0,
  "last_analyzed_version" int,
  "updated_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "SENTENCE" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "paragraph_id" uuid NOT NULL,
  "s_index" int NOT NULL,
  "text" text NOT NULL DEFAULT '',
  "hash" text NOT NULL,
  "role" "SENTENCE_ROLE",
  "emb" real[],
  "confidence_score" double precision
);

CREATE TABLE "TERM_DEFINITION" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "document_id" uuid NOT NULL,
  "term" citext NOT NULL,
  "first_mention_sentence_id" uuid NOT NULL,
  "first_mention_p_index" int NOT NULL,
  "first_mention_s_index" int NOT NULL,
  "clarity_status" "TERM_CLARITY" NOT NULL DEFAULT 'clear',
  "clarity_issues" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "definition_text" text,
  "definition_sentence_id" uuid,
  "context_text" text,
  "subsequent_uses" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "term_type" "TERM_TYPE" NOT NULL DEFAULT 'general'
);

CREATE TABLE "CLAIM_EVIDENCE_LINK" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "document_id" uuid NOT NULL,
  "claim_sentence_id" uuid NOT NULL,
  "evidence_sentence_id" uuid NOT NULL,
  "link_type" "LINK_TYPE" NOT NULL,
  "confidence_score" double precision NOT NULL DEFAULT 0,
  "distance" int NOT NULL DEFAULT 0,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "CRITERION_COVERAGE" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "document_id" uuid NOT NULL,
  "criterion_id" uuid NOT NULL,
  "is_addressed" boolean NOT NULL DEFAULT false,
  "confidence_score" double precision NOT NULL DEFAULT 0,
  "supporting_paragraph_ids" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "supporting_sentence_ids" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "evidence_quality" "EVIDENCE_QUALITY" NOT NULL DEFAULT 'missing',
  "last_checked_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "ANALYSIS_RUN" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "document_id" uuid NOT NULL,
  "doc_version" int NOT NULL,
  "analysis_type" "ANALYSIS_TYPE" NOT NULL DEFAULT 'incremental',
  "trigger_source" text NOT NULL,
  "paragraphs_analyzed" jsonb NOT NULL DEFAULT '[]'::jsonb,
  "status" "ANALYSIS_STATUS" NOT NULL DEFAULT 'queued',
  "stats" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "error_message" text,
  "created_at" timestamptz NOT NULL DEFAULT (now()),
  "started_at" timestamptz,
  "finished_at" timestamptz
);

CREATE TABLE "LOGIC_ERROR" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "analysis_run_id" uuid NOT NULL,
  "document_id" uuid NOT NULL,
  "paragraph_id" uuid,
  "sentence_id" uuid,
  "error_type" "ERROR_TYPE" NOT NULL,
  "error_category" "ERROR_CATEGORY" NOT NULL,
  "severity" "SEVERITY" NOT NULL DEFAULT 'medium',
  "message" text NOT NULL,
  "meta" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "p_index" int,
  "s_index" int,
  "is_resolved" boolean NOT NULL DEFAULT false,
  "resolved_at" timestamptz,
  "resolved_by_doc_version" int,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "FEEDBACK" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "logic_error_id" uuid NOT NULL,
  "suggestion" text NOT NULL,
  "explanation" text,
  "meta" jsonb NOT NULL DEFAULT '{}'::jsonb,
  "user_action" "USER_ACTION",
  "user_action_at" timestamptz,
  "created_at" timestamptz NOT NULL DEFAULT (now())
);

CREATE TABLE "WRITING_SESSION" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "document_id" uuid NOT NULL,
  "user_id" uuid NOT NULL,
  "started_at" timestamptz NOT NULL DEFAULT (now()),
  "ended_at" timestamptz,
  "words_added" int NOT NULL DEFAULT 0,
  "words_deleted" int NOT NULL DEFAULT 0,
  "paragraphs_added" int NOT NULL DEFAULT 0,
  "errors_introduced" int NOT NULL DEFAULT 0,
  "errors_fixed" int NOT NULL DEFAULT 0,
  "active_time_seconds" int NOT NULL DEFAULT 0,
  "analysis_runs_triggered" int NOT NULL DEFAULT 0
);

CREATE TABLE "USER_ERROR_PATTERN" (
  "id" uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  "user_id" uuid NOT NULL,
  "error_type" "ERROR_TYPE" NOT NULL,
  "frequency" int NOT NULL DEFAULT 1,
  "last_occurred_at" timestamptz NOT NULL DEFAULT (now()),
  "avg_time_to_fix_seconds" int
);

CREATE INDEX ON "WRITING_TYPE" USING GIN ("default_checks");

CREATE INDEX ON "WRITING_TYPE" USING GIN ("structure_template");

CREATE INDEX ON "GOAL" USING GIN ("extracted_criteria");

CREATE UNIQUE INDEX ON "RUBRIC_CRITERION" ("goal_id", "order_index");

CREATE INDEX ON "DOCUMENT" ("user_id", "updated_at");

CREATE INDEX ON "DOCUMENT" USING GIN ("structure_json");

CREATE UNIQUE INDEX ON "DOCUMENT_SECTION" ("document_id", "order_index");

CREATE UNIQUE INDEX ON "PARAGRAPH" ("document_id", "p_index");

CREATE INDEX ON "PARAGRAPH" ("hash");

CREATE UNIQUE INDEX ON "SENTENCE" ("paragraph_id", "s_index");

CREATE INDEX ON "SENTENCE" ("hash");

CREATE UNIQUE INDEX ON "TERM_DEFINITION" ("document_id", "term");

CREATE INDEX ON "TERM_DEFINITION" USING GIN ("clarity_issues");

CREATE UNIQUE INDEX ON "CLAIM_EVIDENCE_LINK" ("claim_sentence_id", "evidence_sentence_id");

CREATE INDEX ON "CLAIM_EVIDENCE_LINK" ("document_id", "link_type");

CREATE UNIQUE INDEX ON "CRITERION_COVERAGE" ("document_id", "criterion_id");

CREATE INDEX ON "CRITERION_COVERAGE" USING GIN ("supporting_paragraph_ids");

CREATE INDEX ON "CRITERION_COVERAGE" USING GIN ("supporting_sentence_ids");

CREATE INDEX ON "ANALYSIS_RUN" ("document_id", "created_at");

CREATE INDEX ON "ANALYSIS_RUN" ("document_id", "doc_version");

CREATE INDEX ON "ANALYSIS_RUN" USING GIN ("paragraphs_analyzed");

CREATE INDEX ON "LOGIC_ERROR" ("document_id", "is_resolved", "created_at");

CREATE INDEX ON "LOGIC_ERROR" ("analysis_run_id", "error_type");

CREATE INDEX ON "LOGIC_ERROR" USING GIN ("meta");

CREATE INDEX ON "WRITING_SESSION" ("user_id", "started_at");

CREATE INDEX ON "WRITING_SESSION" ("document_id", "started_at");

CREATE UNIQUE INDEX ON "USER_ERROR_PATTERN" ("user_id", "error_type");

COMMENT ON COLUMN "USER"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "WRITING_TYPE"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "GOAL"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "GOAL"."user_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "GOAL"."writing_type_id" IS 'ON DELETE SET NULL';

COMMENT ON COLUMN "RUBRIC_CRITERION"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "RUBRIC_CRITERION"."goal_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "RUBRIC_CRITERION"."weight" IS 'CHECK (weight >= 0 AND weight <= 1)';

COMMENT ON COLUMN "DOCUMENT"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "DOCUMENT"."user_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "DOCUMENT"."goal_id" IS 'ON DELETE SET NULL';

COMMENT ON TABLE "DOCUMENT_SECTION" IS 'Section membership tracked via PARAGRAPH.section_id. No start/end indexes to avoid drift.';

COMMENT ON COLUMN "DOCUMENT_SECTION"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "DOCUMENT_SECTION"."document_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "DOCUMENT_SECTION"."section_label" IS 'Required when section_type = custom';

COMMENT ON COLUMN "PARAGRAPH"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "PARAGRAPH"."document_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "PARAGRAPH"."section_id" IS 'ON DELETE SET NULL';

COMMENT ON COLUMN "PARAGRAPH"."emb" IS 'pgvector extension; nullable for lazy computation';

COMMENT ON COLUMN "PARAGRAPH"."last_analyzed_version" IS 'Enables incremental analysis';

COMMENT ON COLUMN "SENTENCE"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "SENTENCE"."paragraph_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "SENTENCE"."confidence_score" IS 'Role classification confidence 0-1';

COMMENT ON TABLE "TERM_DEFINITION" IS 'clarity_issues format: [{issue: string, suggestions: string[], severity: string}]';

COMMENT ON COLUMN "TERM_DEFINITION"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "TERM_DEFINITION"."document_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "TERM_DEFINITION"."term" IS 'Case-insensitive for uniqueness';

COMMENT ON COLUMN "TERM_DEFINITION"."first_mention_sentence_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "TERM_DEFINITION"."definition_sentence_id" IS 'ON DELETE SET NULL';

COMMENT ON TABLE "CLAIM_EVIDENCE_LINK" IS 'CRITICAL: Enforce both sentences belong to same document via application logic or trigger. DBML cannot express cross-table constraint.';

COMMENT ON COLUMN "CLAIM_EVIDENCE_LINK"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "CLAIM_EVIDENCE_LINK"."document_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "CLAIM_EVIDENCE_LINK"."claim_sentence_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "CLAIM_EVIDENCE_LINK"."evidence_sentence_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "CLAIM_EVIDENCE_LINK"."confidence_score" IS 'CHECK (confidence_score >= 0 AND confidence_score <= 1)';

COMMENT ON COLUMN "CLAIM_EVIDENCE_LINK"."distance" IS 'Number of sentences between claim and evidence';

COMMENT ON COLUMN "CRITERION_COVERAGE"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "CRITERION_COVERAGE"."document_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "CRITERION_COVERAGE"."criterion_id" IS 'ON DELETE CASCADE';

COMMENT ON TABLE "ANALYSIS_RUN" IS 'stats format: {processing_time_ms, tokens_used, errors_found, errors_resolved_since_last}';

COMMENT ON COLUMN "ANALYSIS_RUN"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "ANALYSIS_RUN"."document_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "ANALYSIS_RUN"."doc_version" IS 'Snapshot of DOCUMENT.version at analysis time';

COMMENT ON COLUMN "ANALYSIS_RUN"."trigger_source" IS 'auto_pause|manual|save|scheduled';

COMMENT ON TABLE "LOGIC_ERROR" IS 'meta format: {term, compared_sentences, similarity_score, affected_criterion_id, ...}';

COMMENT ON COLUMN "LOGIC_ERROR"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "LOGIC_ERROR"."analysis_run_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "LOGIC_ERROR"."document_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "LOGIC_ERROR"."paragraph_id" IS 'ON DELETE SET NULL';

COMMENT ON COLUMN "LOGIC_ERROR"."sentence_id" IS 'ON DELETE SET NULL';

COMMENT ON TABLE "FEEDBACK" IS 'meta format: {prompt_id, model_used, tokens, generation_time_ms}';

COMMENT ON COLUMN "FEEDBACK"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "FEEDBACK"."logic_error_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "WRITING_SESSION"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "WRITING_SESSION"."document_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "WRITING_SESSION"."user_id" IS 'ON DELETE CASCADE';

COMMENT ON COLUMN "USER_ERROR_PATTERN"."id" IS 'DEFAULT gen_random_uuid()';

COMMENT ON COLUMN "USER_ERROR_PATTERN"."user_id" IS 'ON DELETE CASCADE';

ALTER TABLE "GOAL" ADD FOREIGN KEY ("user_id") REFERENCES "USER" ("id");

ALTER TABLE "GOAL" ADD FOREIGN KEY ("writing_type_id") REFERENCES "WRITING_TYPE" ("id");

ALTER TABLE "RUBRIC_CRITERION" ADD FOREIGN KEY ("goal_id") REFERENCES "GOAL" ("id");

ALTER TABLE "DOCUMENT" ADD FOREIGN KEY ("user_id") REFERENCES "USER" ("id");

ALTER TABLE "DOCUMENT" ADD FOREIGN KEY ("goal_id") REFERENCES "GOAL" ("id");

ALTER TABLE "DOCUMENT_SECTION" ADD FOREIGN KEY ("document_id") REFERENCES "DOCUMENT" ("id");

ALTER TABLE "PARAGRAPH" ADD FOREIGN KEY ("document_id") REFERENCES "DOCUMENT" ("id");

ALTER TABLE "PARAGRAPH" ADD FOREIGN KEY ("section_id") REFERENCES "DOCUMENT_SECTION" ("id");

ALTER TABLE "SENTENCE" ADD FOREIGN KEY ("paragraph_id") REFERENCES "PARAGRAPH" ("id");

ALTER TABLE "TERM_DEFINITION" ADD FOREIGN KEY ("document_id") REFERENCES "DOCUMENT" ("id");

ALTER TABLE "TERM_DEFINITION" ADD FOREIGN KEY ("first_mention_sentence_id") REFERENCES "SENTENCE" ("id");

ALTER TABLE "TERM_DEFINITION" ADD FOREIGN KEY ("definition_sentence_id") REFERENCES "SENTENCE" ("id");

ALTER TABLE "CLAIM_EVIDENCE_LINK" ADD FOREIGN KEY ("document_id") REFERENCES "DOCUMENT" ("id");

ALTER TABLE "CLAIM_EVIDENCE_LINK" ADD FOREIGN KEY ("claim_sentence_id") REFERENCES "SENTENCE" ("id");

ALTER TABLE "CLAIM_EVIDENCE_LINK" ADD FOREIGN KEY ("evidence_sentence_id") REFERENCES "SENTENCE" ("id");

ALTER TABLE "CRITERION_COVERAGE" ADD FOREIGN KEY ("document_id") REFERENCES "DOCUMENT" ("id");

ALTER TABLE "CRITERION_COVERAGE" ADD FOREIGN KEY ("criterion_id") REFERENCES "RUBRIC_CRITERION" ("id");

ALTER TABLE "ANALYSIS_RUN" ADD FOREIGN KEY ("document_id") REFERENCES "DOCUMENT" ("id");

ALTER TABLE "LOGIC_ERROR" ADD FOREIGN KEY ("analysis_run_id") REFERENCES "ANALYSIS_RUN" ("id");

ALTER TABLE "LOGIC_ERROR" ADD FOREIGN KEY ("document_id") REFERENCES "DOCUMENT" ("id");

ALTER TABLE "LOGIC_ERROR" ADD FOREIGN KEY ("paragraph_id") REFERENCES "PARAGRAPH" ("id");

ALTER TABLE "LOGIC_ERROR" ADD FOREIGN KEY ("sentence_id") REFERENCES "SENTENCE" ("id");

ALTER TABLE "FEEDBACK" ADD FOREIGN KEY ("logic_error_id") REFERENCES "LOGIC_ERROR" ("id");

ALTER TABLE "WRITING_SESSION" ADD FOREIGN KEY ("document_id") REFERENCES "DOCUMENT" ("id");

ALTER TABLE "WRITING_SESSION" ADD FOREIGN KEY ("user_id") REFERENCES "USER" ("id");

ALTER TABLE "USER_ERROR_PATTERN" ADD FOREIGN KEY ("user_id") REFERENCES "USER" ("id");