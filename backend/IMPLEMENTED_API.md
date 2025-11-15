# LogicGuard API Reference Guide

This document specifies the input and output for completed API reference for LogicGuard backend.

✅ **Implemented Endpoints:**

**Authentication & User Management:**

- POST `/api/auth/register`
- POST `/api/auth/login`
- GET `/api/auth/me`
- PUT `/api/auth/me`

**Writing Type & Goal Setup:**

- GET `/api/writing-types/`
- GET `/api/writing-types/{id}`
- POST `/api/goals/`
- GET `/api/goals/`
- GET `/api/goals/{id}`
- DELETE `/api/goals/{id}`

**Writing Canvas & Document Management:**

- GET `/api/documents/`
- POST `/api/documents/`
- GET `/api/documents/{id}`
- PUT `/api/documents/{id}`
- DELETE `/api/documents/{id}`
- GET `/api/documents/{id}/sections`
- PUT `/api/documents/{id}/sections/{section_id}`
- GET `/api/documents/{id}/paragraphs`
- PUT `/api/documents/paragraphs/{id}`
- GET `/api/documents/paragraphs/{id}/sentences`

**Logic Quality Checks:**

- POST `/api/logic-checks/unsupported-claims`
- POST `/api/logic-checks/undefined-terms`
- POST `/api/logic-checks/contradictions`

🔄 **Placeholder (Coming Soon):**

- Analysis endpoints
- Feedback & error detection endpoints

---

## 1. Authentication & User Management

### 1.1 Register User

**POST** `/api/auth/register`

Create a new user account.

**Input:**

```json
{
	"email": "user@example.com",
	"password": "password123"
}
```

**Output:**

```json
{
	"id": "33d386ec-7b46-4b20-9669-51ce979565d4",
	"email": "user@example.com",
	"created_at": "2025-10-21T04:37:17.693078Z"
}
```

**curl Example:**

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

---

### 1.2 Login

**POST** `/api/auth/login`

Authenticate and receive JWT access token.

**Input:**

```json
{
	"email": "user@example.com",
	"password": "password123"
}
```

**Output:**

```json
{
	"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
	"token_type": "bearer",
	"user": {
		"id": "33d386ec-7b46-4b20-9669-51ce979565d4",
		"email": "user@example.com",
		"created_at": "2025-10-21T04:37:17.693078Z"
	}
}
```

**curl Example:**

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

---

### 1.3 Get Current User Profile

**GET** `/api/auth/me`

Retrieve authenticated user's profile information.

**Input:** None (requires Authorization header)

**Output:**

```json
{
	"id": "33d386ec-7b46-4b20-9669-51ce979565d4",
	"email": "user@example.com",
	"created_at": "2025-10-21T04:37:17.693078Z"
}
```

**curl Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 1.4 Update User Profile

**PUT** `/api/auth/me`

Update user email or password.

**Input:**

```json
{
	"email": "newemail@example.com",
	"password": "newpassword456"
}
```

**Output:**

```json
{
	"id": "33d386ec-7b46-4b20-9669-51ce979565d4",
	"email": "newemail@example.com",
	"created_at": "2025-10-21T04:37:17.693078Z"
}
```

**curl Example:**

```bash
curl -X PUT "http://127.0.0.1:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com"
  }'
```

---

## 2. Writing Type & Goal Setup (Context Setup)

### 2.1 List All Writing Types

**GET** `/api/writing-types/`

Fetch available writing templates (Essay, Proposal, Report, Pitch, Blog Post).

**Input:** None

**Output:**

```json
[
	{
		"id": "00000000-0000-0000-0000-000000000001",
		"name": "essay",
		"display_name": "Essay",
		"description": "Academic or personal essay with introduction, body paragraphs, and conclusion",
		"default_checks": {
			"check_thesis": true,
			"check_evidence": true,
			"check_transitions": true
		},
		"structure_template": {
			"sections": ["introduction", "body", "conclusion"],
			"min_paragraphs": 5
		}
	},
	{
		"id": "00000000-0000-0000-0000-000000000002",
		"name": "proposal",
		"display_name": "Proposal",
		"description": "Business or project proposal with problem, solution, and implementation plan",
		"default_checks": {
			"check_problem_statement": true,
			"check_solution_clarity": true,
			"check_feasibility": true
		},
		"structure_template": {
			"sections": [
				"executive_summary",
				"problem",
				"solution",
				"implementation",
				"budget"
			],
			"min_paragraphs": 8
		}
	}
]
```

**curl Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/writing-types/" \
  -H "accept: application/json"
```

---

### 2.2 Get Writing Type Detail

**GET** `/api/writing-types/{id}`

Retrieve section templates and default checks for a specific writing type.

**Input:** None (ID in URL path)

**Output:**

```json
{
	"id": "00000000-0000-0000-0000-000000000001",
	"name": "essay",
	"display_name": "Essay",
	"description": "Academic or personal essay with introduction, body paragraphs, and conclusion",
	"default_checks": {
		"check_thesis": true,
		"check_evidence": true,
		"check_transitions": true,
		"check_conclusion": true
	},
	"structure_template": {
		"sections": ["introduction", "body", "conclusion"],
		"min_paragraphs": 5,
		"recommended_word_count": 1500
	}
}
```

**curl Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/writing-types/00000000-0000-0000-0000-000000000001" \
  -H "accept: application/json"
```

---

### 2.3 Create New Goal

**POST** `/api/goals/`

Submit rubric text and key constraints. The API will automatically extract criteria using NLP.

**Input:**

```json
{
	"writing_type_custom": "Research Paper",
	"rubric_text": "1. Clear thesis statement (30%)\n2. Strong evidence and citations (40%)\n3. Logical flow and organization (20%)\n4. Proper grammar and formatting (10%)",
	"key_constraints": "Must be 5-7 pages, APA format, minimum 5 scholarly sources"
}
```

**Output:**

```json
{
	"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
	"user_id": "33d386ec-7b46-4b20-9669-51ce979565d4",
	"writing_type_custom": "Research Paper",
	"rubric_text": "1. Clear thesis statement (30%)\n2. Strong evidence and citations (40%)\n3. Logical flow and organization (20%)\n4. Proper grammar and formatting (10%)",
	"extracted_criteria": {
		"criteria": [
			{
				"label": "Clear thesis statement",
				"description": "Clear thesis statement (30%)",
				"weight": 0.3,
				"is_mandatory": true
			},
			{
				"label": "Strong evidence and citations",
				"description": "Strong evidence and citations (40%)",
				"weight": 0.4,
				"is_mandatory": true
			},
			{
				"label": "Logical flow and organization",
				"description": "Logical flow and organization (20%)",
				"weight": 0.2,
				"is_mandatory": true
			},
			{
				"label": "Proper grammar and formatting",
				"description": "Proper grammar and formatting (10%)",
				"weight": 0.1,
				"is_mandatory": true
			}
		],
		"total_criteria": 4,
		"extraction_method": "rule_based"
	},
	"key_constraints": "Must be 5-7 pages, APA format, minimum 5 scholarly sources",
	"created_at": "2025-10-21T04:30:32.105Z",
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
curl -X POST "http://127.0.0.1:8000/api/goals/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "writing_type_custom": "Research Paper",
    "rubric_text": "1. Clear thesis statement (30%)\n2. Strong evidence and citations (40%)\n3. Logical flow and organization (20%)\n4. Proper grammar and formatting (10%)",
    "key_constraints": "Must be 5-7 pages, APA format, minimum 5 scholarly sources"
  }'
```

---

## 3. Logic Quality Checks

These endpoints expose the AI micro-services now powering the unsupported-claim, undefined-term, and contradiction checks that the frontend canvas needs.

### 3.1 Unsupported Claims

**POST** `/api/logic-checks/unsupported-claims`

**Input:**

```json
{
	"context": {
		"writing_type": "Technical Proposal",
		"main_goal": "Chứng minh NoSQL có khả năng mở rộng tốt hơn",
		"criteria": ["nhắc đến scalability", "có luận cứ kỹ thuật"],
		"constraints": ["word_limit: 1000"]
	},
	"content": "Nội dung bài viết"
}
```

**Output (truncated):**

```json
{
	"success": true,
	"total_claims_found": 4,
	"total_unsupported": 2,
	"unsupported_claims": [
		{
			"claim": "AI can perfectly predict human emotions.",
			"status": "unsupported",
			"suggestion": "Add source, data, or example to support this claim."
		}
	],
	"supported_claims": [],
	"metadata": {
		"model": "gemini-2.5-flash"
	}
}
```

### 3.2 Undefined Terms

**POST** `/api/logic-checks/undefined-terms`

Request body matches the unsupported-claims endpoint (`context` + `content`). The response contains `total_terms_found`, `total_undefined`, along with `undefined_terms`/`defined_terms` arrays describing each detected entity and whether a definition exists around its first mention.

### 3.3 Contradictions

**POST** `/api/logic-checks/contradictions`

**Input (defaults shown):**

```json
{
	"text": "Sentence A. Sentence B.",
	"mode": "finetuned",
	"threshold": 0.75,
	"use_embeddings_filter": true,
	"embedding_model_name": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
	"top_k": 50,
	"sim_min": 0.3,
	"sim_max": 0.98,
	"batch_size": 8,
	"max_length": 128
}
```

**Output (abridged):**

```json
{
	"success": true,
	"mode": "finetuned",
	"total_sentences": 5,
	"total_contradictions": 1,
	"contradictions": [
		{
			"id": 1,
			"sentence1": "Q1 revenue dropped 20%",
			"sentence2": "Revenue has grown every quarter",
			"confidence": 0.82,
			"boosted": true
		}
	]
}
```

Every endpoint requires authentication (Bearer token). The backend returns `success: false` plus `metadata.error` if the underlying model fails so the frontend can display actionable messaging.

---

### 2.4 List User Goals

**GET** `/api/goals/`

List all goals created by the authenticated user.

**Input:** None (requires Authorization header)

**Output:**

```json
[
	{
		"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
		"user_id": "33d386ec-7b46-4b20-9669-51ce979565d4",
		"writing_type_custom": "Research Paper",
		"rubric_text": "1. Clear thesis statement (30%)...",
		"key_constraints": "Must be 5-7 pages, APA format, minimum 5 scholarly sources",
		"created_at": "2025-10-21T04:30:32.105Z"
	},
	{
		"id": "5bc95f74-6828-5673-c4gd-3d074g77bgb7",
		"user_id": "33d386ec-7b46-4b20-9669-51ce979565d4",
		"writing_type_custom": "Essay",
		"rubric_text": "1. Introduction with thesis (25%)...",
		"key_constraints": "750-1000 words, MLA format",
		"created_at": "2025-10-21T05:15:20.332Z"
	}
]
```

**curl Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/goals/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 2.5 Get Goal Detail

**GET** `/api/goals/{id}`

Retrieve goal details including extracted criteria and rubric structure.

**Input:** None (ID in URL path, requires Authorization header)

**Output:**

```json
{
	"id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
	"user_id": "33d386ec-7b46-4b20-9669-51ce979565d4",
	"writing_type_custom": "Research Paper",
	"rubric_text": "1. Clear thesis statement (30%)\n2. Strong evidence and citations (40%)\n3. Logical flow and organization (20%)\n4. Proper grammar and formatting (10%)",
	"extracted_criteria": {
		"criteria": [
			{
				"label": "Clear thesis statement",
				"description": "Clear thesis statement (30%)",
				"weight": 0.3,
				"is_mandatory": true
			}
		],
		"total_criteria": 4,
		"extraction_method": "rule_based"
	},
	"key_constraints": "Must be 5-7 pages, APA format, minimum 5 scholarly sources",
	"created_at": "2025-10-21T04:30:32.105Z",
	"criteria": [
		{
			"id": "criterion-uuid-1",
			"goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
			"label": "Clear thesis statement",
			"description": "Clear thesis statement (30%)",
			"weight": 0.3,
			"order_index": 0,
			"is_mandatory": true
		}
	]
}
```

**curl Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/goals/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 2.6 Delete Goal

**DELETE** `/api/goals/{id}`

Remove a goal and all linked rubric criteria.

**Input:** None (ID in URL path, requires Authorization header)

**Output:** `204 No Content`

**curl Example:**

```bash
curl -X DELETE "http://127.0.0.1:8000/api/goals/3fa85f64-5717-4562-b3fc-2c963f66afa6" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 3. Writing Canvas & Document Management

### 3.1 List Documents

**GET** `/api/documents/`

Get all documents for the authenticated user.

**Input:** None (requires Authorization header)

**Output:**

```json
[
	{
		"id": "75d7780d-9342-4f07-84af-762319d18cc4",
		"title": "The Impact of Artificial Intelligence on Healthcare",
		"word_count": 298,
		"created_at": "2025-10-21T09:25:43.546937Z",
		"updated_at": "2025-10-21T09:25:43.546937Z"
	},
	{
		"id": "6426a9a3-396b-4b80-9fea-ec360409a326",
		"title": "Comprehensive Essay on Technology",
		"word_count": 137,
		"created_at": "2025-10-21T08:44:42.327575Z",
		"updated_at": "2025-10-21T09:08:34.536302Z"
	}
]
```

**curl Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/documents/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 3.2 Create Document

**POST** `/api/documents/`

Create a new document with optional goal association.

**Input:**

```json
{
	"title": "My Research Paper",
	"content_full": "This is the beginning of my research paper on artificial intelligence...",
	"goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
}
```

**Output:**

```json
{
	"id": "89c7890e-1234-5678-90ab-cdef12345678",
	"user_id": "33d386ec-7b46-4b20-9669-51ce979565d4",
	"goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
	"title": "My Research Paper",
	"content_full": "This is the beginning of my research paper on artificial intelligence...",
	"version": 1,
	"word_count": 12,
	"created_at": "2025-10-21T10:30:15.123456Z",
	"updated_at": "2025-10-21T10:30:15.123456Z"
}
```

**curl Example:**

```bash
curl -X POST "http://127.0.0.1:8000/api/documents/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Research Paper",
    "content_full": "This is the beginning of my research paper...",
    "goal_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6"
  }'
```

---

### 3.3 Get Document

**GET** `/api/documents/{id}`

Retrieve a specific document with full content.

**Input:** None (ID in URL path, requires Authorization header)

**Output:**

```json
{
	"id": "75d7780d-9342-4f07-84af-762319d18cc4",
	"user_id": "33d386ec-7b46-4b20-9669-51ce979565d4",
	"goal_id": null,
	"title": "The Impact of Artificial Intelligence on Healthcare",
	"content_full": "Artificial intelligence is transforming the healthcare industry in unprecedented ways. From diagnostic tools to treatment planning, AI systems are becoming integral to modern medical practice.\n\nOne of the most significant applications of AI in healthcare is in medical imaging and diagnostics...",
	"version": 1,
	"word_count": 298,
	"created_at": "2025-10-21T09:25:43.546937Z",
	"updated_at": "2025-10-21T09:25:43.546937Z"
}
```

**curl Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/documents/75d7780d-9342-4f07-84af-762319d18cc4" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 3.4 Update Document

**PUT** `/api/documents/{id}`

Update document title, content, or goal association. Version automatically increments.

**Input:**

```json
{
	"title": "Updated Title: AI in Healthcare",
	"content_full": "Updated content with new paragraphs and research findings..."
}
```

**Output:**

```json
{
	"id": "75d7780d-9342-4f07-84af-762319d18cc4",
	"user_id": "33d386ec-7b46-4b20-9669-51ce979565d4",
	"goal_id": null,
	"title": "Updated Title: AI in Healthcare",
	"content_full": "Updated content with new paragraphs and research findings...",
	"version": 2,
	"word_count": 156,
	"created_at": "2025-10-21T09:25:43.546937Z",
	"updated_at": "2025-10-21T11:45:22.789012Z"
}
```

**curl Example:**

```bash
curl -X PUT "http://127.0.0.1:8000/api/documents/75d7780d-9342-4f07-84af-762319d18cc4" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title: AI in Healthcare",
    "content_full": "Updated content with new paragraphs..."
  }'
```

---

### 3.5 Delete Document

**DELETE** `/api/documents/{id}`

Permanently delete a document.

**Input:** None (ID in URL path, requires Authorization header)

**Output:** `204 No Content`

**curl Example:**

```bash
curl -X DELETE "http://127.0.0.1:8000/api/documents/75d7780d-9342-4f07-84af-762319d18cc4" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 3.6 List Document Sections

**GET** `/api/documents/{document_id}/sections`

Get all sections for a document (e.g., Introduction, Body paragraphs, Conclusion).

**Input:** None (document_id in URL path, requires Authorization header)

**Output:**

```json
[
	{
		"id": "d72b31b3-6b68-4123-bc99-35c9e2e67580",
		"document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
		"section_type": "intro",
		"section_label": "Introduction",
		"order_index": 0,
		"is_complete": true
	},
	{
		"id": "ad5aa8e7-f387-4098-b8a4-9d9cb2bcebf9",
		"document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
		"section_type": "body",
		"section_label": "Medical Imaging and Diagnostics",
		"order_index": 1,
		"is_complete": true
	},
	{
		"id": "e98d0a28-55b2-4efb-a90b-2fef776e18ed",
		"document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
		"section_type": "body",
		"section_label": "Ethical Considerations",
		"order_index": 4,
		"is_complete": false
	}
]
```

**curl Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/documents/75d7780d-9342-4f07-84af-762319d18cc4/sections" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 3.7 Update Section Status

**PUT** `/api/documents/{document_id}/sections/{section_id}`

Mark a section as complete or incomplete.

**Input:**

```json
{
	"is_complete": true
}
```

**Output:**

```json
{
	"id": "e98d0a28-55b2-4efb-a90b-2fef776e18ed",
	"document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
	"section_type": "body",
	"section_label": "Ethical Considerations",
	"order_index": 4,
	"is_complete": true
}
```

**curl Example:**

```bash
curl -X PUT "http://127.0.0.1:8000/api/documents/75d7780d-9342-4f07-84af-762319d18cc4/sections/e98d0a28-55b2-4efb-a90b-2fef776e18ed" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_complete": true
  }'
```

---

### 3.8 List Document Paragraphs

**GET** `/api/documents/{document_id}/paragraphs`

Get all paragraphs in a document.

**Input:** None (document_id in URL path, requires Authorization header)

**Output:**

```json
[
	{
		"id": "e0dd0926-e761-462c-b0d6-4b46c860ebe0",
		"document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
		"section_id": "d72b31b3-6b68-4123-bc99-35c9e2e67580",
		"p_index": 0,
		"text": "Artificial intelligence is transforming the healthcare industry in unprecedented ways. From diagnostic tools to treatment planning, AI systems are becoming integral to modern medical practice.",
		"word_count": 26,
		"emb": null,
		"updated_at": "2025-10-21T09:27:07.350353Z"
	},
	{
		"id": "4f59405d-53ae-4287-bbd7-605c4a469726",
		"document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
		"section_id": "ad5aa8e7-f387-4098-b8a4-9d9cb2bcebf9",
		"p_index": 1,
		"text": "One of the most significant applications of AI in healthcare is in medical imaging and diagnostics. Machine learning algorithms can now analyze X-rays, MRIs, and CT scans with accuracy that rivals or exceeds human radiologists.",
		"word_count": 38,
		"emb": null,
		"updated_at": "2025-10-21T09:27:07.351118Z"
	}
]
```

**curl Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/documents/75d7780d-9342-4f07-84af-762319d18cc4/paragraphs" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

### 3.9 Update Paragraph

**PUT** `/api/documents/paragraphs/{paragraph_id}`

Update paragraph text or embeddings.

**Input:**

```json
{
	"text": "This is the updated paragraph text with new content and analysis.",
	"emb": [0.123, 0.456, 0.789]
}
```

**Output:**

```json
{
	"id": "e0dd0926-e761-462c-b0d6-4b46c860ebe0",
	"document_id": "75d7780d-9342-4f07-84af-762319d18cc4",
	"section_id": "d72b31b3-6b68-4123-bc99-35c9e2e67580",
	"p_index": 0,
	"text": "This is the updated paragraph text with new content and analysis.",
	"word_count": 11,
	"emb": [0.123, 0.456, 0.789],
	"updated_at": "2025-10-21T12:15:45.678901Z"
}
```

**curl Example:**

```bash
curl -X PUT "http://127.0.0.1:8000/api/documents/paragraphs/e0dd0926-e761-462c-b0d6-4b46c860ebe0" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is the updated paragraph text with new content and analysis."
  }'
```

---

### 3.10 List Paragraph Sentences

**GET** `/api/documents/paragraphs/{paragraph_id}/sentences`

Get all sentences in a paragraph with their roles (claim, evidence, transition, etc.).

**Input:** None (paragraph_id in URL path, requires Authorization header)

**Output:**

```json
[
	{
		"id": "e860a69a-2cc6-4af7-b3b6-eb12325c35e1",
		"paragraph_id": "4f59405d-53ae-4287-bbd7-605c4a469726",
		"s_index": 0,
		"text": "One of the most significant applications of AI in healthcare is in medical imaging and diagnostics.",
		"role": "claim",
		"confidence_score": null
	},
	{
		"id": "52deab08-5d1a-460c-b374-d3f59aded904",
		"paragraph_id": "4f59405d-53ae-4287-bbd7-605c4a469726",
		"s_index": 1,
		"text": "Machine learning algorithms can now analyze X-rays, MRIs, and CT scans with accuracy that rivals or exceeds human radiologists.",
		"role": "evidence",
		"confidence_score": null
	}
]
```

**curl Example:**

```bash
curl -X GET "http://127.0.0.1:8000/api/documents/paragraphs/4f59405d-53ae-4287-bbd7-605c4a469726/sentences" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 4. Analysis Endpoints (Placeholder)

### 4.1 Analyze Document

**POST** `/api/analysis/documents/{document_id}/analyze`

_Coming soon: Run NLP analysis on document structure, logic, and coherence._

---

### 4.2 Get Analysis Results

**GET** `/api/analysis/runs/{run_id}`

_Coming soon: Retrieve detailed analysis results._

---

## 5. Feedback & Error Detection (Placeholder)

### 5.1 Get Document Errors

**GET** `/api/feedback/documents/{document_id}/errors`

_Coming soon: List all detected logic errors and issues._

---

### 5.2 Get Error Feedback

**GET** `/api/feedback/errors/{error_id}/feedback`

_Coming soon: Get detailed feedback and suggestions for a specific error._

---

## 6. NLP Criteria Extraction

The API automatically extracts criteria from your rubric text using pattern matching:

**Supported Formats:**

- Numbered lists: `1.`, `2.`, `3.`
- Bullet points: `-`, `*`, `•`
- Percentages: `(30%)`, `30%`
- Weight notation: `weight: 0.3`
- Optional markers: Text containing "optional" will be marked as non-mandatory

**Example Rubric:**

```
1. Clear thesis statement (30%)
2. Strong evidence and citations (40%)
3. Logical organization (20%)
- Optional: Creative writing style (10%)
```

**Extracted Criteria:**

```json
{
	"criteria": [
		{ "label": "Clear thesis statement", "weight": 0.3, "is_mandatory": true },
		{
			"label": "Strong evidence and citations",
			"weight": 0.4,
			"is_mandatory": true
		},
		{ "label": "Logical organization", "weight": 0.2, "is_mandatory": true },
		{ "label": "Creative writing style", "weight": 0.1, "is_mandatory": false }
	]
}
```
