CREATE OR REPLACE FUNCTION ensure_claim_evidence_same_document()
RETURNS trigger AS $$
DECLARE
  doc_claim uuid;
  doc_evid  uuid;
BEGIN
  SELECT p.document_id INTO doc_claim
  FROM sentence s JOIN paragraph p ON s.paragraph_id = p.id
  WHERE s.id = NEW.claim_sentence_id;

  SELECT p.document_id INTO doc_evid
  FROM sentence s JOIN paragraph p ON s.paragraph_id = p.id
  WHERE s.id = NEW.evidence_sentence_id;

  IF doc_claim IS NULL OR doc_evid IS NULL OR doc_claim <> doc_evid THEN
    RAISE EXCEPTION 'claim and evidence must belong to the same document';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_claim_evidence_same_doc ON claim_evidence_link;
CREATE TRIGGER trg_claim_evidence_same_doc
BEFORE INSERT OR UPDATE ON claim_evidence_link
FOR EACH ROW EXECUTE FUNCTION ensure_claim_evidence_same_document();
