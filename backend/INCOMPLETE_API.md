# LogicGuard - Incomplete API Endpoints Specification

This document specifies the expected input and output for all remaining API endpoints that need to be implemented - **28 API endpoints** across 4 categories:

### 1. Real-Time Logic Checking (8 endpoints)
- Queue analysis, check status, view history
- Upload embeddings
- Detect contradictions, undefined terms, unsupported claims, logical jumps

### 2. Error Tracking & Feedback (5 endpoints)
- Get/resolve errors
- Generate and manage AI feedback

### 3. Goal Alignment Dashboard (3 endpoints)
- Get/recompute rubric coverage
- List criteria

### 4. Analytics & Writing Insights (5 endpoints)
- Session tracking
- User and document analytics


---

## 4. Real-Time Logic Checking (NLP + Analysis)

### 4.1 Queue New Analysis
**POST** `/api/analysis/run`

Trigger full or incremental analysis for a document.

**Input:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "analysis_type": "full",
  "options": {
    "check_contradictions": true,
    "check_undefined_terms": true,
    "check_unsupported_claims": true,
    "check_logical_jumps": true,
    "check_goal_alignment": true
  }
}
```

**Output:**
```json
{
  "run_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "status": "queued",
  "analysis_type": "full",
  "queued_at": "2025-10-23T10:30:15.123456Z",
  "estimated_completion": "2025-10-23T10:31:00.000000Z"
}
```

**curl Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/analysis/run" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
    "analysis_type": "full",
    "options": {
      "check_contradictions": true,
      "check_undefined_terms": true
    }
  }'
```

---

### 4.2 Get Latest Analysis Status
**GET** `/api/analysis/{document_id}/status`

Retrieve running or completed analysis state.

**Input:** None (document_id in URL path)

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "latest_run": {
    "run_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
    "status": "completed",
    "analysis_type": "full",
    "started_at": "2025-10-23T10:30:15.123456Z",
    "completed_at": "2025-10-23T10:30:45.789012Z",
    "duration_seconds": 30,
    "errors_found": 5,
    "warnings_found": 12
  },
  "document_version": 3,
  "is_current": true
}
```

**curl Example:**
```bash
curl -X GET "http://127.0.0.1:8000/api/analysis/75d7780d-9342-4f07-84af-762319d18cc4/status" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 4.3 Get Analysis History
**GET** `/api/analysis/{document_id}/history`

List past analysis runs, stats, and errors found.

**Input:** None (document_id in URL path, optional query params: `limit`, `offset`)

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "total_runs": 8,
  "runs": [
    {
      "run_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
      "status": "completed",
      "analysis_type": "full",
      "document_version": 3,
      "started_at": "2025-10-23T10:30:15.123456Z",
      "completed_at": "2025-10-23T10:30:45.789012Z",
      "duration_seconds": 30,
      "errors_found": 5,
      "warnings_found": 12,
      "error_breakdown": {
        "contradictions": 2,
        "undefined_terms": 1,
        "unsupported_claims": 2,
        "logical_jumps": 0
      }
    },
    {
      "run_id": "b2c3d4e5-6789-01bc-def1-234567890abc",
      "status": "completed",
      "analysis_type": "incremental",
      "document_version": 2,
      "started_at": "2025-10-23T09:15:20.555555Z",
      "completed_at": "2025-10-23T09:15:35.666666Z",
      "duration_seconds": 15,
      "errors_found": 3,
      "warnings_found": 8,
      "error_breakdown": {
        "contradictions": 1,
        "undefined_terms": 0,
        "unsupported_claims": 2,
        "logical_jumps": 0
      }
    }
  ]
}
```

**curl Example:**
```bash
curl -X GET "http://127.0.0.1:8000/api/analysis/75d7780d-9342-4f07-84af-762319d18cc4/history?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 4.4 Upload Embeddings
**POST** `/api/analysis/embeddings`

Store vector embeddings for paragraphs or sentences.

**Input:**
```json
{
  "embeddings": [
    {
      "paragraph_id": "e0dd0926-e761-462c-b0d6-4b46c860ebe0",
      "embedding": [0.123, 0.456, 0.789, ..., 0.321],
      "model": "sentence-transformers/all-MiniLM-L6-v2",
      "dimension": 384
    },
    {
      "paragraph_id": "4f59405d-53ae-4287-bbd7-605c4a469726",
      "embedding": [0.234, 0.567, 0.890, ..., 0.432],
      "model": "sentence-transformers/all-MiniLM-L6-v2",
      "dimension": 384
    }
  ]
}
```

**Output:**
```json
{
  "success": true,
  "embeddings_stored": 2,
  "model": "sentence-transformers/all-MiniLM-L6-v2",
  "dimension": 384,
  "stored_at": "2025-10-23T10:32:15.123456Z"
}
```

**curl Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/analysis/embeddings" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "embeddings": [
      {
        "paragraph_id": "e0dd0926-e761-462c-b0d6-4b46c860ebe0",
        "embedding": [0.123, 0.456, 0.789],
        "model": "sentence-transformers/all-MiniLM-L6-v2",
        "dimension": 384
      }
    ]
  }'
```

---

### 4.5 Detect Contradictions
**POST** `/api/analysis/check/contradictions`

Compare sentence pairs using NLI (Natural Language Inference) model.

**Input:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "sentence_pairs": [
    {
      "sentence_1_id": "e860a69a-2cc6-4af7-b3b6-eb12325c35e1",
      "sentence_2_id": "52deab08-5d1a-460c-b374-d3f59aded904"
    }
  ],
  "threshold": 0.85
}
```

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "contradictions_found": 1,
  "results": [
    {
      "sentence_1": {
        "id": "e860a69a-2cc6-4af7-b3b6-eb12325c35e1",
        "text": "AI is revolutionizing healthcare with unprecedented accuracy.",
        "paragraph_id": "4f59405d-53ae-4287-bbd7-605c4a469726"
      },
      "sentence_2": {
        "id": "52deab08-5d1a-460c-b374-d3f59aded904",
        "text": "Machine learning systems still struggle with medical diagnosis accuracy.",
        "paragraph_id": "6ee05467-0f06-4476-9830-451e31a8be04"
      },
      "is_contradiction": true,
      "confidence_score": 0.92,
      "nli_label": "contradiction",
      "explanation": "The first sentence claims AI has unprecedented accuracy while the second states systems struggle with accuracy."
    }
  ],
  "model_used": "microsoft/deberta-v3-base-nli",
  "analyzed_at": "2025-10-23T10:35:20.123456Z"
}
```

**curl Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/analysis/check/contradictions" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
    "sentence_pairs": [
      {
        "sentence_1_id": "e860a69a-2cc6-4af7-b3b6-eb12325c35e1",
        "sentence_2_id": "52deab08-5d1a-460c-b374-d3f59aded904"
      }
    ],
    "threshold": 0.85
  }'
```

---

### 4.6 Detect Undefined Terms
**POST** `/api/analysis/check/undefined-terms`

Entity recognition and clarity check for technical terms.

**Input:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "paragraphs": [
    "e0dd0926-e761-462c-b0d6-4b46c860ebe0",
    "4f59405d-53ae-4287-bbd7-605c4a469726"
  ],
  "min_occurrences": 2
}
```

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "undefined_terms_found": 3,
  "terms": [
    {
      "term": "in silico",
      "category": "technical_jargon",
      "occurrences": 2,
      "first_mention": {
        "sentence_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
        "paragraph_id": "f49f8ea7-1a67-45b3-8f40-b961939578b9",
        "context": "AI algorithms can screen millions of compounds in silico..."
      },
      "is_defined": false,
      "suggestion": "Consider defining 'in silico' (computer simulation) on first use for clarity."
    },
    {
      "term": "NLI model",
      "category": "acronym",
      "occurrences": 3,
      "first_mention": {
        "sentence_id": "def67890-ghij-klmn-opqr-stuvwxyz1234",
        "paragraph_id": "4f59405d-53ae-4287-bbd7-605c4a469726",
        "context": "...using an NLI model to detect contradictions..."
      },
      "is_defined": false,
      "suggestion": "Define NLI (Natural Language Inference) on first use."
    },
    {
      "term": "algorithmic bias",
      "category": "technical_concept",
      "occurrences": 2,
      "first_mention": {
        "sentence_id": "ghi78901-jklm-nopq-rstu-vwxyz1234567",
        "paragraph_id": "6ee05467-0f06-4476-9830-451e31a8be04",
        "context": "Issues of data privacy, algorithmic bias, and the need..."
      },
      "is_defined": false,
      "suggestion": "Explain what algorithmic bias means in this context."
    }
  ],
  "analyzed_at": "2025-10-23T10:40:12.345678Z"
}
```

**curl Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/analysis/check/undefined-terms" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
    "paragraphs": ["e0dd0926-e761-462c-b0d6-4b46c860ebe0"],
    "min_occurrences": 2
  }'
```

---

### 4.7 Detect Unsupported Claims
**POST** `/api/analysis/check/unsupported-claims`

Claim/evidence classification and link detection.

**Input:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "paragraphs": [
    "4f59405d-53ae-4287-bbd7-605c4a469726",
    "dabf1e89-d7a1-40be-864e-86700581187c"
  ]
}
```

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "unsupported_claims_found": 2,
  "claims": [
    {
      "claim_id": "claim-uuid-1",
      "sentence_id": "e860a69a-2cc6-4af7-b3b6-eb12325c35e1",
      "paragraph_id": "4f59405d-53ae-4287-bbd7-605c4a469726",
      "text": "AI systems achieve 95% accuracy in medical diagnosis.",
      "classification": "claim",
      "confidence": 0.94,
      "has_evidence": false,
      "evidence_sentences": [],
      "severity": "high",
      "suggestion": "This claim requires supporting evidence such as citations, statistics, or examples."
    },
    {
      "claim_id": "claim-uuid-2",
      "sentence_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
      "paragraph_id": "dabf1e89-d7a1-40be-864e-86700581187c",
      "text": "Personalized medicine will reduce healthcare costs by 40%.",
      "classification": "claim",
      "confidence": 0.89,
      "has_evidence": false,
      "evidence_sentences": [],
      "severity": "high",
      "suggestion": "Provide data or research to support this specific percentage claim."
    }
  ],
  "supported_claims": 5,
  "total_claims": 7,
  "analyzed_at": "2025-10-23T10:42:30.456789Z"
}
```

**curl Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/analysis/check/unsupported-claims" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
    "paragraphs": ["4f59405d-53ae-4287-bbd7-605c4a469726"]
  }'
```

---

### 4.8 Detect Logical Jumps
**POST** `/api/analysis/check/logical-jumps`

Similarity analysis between paragraphs to detect abrupt topic changes.

**Input:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "section_id": "ad5aa8e7-f387-4098-b8a4-9d9cb2bcebf9",
  "similarity_threshold": 0.4
}
```

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "section_id": "ad5aa8e7-f387-4098-b8a4-9d9cb2bcebf9",
  "logical_jumps_found": 1,
  "jumps": [
    {
      "from_paragraph": {
        "id": "4f59405d-53ae-4287-bbd7-605c4a469726",
        "p_index": 1,
        "text": "One of the most significant applications of AI in healthcare is in medical imaging...",
        "topic": "medical_imaging"
      },
      "to_paragraph": {
        "id": "dabf1e89-d7a1-40be-864e-86700581187c",
        "p_index": 3,
        "text": "AI is also revolutionizing personalized medicine and treatment planning...",
        "topic": "personalized_medicine"
      },
      "similarity_score": 0.32,
      "is_logical_jump": true,
      "severity": "medium",
      "suggestion": "Consider adding a transition sentence to connect the discussion of medical imaging to personalized medicine. Current similarity score (0.32) is below threshold (0.40).",
      "recommended_transition": "Beyond diagnostic imaging, AI's capabilities extend to treatment personalization."
    }
  ],
  "analyzed_at": "2025-10-23T10:45:00.567890Z"
}
```

**curl Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/analysis/check/logical-jumps" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
    "section_id": "ad5aa8e7-f387-4098-b8a4-9d9cb2bcebf9",
    "similarity_threshold": 0.4
  }'
```

---

## 5. Error Tracking & Feedback (Sidebar Integration)

### 5.1 Get Logic Errors
**GET** `/api/documents/{id}/errors`

Fetch unresolved logic errors for a document.

**Input:** None (document ID in URL path, optional query params: `status`, `error_type`)

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "document_version": 3,
  "total_errors": 5,
  "unresolved_errors": 3,
  "errors": [
    {
      "id": "error-uuid-1",
      "error_type": "contradiction",
      "severity": "high",
      "status": "unresolved",
      "location": {
        "paragraph_id": "4f59405d-53ae-4287-bbd7-605c4a469726",
        "sentence_id": "e860a69a-2cc6-4af7-b3b6-eb12325c35e1",
        "p_index": 1
      },
      "description": "Contradictory statement detected with paragraph 7",
      "details": {
        "conflicting_sentence_id": "52deab08-5d1a-460c-b374-d3f59aded904",
        "confidence_score": 0.92
      },
      "detected_at": "2025-10-23T10:35:20.123456Z",
      "resolved_at": null
    },
    {
      "id": "error-uuid-2",
      "error_type": "unsupported_claim",
      "severity": "high",
      "status": "unresolved",
      "location": {
        "paragraph_id": "dabf1e89-d7a1-40be-864e-86700581187c",
        "sentence_id": "abc12345-def6-7890-ghij-klmnopqrstuv",
        "p_index": 3
      },
      "description": "Claim lacks supporting evidence",
      "details": {
        "claim_text": "Personalized medicine will reduce healthcare costs by 40%.",
        "confidence_score": 0.89
      },
      "detected_at": "2025-10-23T10:42:30.456789Z",
      "resolved_at": null
    },
    {
      "id": "error-uuid-3",
      "error_type": "undefined_term",
      "severity": "medium",
      "status": "unresolved",
      "location": {
        "paragraph_id": "f49f8ea7-1a67-45b3-8f40-b961939578b9",
        "sentence_id": "def67890-ghij-klmn-opqr-stuvwxyz1234",
        "p_index": 5
      },
      "description": "Technical term 'in silico' not defined",
      "details": {
        "term": "in silico",
        "first_occurrence": true
      },
      "detected_at": "2025-10-23T10:40:12.345678Z",
      "resolved_at": null
    }
  ]
}
```

**curl Example:**
```bash
curl -X GET "http://127.0.0.1:8000/api/documents/75d7780d-9342-4f07-84af-762319d18cc4/errors?status=unresolved" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 5.2 Resolve Logic Error
**PATCH** `/api/errors/{id}/resolve`

Mark a logic error as resolved.

**Input:**
```json
{
  "resolution_type": "fixed",
  "resolution_note": "Removed contradictory sentence and clarified the claim."
}
```

**Output:**
```json
{
  "id": "error-uuid-1",
  "error_type": "contradiction",
  "severity": "high",
  "status": "resolved",
  "resolution_type": "fixed",
  "resolution_note": "Removed contradictory sentence and clarified the claim.",
  "detected_at": "2025-10-23T10:35:20.123456Z",
  "resolved_at": "2025-10-23T11:20:45.678901Z",
  "resolved_by": "33d386ec-7b46-4b20-9669-51ce979565d4"
}
```

**curl Example:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/errors/error-uuid-1/resolve" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resolution_type": "fixed",
    "resolution_note": "Removed contradictory sentence and clarified the claim."
  }'
```

---

### 5.3 Add AI Feedback
**POST** `/api/feedback`

Generate suggestion text via LLM for a specific error or section.

**Input:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "error_id": "error-uuid-2",
  "feedback_type": "suggestion",
  "context": {
    "paragraph_id": "dabf1e89-d7a1-40be-864e-86700581187c",
    "error_type": "unsupported_claim"
  }
}
```

**Output:**
```json
{
  "id": "feedback-uuid-1",
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "document_version": 3,
  "error_id": "error-uuid-2",
  "feedback_type": "suggestion",
  "category": "evidence_needed",
  "title": "Add Supporting Evidence",
  "message": "Your claim that 'Personalized medicine will reduce healthcare costs by 40%' requires supporting evidence. Consider adding:\n\n1. Citations from peer-reviewed research\n2. Statistical data from healthcare organizations\n3. Case studies demonstrating cost reduction\n\nExample: 'According to a 2024 study by the Journal of Healthcare Economics, targeted genomic treatments have shown cost reductions of 35-45% in pilot programs (Smith et al., 2024).'",
  "suggestions": [
    "Add citation to support the 40% reduction claim",
    "Provide specific examples or case studies",
    "Reference authoritative sources (WHO, NIH, peer-reviewed journals)"
  ],
  "severity": "high",
  "status": "pending",
  "generated_by": "gpt-4",
  "created_at": "2025-10-23T11:25:30.123456Z"
}
```

**curl Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/feedback" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
    "error_id": "error-uuid-2",
    "feedback_type": "suggestion",
    "context": {
      "paragraph_id": "dabf1e89-d7a1-40be-864e-86700581187c",
      "error_type": "unsupported_claim"
    }
  }'
```

---

### 5.4 Get Feedback by Document
**GET** `/api/documents/{id}/feedback`

Return feedback entries linked to current document version.

**Input:** None (document ID in URL path, optional query params: `status`, `feedback_type`)

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "document_version": 3,
  "total_feedback": 4,
  "feedback": [
    {
      "id": "feedback-uuid-1",
      "feedback_type": "suggestion",
      "category": "evidence_needed",
      "title": "Add Supporting Evidence",
      "message": "Your claim that 'Personalized medicine will reduce healthcare costs by 40%' requires...",
      "severity": "high",
      "status": "pending",
      "error_id": "error-uuid-2",
      "location": {
        "paragraph_id": "dabf1e89-d7a1-40be-864e-86700581187c",
        "p_index": 3
      },
      "created_at": "2025-10-23T11:25:30.123456Z"
    },
    {
      "id": "feedback-uuid-2",
      "feedback_type": "improvement",
      "category": "clarity",
      "title": "Define Technical Term",
      "message": "Consider defining 'in silico' for readers unfamiliar with computational biology terminology.",
      "severity": "medium",
      "status": "applied",
      "error_id": "error-uuid-3",
      "location": {
        "paragraph_id": "f49f8ea7-1a67-45b3-8f40-b961939578b9",
        "p_index": 5
      },
      "created_at": "2025-10-23T11:26:15.234567Z",
      "action_taken_at": "2025-10-23T11:45:20.345678Z"
    },
    {
      "id": "feedback-uuid-3",
      "feedback_type": "warning",
      "category": "logical_flow",
      "title": "Improve Transition",
      "message": "The jump from medical imaging to personalized medicine needs a smoother transition.",
      "severity": "medium",
      "status": "dismissed",
      "location": {
        "paragraph_id": "4f59405d-53ae-4287-bbd7-605c4a469726",
        "p_index": 1
      },
      "created_at": "2025-10-23T11:27:00.456789Z",
      "action_taken_at": "2025-10-23T11:50:10.567890Z"
    }
  ]
}
```

**curl Example:**
```bash
curl -X GET "http://127.0.0.1:8000/api/documents/75d7780d-9342-4f07-84af-762319d18cc4/feedback?status=pending" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 5.5 Update User Action on Feedback
**PATCH** `/api/feedback/{id}/action`

Mark feedback as accepted, dismissed, or applied.

**Input:**
```json
{
  "action": "applied",
  "action_note": "Added citation from Smith et al. 2024 study"
}
```

**Output:**
```json
{
  "id": "feedback-uuid-1",
  "feedback_type": "suggestion",
  "category": "evidence_needed",
  "status": "applied",
  "action": "applied",
  "action_note": "Added citation from Smith et al. 2024 study",
  "created_at": "2025-10-23T11:25:30.123456Z",
  "action_taken_at": "2025-10-23T12:15:45.678901Z",
  "action_taken_by": "33d386ec-7b46-4b20-9669-51ce979565d4"
}
```

**curl Example:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/feedback/feedback-uuid-1/action" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "applied",
    "action_note": "Added citation from Smith et al. 2024 study"
  }'
```

---

## 6. Goal Alignment Dashboard

### 6.1 Get Rubric Coverage
**GET** `/api/documents/{id}/goal-coverage`

Return which rubric criteria are addressed in the document.

**Input:** None (document ID in URL path)

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "document_version": 3,
  "overall_coverage": 75.0,
  "last_computed": "2025-10-23T10:30:45.789012Z",
  "criteria_coverage": [
    {
      "criterion_id": "criterion-uuid-1",
      "label": "Clear thesis statement",
      "weight": 0.3,
      "is_mandatory": true,
      "is_covered": true,
      "coverage_score": 0.92,
      "evidence": {
        "paragraph_ids": ["e0dd0926-e761-462c-b0d6-4b46c860ebe0"],
        "sentence_ids": ["e860a69a-2cc6-4af7-b3b6-eb12325c35e1"],
        "matching_text": "Artificial intelligence is transforming the healthcare industry...",
        "confidence": 0.92
      }
    },
    {
      "criterion_id": "criterion-uuid-2",
      "label": "Strong evidence and citations",
      "weight": 0.4,
      "is_mandatory": true,
      "is_covered": true,
      "coverage_score": 0.68,
      "evidence": {
        "paragraph_ids": [
          "4f59405d-53ae-4287-bbd7-605c4a469726",
          "f49f8ea7-1a67-45b3-8f40-b961939578b9"
        ],
        "sentence_ids": [
          "52deab08-5d1a-460c-b374-d3f59aded904",
          "abc12345-def6-7890-ghij-klmnopqrstuv"
        ],
        "matching_text": "Machine learning algorithms can now analyze...",
        "confidence": 0.68
      }
    },
    {
      "criterion_id": "criterion-uuid-3",
      "label": "Logical flow and organization",
      "weight": 0.2,
      "is_mandatory": true,
      "is_covered": true,
      "coverage_score": 0.85,
      "evidence": {
        "paragraph_ids": ["all"],
        "structure_analysis": "Document follows logical progression from introduction through body to conclusion",
        "confidence": 0.85
      }
    },
    {
      "criterion_id": "criterion-uuid-4",
      "label": "Proper grammar and formatting",
      "weight": 0.1,
      "is_mandatory": true,
      "is_covered": false,
      "coverage_score": 0.45,
      "evidence": {
        "issues_found": ["Missing citations in APA format", "Inconsistent heading styles"],
        "confidence": 0.45
      }
    }
  ],
  "missing_criteria": [
    {
      "criterion_id": "criterion-uuid-4",
      "label": "Proper grammar and formatting",
      "weight": 0.1,
      "suggestion": "Review APA formatting guidelines and ensure consistent citation style throughout."
    }
  ]
}
```

**curl Example:**
```bash
curl -X GET "http://127.0.0.1:8000/api/documents/75d7780d-9342-4f07-84af-762319d18cc4/goal-coverage" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 6.2 Recompute Goal Alignment
**POST** `/api/documents/{id}/goal-coverage/recompute`

Run semantic matching and scoring to update goal alignment analysis.

**Input:**
```json
{
  "force_refresh": true,
  "include_suggestions": true
}
```

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "computation_status": "completed",
  "overall_coverage": 75.0,
  "previous_coverage": 68.0,
  "improvement": 7.0,
  "computed_at": "2025-10-23T12:30:15.123456Z",
  "computation_time_ms": 2450,
  "changes_detected": [
    {
      "criterion_id": "criterion-uuid-2",
      "label": "Strong evidence and citations",
      "previous_score": 0.55,
      "new_score": 0.68,
      "change": 0.13,
      "reason": "Added new evidence in paragraph 5"
    }
  ]
}
```

**curl Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/documents/75d7780d-9342-4f07-84af-762319d18cc4/goal-coverage/recompute" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "force_refresh": true,
    "include_suggestions": true
  }'
```

---

### 6.3 Get Rubric Criteria List
**GET** `/api/goals/{id}/criteria`

List extracted rubric items for a specific goal.

**Input:** None (goal ID in URL path)

**Output:**
```json
{
  "goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "total_criteria": 4,
  "total_weight": 1.0,
  "criteria": [
    {
      "id": "criterion-uuid-1",
      "goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "label": "Clear thesis statement",
      "description": "Clear thesis statement (30%)",
      "weight": 0.3,
      "order_index": 0,
      "is_mandatory": true
    },
    {
      "id": "criterion-uuid-2",
      "goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "label": "Strong evidence and citations",
      "description": "Strong evidence and citations (40%)",
      "weight": 0.4,
      "order_index": 1,
      "is_mandatory": true
    },
    {
      "id": "criterion-uuid-3",
      "goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "label": "Logical flow and organization",
      "description": "Logical flow and organization (20%)",
      "weight": 0.2,
      "order_index": 2,
      "is_mandatory": true
    },
    {
      "id": "criterion-uuid-4",
      "goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "label": "Proper grammar and formatting",
      "description": "Proper grammar and formatting (10%)",
      "weight": 0.1,
      "order_index": 3,
      "is_mandatory": true
    }
  ]
}
```

**curl Example:**
```bash
curl -X GET "http://127.0.0.1:8000/api/goals/3fa85f64-5717-4562-b3fc-2c963f66afa6/criteria" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 7. Analytics & Writing Insights

### 7.1 Start Writing Session
**POST** `/api/sessions/start`

Begin tracking a writing session.

**Input:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "session_type": "writing"
}
```

**Output:**
```json
{
  "session_id": "session-uuid-1",
  "user_id": "33d386ec-7b46-4b20-9669-51ce979565d4",
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "session_type": "writing",
  "started_at": "2025-10-23T13:00:00.000000Z",
  "initial_word_count": 298,
  "initial_error_count": 5
}
```

**curl Example:**
```bash
curl -X POST "http://127.0.0.1:8000/api/sessions/start" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
    "session_type": "writing"
  }'
```

---

### 7.2 End Writing Session
**PATCH** `/api/sessions/{id}/end`

Close session and record statistics.

**Input:**
```json
{
  "final_word_count": 350,
  "final_error_count": 2,
  "errors_fixed": 3
}
```

**Output:**
```json
{
  "session_id": "session-uuid-1",
  "user_id": "33d386ec-7b46-4b20-9669-51ce979565d4",
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "session_type": "writing",
  "started_at": "2025-10-23T13:00:00.000000Z",
  "ended_at": "2025-10-23T14:30:00.000000Z",
  "duration_minutes": 90,
  "initial_word_count": 298,
  "final_word_count": 350,
  "words_added": 52,
  "words_per_minute": 0.58,
  "initial_error_count": 5,
  "final_error_count": 2,
  "errors_fixed": 3,
  "new_errors_introduced": 0,
  "productivity_score": 85
}
```

**curl Example:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/sessions/session-uuid-1/end" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "final_word_count": 350,
    "final_error_count": 2,
    "errors_fixed": 3
  }'
```

---

### 7.3 Get Session History
**GET** `/api/sessions`

List all past writing sessions.

**Input:** None (optional query params: `limit`, `offset`, `document_id`)

**Output:**
```json
{
  "total_sessions": 15,
  "sessions": [
    {
      "session_id": "session-uuid-1",
      "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
      "document_title": "The Impact of Artificial Intelligence on Healthcare",
      "session_type": "writing",
      "started_at": "2025-10-23T13:00:00.000000Z",
      "ended_at": "2025-10-23T14:30:00.000000Z",
      "duration_minutes": 90,
      "words_added": 52,
      "errors_fixed": 3,
      "productivity_score": 85
    },
    {
      "session_id": "session-uuid-2",
      "document_id": "6426a9a3-396b-4b80-9fea-ec360409a326",
      "document_title": "Comprehensive Essay on Technology",
      "session_type": "editing",
      "started_at": "2025-10-22T10:15:00.000000Z",
      "ended_at": "2025-10-22T11:00:00.000000Z",
      "duration_minutes": 45,
      "words_added": 12,
      "errors_fixed": 7,
      "productivity_score": 92
    }
  ]
}
```

**curl Example:**
```bash
curl -X GET "http://127.0.0.1:8000/api/sessions?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 7.4 Get User Insights
**GET** `/api/analytics/user`

Aggregate user's writing stats and error frequencies.

**Input:** None (optional query params: `time_period` - e.g., "7d", "30d", "all")

**Output:**
```json
{
  "user_id": "33d386ec-7b46-4b20-9669-51ce979565d4",
  "time_period": "30d",
  "analytics_generated_at": "2025-10-23T15:00:00.000000Z",
  "writing_stats": {
    "total_sessions": 15,
    "total_writing_time_minutes": 720,
    "total_words_written": 3450,
    "average_words_per_session": 230,
    "average_session_duration_minutes": 48,
    "average_words_per_minute": 4.8,
    "most_productive_time": "morning (9am-12pm)"
  },
  "document_stats": {
    "total_documents": 5,
    "completed_documents": 2,
    "in_progress_documents": 3,
    "average_document_length": 550
  },
  "error_stats": {
    "total_errors_detected": 42,
    "total_errors_fixed": 35,
    "fix_rate": 83.3,
    "error_breakdown": {
      "contradictions": 8,
      "undefined_terms": 12,
      "unsupported_claims": 15,
      "logical_jumps": 7
    },
    "most_common_error": "unsupported_claims",
    "improvement_areas": [
      "Add more supporting evidence for claims",
      "Define technical terms on first use"
    ]
  },
  "goal_stats": {
    "total_goals": 3,
    "average_rubric_coverage": 72.5,
    "best_performing_criterion": "Logical flow and organization",
    "needs_improvement": ["Proper grammar and formatting"]
  },
  "productivity_trends": {
    "average_productivity_score": 78,
    "trend": "improving",
    "best_session_date": "2025-10-22",
    "best_session_score": 92
  }
}
```

**curl Example:**
```bash
curl -X GET "http://127.0.0.1:8000/api/analytics/user?time_period=30d" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 7.5 Get Document Progress Summary
**GET** `/api/analytics/document/{id}`

Return total errors, fixed vs unresolved, and rubric coverage percentage.

**Input:** None (document ID in URL path)

**Output:**
```json
{
  "document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
  "title": "The Impact of Artificial Intelligence on Healthcare",
  "version": 3,
  "word_count": 298,
  "created_at": "2025-10-21T09:25:43.546937Z",
  "last_updated": "2025-10-23T14:30:00.000000Z",
  "progress_summary": {
    "completion_percentage": 75,
    "status": "in_progress",
    "sections_complete": 5,
    "sections_total": 6
  },
  "error_summary": {
    "total_errors_detected": 8,
    "errors_resolved": 5,
    "errors_unresolved": 3,
    "resolution_rate": 62.5,
    "error_breakdown": {
      "contradictions": {
        "total": 2,
        "resolved": 1,
        "unresolved": 1
      },
      "undefined_terms": {
        "total": 2,
        "resolved": 2,
        "unresolved": 0
      },
      "unsupported_claims": {
        "total": 3,
        "resolved": 2,
        "unresolved": 1
      },
      "logical_jumps": {
        "total": 1,
        "resolved": 0,
        "unresolved": 1
      }
    }
  },
  "goal_alignment": {
    "goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "overall_coverage": 75.0,
    "criteria_met": 3,
    "criteria_total": 4,
    "missing_criteria": [
      "Proper grammar and formatting"
    ],
    "last_computed": "2025-10-23T12:30:15.123456Z"
  },
  "writing_activity": {
    "total_sessions": 3,
    "total_writing_time_minutes": 180,
    "last_session": "2025-10-23T14:30:00.000000Z",
    "words_added_last_session": 52
  },
  "recommendations": [
    "Resolve 1 remaining contradiction in paragraph 7",
    "Add evidence to support claim in paragraph 3",
    "Improve transition between paragraphs 1 and 3",
    "Review and apply APA formatting guidelines"
  ]
}
```

**curl Example:**
```bash
curl -X GET "http://127.0.0.1:8000/api/analytics/document/75d7780d-9342-4f07-84af-762319d18cc4" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

