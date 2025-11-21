"""
promptStore.py

Chứa các prompt dùng cho:
- Undefined Terms (EN-only endpoint)
- Unsupported Claims (EN-only endpoint)
- Unified Analysis EN (4 + 1 subtasks: contradictions, undefined terms, unsupported claims,
  logical jumps, spelling errors)
- Unified Analysis VI (5 subtasks tương tự, tiếng Việt)

Lưu ý quan trọng:
- Các prompt unified (prompt_analysis, prompt_analysis_vi) có thêm block "spelling_errors"
  trong JSON ví dụ. Nếu bạn muốn Gemini trả ra đúng block này và vẫn dùng
  GenerationConfig(response_schema=...), bạn cần:
    1) Thêm trường "spelling_errors" vào RESPONSE_SCHEMA trong Analysis.py
    2) Hoặc bỏ response_schema, chỉ dùng response_mime_type="application/json"
- Nếu hiện tại schema của bạn CHƯA có "spelling_errors", Gemini sẽ cố gắng bám theo schema,
  và có thể bỏ qua phần đó trong prompt. Khi đó bạn vẫn có thể dùng rule-based spelling
  từ term_normalizer.py thông qua metadata.spelling_errors như bạn đã làm.
"""

from typing import Dict, Any


# ==============================
# 1. UNDEFINED TERMS (EN ONLY)
# ==============================

def prompt_undefined_terms(context: Dict[str, Any], content: str) -> str:
    """
    Prompt phân tích THUẬT NGỮ CHƯA ĐỊNH NGHĨA (Undefined Terms) – tiếng Anh.
    Dùng riêng khi bạn muốn gọi API chỉ cho undefined terms.

    Lưu ý đặc biệt:
    - KHÔNG được coi các lỗi chính tả hiển nhiên (deeplearnnig, algoritm, platfomr, tạoo, ...)
      là "thuật ngữ". Nếu bạn nghi ngờ đó chỉ là typo, hãy BỎ QUA, KHÔNG đưa vào undefined_terms.
    - Chỉ coi là undefined term nếu nó có vẻ là:
      + tên mô hình, tên hệ thống, tên sản phẩm, tên module
      + khái niệm kỹ thuật, từ viết tắt, thuật ngữ domain-specific
    """

    writing_type = context.get("writing_type", "Document")
    main_goal = context.get("main_goal", "")
    criteria = context.get("criteria", [])
    constraints = context.get("constraints", [])

    context_lines = []
    context_lines.append(f"Writing Type: {writing_type}")
    if main_goal:
        context_lines.append(f"Main Goal: {main_goal}")
    if criteria:
        formatted_criteria = "\n".join(f"  - {item}" for item in criteria)
        context_lines.append(f"Criteria:\n{formatted_criteria}")
    if constraints:
        formatted_constraints = "\n".join(f"  - {item}" for item in constraints)
        context_lines.append(f"Constraints:\n{formatted_constraints}")

    context_block = "\n".join(context_lines)

    prompt = f"""You are LogicGuard, an expert technical writing analyst specialized in identifying undefined terminology in {writing_type} documents.

### Task Overview
Your task is to identify all technical terms, specialized concepts, acronyms, and domain-specific vocabulary that appear in the document WITHOUT proper definition or explanation at their first occurrence.

You MUST NOT treat obvious spelling mistakes as technical terms.
Examples of spelling mistakes that should NOT be returned as undefined terms:
- "deeplearnnig" instead of "deep learning"
- "algoritm" instead of "algorithm"
- "databaes" instead of "database"
- "platfomr" instead of "platform"
- "tạoo" instead of "tạo"

If a word clearly looks like a typo for a common word, IGNORE it here and do NOT include it in undefined_terms.

### Context Information
{context_block}

### Document Content
<<<BEGIN DOCUMENT>>>
{content}
<<<END DOCUMENT>>>

### Definition Patterns to Look For
When checking if a term is defined, look for these patterns at or near the first occurrence:
- "X is..."
- "X is defined as..."
- "X means..."
- "X (short for ...)"
- "X, also known as..."
- Parenthetical explanations immediately after the term
- Contextual clues that make the meaning clear to a general audience

### Instructions
1. Read through the entire document and identify ALL specialized terms, technical concepts, acronyms, and domain-specific vocabulary.
2. For each term found:
   - Locate its FIRST occurrence in the document.
   - Check if there is a definition or explanation at or near that occurrence.
   - Note the paragraph or section where it first appears.
3. Flag terms that are NOT adequately defined for a general reader.
4. Consider the document type: {writing_type} - some terms may be assumed knowledge for the expected audience.
5. DO NOT include plain spelling errors as undefined terms.

### Output Format
Return ONLY valid JSON in this exact structure:
{{
    "total_terms_found": <number>,
    "undefined_terms": [
        {{
            "term": "gradient clipping",
            "first_appeared": "Paragraph 3",
            "context_snippet": "Short excerpt showing where the term appears",
            "is_defined": false,
            "reason": "Term appears without explanation or definition pattern"
        }},
        {{
            "term": "NoSQL",
            "first_appeared": "Paragraph 1",
            "context_snippet": "NoSQL databases provide better scalability...",
            "is_defined": false,
            "reason": "Acronym used without expansion or explanation"
        }}
    ],
    "defined_terms": [
        {{
            "term": "scalability",
            "first_appeared": "Paragraph 2",
            "context_snippet": "scalability, which is the ability to handle...",
            "is_defined": true,
            "definition_found": "which is the ability to handle increasing workloads"
        }}
    ]
}}

### Important Notes
- Include BOTH undefined_terms and defined_terms for transparency.
- Be thorough but avoid false positives (common terms don't need definition).
- Consider the intended audience's expected knowledge level.
- Focus on domain-specific terminology that requires clarification.
- Paragraph numbers should match the logical structure of the document.
- DO NOT include obvious spelling mistakes in undefined_terms.

Return ONLY the JSON output. Do not include any markdown code blocks, commentary, or explanations outside the JSON structure.
"""
    return prompt


# =======================================
# 2. UNSUPPORTED CLAIMS (EN ONLY)
# =======================================

def prompt_unsupported_claims(context: Dict[str, Any], content: str) -> str:
    """
    Prompt phân tích LUẬN ĐIỂM THIẾU CHỨNG CỨ (Unsupported Claims) – tiếng Anh.
    Dùng riêng khi muốn gọi API chỉ cho unsupported claims.
    """

    writing_type = context.get("writing_type", "Document")
    main_goal = context.get("main_goal", "")
    criteria = context.get("criteria", [])
    constraints = context.get("constraints", [])

    context_lines = []
    context_lines.append(f"Writing Type: {writing_type}")
    if main_goal:
        context_lines.append(f"Main Goal: {main_goal}")
    if criteria:
        formatted_criteria = "\n".join(f"  - {item}" for item in criteria)
        context_lines.append(f"Criteria:\n{formatted_criteria}")
    if constraints:
        formatted_constraints = "\n".join(f"  - {item}" for item in constraints)
        context_lines.append(f"Constraints:\n{formatted_constraints}")

    context_block = "\n".join(context_lines)

    prompt = f"""You are LogicGuard, an expert writing analyst specialized in identifying unsupported claims in {writing_type} documents.

### Task Overview
Your task is to identify claims, assertions, or statements that lack adequate supporting evidence such as data, examples, citations, or logical reasoning.

### Context Information
{context_block}

### Document Content
<<<BEGIN DOCUMENT>>>
{content}
<<<END DOCUMENT>>>

### What Constitutes a Claim
A claim is a statement that:
- Makes an assertion about facts, trends, or relationships.
- Presents an opinion as if it were fact.
- Makes predictions or generalizations.
- States cause-and-effect relationships.
- Compares or evaluates things.

### What Constitutes Evidence
Evidence includes:
- Data/Statistics: Numbers, percentages, measurements, research findings.
- Examples: Specific instances, case studies, real-world scenarios.
- Citations: References to studies, experts, publications, or authoritative sources.
- Logical reasoning: Step-by-step explanations that build on established facts.
- Quotations: Direct statements from credible sources.
- Visual data: Graphs, charts, tables (when mentioned).

### Evidence Proximity Rule
A claim is considered "supported" if evidence appears:
- In the same sentence,
- Within ±2 sentences (before or after the claim),
- Or in the same paragraph with clear connection to the claim.

### Instructions
1. Read through the document sentence by sentence.
2. Identify all claims (assertive statements that require support).
3. For each claim:
   - Check if there is supporting evidence within ±2 sentences.
   - Evaluate if the evidence is sufficient and relevant.
   - Classify as "supported", "weakly_supported", or "unsupported".
4. For unsupported or weakly supported claims, provide specific suggestions for improvement.

### Output Format
Return ONLY valid JSON in this exact structure:
{{
    "total_claims_found": <number>,
    "unsupported_claims": [
        {{
            "claim": "AI can perfectly predict human emotions.",
            "location": "Paragraph 2, Sentence 3",
            "status": "unsupported",
            "reason": "No data, research, or examples provided to support this absolute claim",
            "surrounding_context": "Brief excerpt showing the claim in context...",
            "suggestion": "Add source, data, or example to support this claim. Consider: cite research studies, provide statistical evidence, or qualify the statement."
        }},
        {{
            "claim": "NoSQL databases are always faster than SQL databases.",
            "location": "Paragraph 3, Sentence 1",
            "status": "unsupported",
            "reason": "Absolute claim with no comparative data or benchmarks provided",
            "surrounding_context": "NoSQL databases are always faster than SQL databases. They scale better too...",
            "suggestion": "Provide benchmark data, specify use cases, or cite performance studies. Avoid absolute terms without evidence."
        }}
    ],
    "supported_claims": [
        {{
            "claim": "According to Smith (2023), machine learning models achieve 85% accuracy.",
            "location": "Paragraph 1, Sentence 2",
            "status": "supported",
            "evidence_type": "citation with data",
            "evidence": "References Smith (2023) and provides specific accuracy metric"
        }},
        {{
            "claim": "The system reduced processing time by 40%.",
            "location": "Paragraph 4, Sentence 5",
            "status": "supported",
            "evidence_type": "data/measurement",
            "evidence": "Specific quantifiable metric provided"
        }}
    ]
}}

### Important Guidelines
- Be strict but fair: claims need evidence, but obvious facts don't.
- Consider the writing type: {writing_type} may have different evidence standards.
- Watch for weasel words: "probably", "might", "could" don't magically make a claim acceptable.
- Absolute statements: "always", "never", "all", "none" require strong evidence.
- Comparative claims: "better", "faster", "more efficient" need comparative data.
- Causal claims: "causes", "leads to", "results in" need logical or empirical support.
- Common knowledge: well-established facts don't always need citations.

Return ONLY the JSON output. Do not include any markdown code blocks, commentary, or explanations outside the JSON structure.
"""
    return prompt


# =======================================
# 3. UNIFIED ANALYSIS – ENGLISH
# =======================================

def prompt_analysis(context: Dict[str, Any], content: str) -> str:
    """
    Unified English prompt:
    - Runs 5 subtasks in one call:
      1) Contradictions
      2) Undefined Terms
      3) Unsupported Claims
      4) Logical Jumps
      5) Spelling Errors (EN + VI within the document)
    """

    writing_type = context.get("writing_type", "Document")
    main_goal = context.get("main_goal", "")
    criteria = context.get("criteria", [])
    constraints = context.get("constraints", [])

    context_lines = []
    context_lines.append(f"Writing Type: {writing_type}")
    if main_goal:
        context_lines.append(f"Main Goal: {main_goal}")
    if criteria:
        context_lines.append("Criteria:")
        for c in criteria:
            context_lines.append(f"  - {c}")
    if constraints:
        context_lines.append("Constraints:")
        for r in constraints:
            context_lines.append(f"  - {r}")
    context_block = "\n".join(context_lines)

    prompt = f"""
You are LogicGuard, an AI assistant specialized in logical and structural analysis of {writing_type} documents.

Your mission: analyse the document along 5 dimensions:
1) Contradictions
2) Undefined Terms
3) Unsupported Claims
4) Logical Jumps
5) Spelling Errors (English + Vietnamese)

You receive:
- CONTEXT: high-level info about the writing task.
- CONTENT: the full original document as a plain string.

IMPORTANT GLOBAL RULES:
- You MUST return ONLY ONE JSON object.
- The JSON MUST be valid (no trailing commas, no comments).
- Do NOT wrap the JSON in markdown (no ```).
- Do NOT output any explanation text outside of the JSON.
- ALL positions (start_pos, end_pos) for spelling errors are 0-based character indices
  on the ORIGINAL CONTENT string exactly as given in the DOCUMENT block.
- end_pos is exclusive (same convention as Python slicing: content[start_pos:end_pos]).
- Do NOT treat brand names or clearly intentional product/model names as spelling errors
  (e.g., "iPhone", "YouTube", "Z-Trax", "NeuroLearn-X", etc.).

------------------------------------------
### CONTEXT
{context_block}

------------------------------------------
### DOCUMENT (CONTENT STRING TO ANALYSE)
<<<BEGIN DOCUMENT>>>
{content}
<<<END DOCUMENT>>>

You MUST use this exact CONTENT above to:
- Detect contradictions, undefined terms, unsupported claims, logical jumps.
- Detect spelling errors (both English and Vietnamese).
- Compute all start_pos / end_pos for spelling_errors.

------------------------------------------
### SUBTASK 1 – CONTRADICTIONS

- Find pairs of statements (sentences) that cannot both be true.
- Look for conflicting facts, numbers, dates, events, or strong opinions that directly oppose each other.
- For each contradiction item:
  - sentence1, sentence2: full sentences from CONTENT.
  - sentence1_location, sentence2_location: short descriptions like "Paragraph 1, Sentence 2".
  - contradiction_type: short label, e.g. "factual", "numerical", "temporal", "logical".
  - severity: one of ["high", "medium", "low"].
  - explanation: 1–3 sentences explaining why they contradict.
  - suggestion: concrete suggestion to resolve or clarify the conflict.
- total_found MUST equal the length of items.

------------------------------------------
### SUBTASK 2 – UNDEFINED TERMS

- Find technical terms, acronyms, model names, product names, or domain-specific concepts
  that are important but NOT clearly defined at first use.
- A term is considered "defined" if:
  - It has an explicit definition (e.g., "X is...", "X means..."), OR
  - It has a short explanation in parentheses, OR
  - The meaning is very clear for the expected audience.
- Do NOT treat obvious spelling mistakes as undefined terms.
- For each undefined term item:
  - term: exact substring from CONTENT (respect original casing, accents, etc.).
  - first_appeared: location like "Paragraph 2, Sentence 1".
  - context_snippet: short snippet (< 150 chars) around the first occurrence.
  - is_defined: usually false for undefined terms; may be true for partially defined but still unclear.
  - reason: why this term is considered undefined or unclear.
  - suggestion: how the author could define or clarify it.
- total_found MUST equal the length of items.

------------------------------------------
### SUBTASK 3 – UNSUPPORTED CLAIMS

A claim is:
- A statement that asserts something about reality, trends, relationships, predictions, comparisons, or causes.

Evidence can be:
- Data, statistics, examples, citations, or explicit reasoning.

A claim is "supported" ONLY IF:
- There is evidence in the same sentence, OR
- Within ±2 sentences, OR
- Clearly in the same paragraph and explicitly connected.

For each unsupported claim item:
- claim: the main sentence or clause.
- location: e.g., "Paragraph 3, Sentence 2".
- status: one of ["unsupported", "weak", "partially_supported"].
- claim_type: e.g. "absolute", "comparative", "causal", "predictive".
- reason: why the support is missing or weak.
- surrounding_context: short snippet around the claim.
- suggestion: what kind of evidence or rephrasing would fix it.

total_found MUST equal the length of items.

------------------------------------------
### SUBTASK 4 – LOGICAL JUMPS

- Inspect transitions between paragraphs.
- A logical jump occurs when the topic or reasoning changes abruptly
  without any clear bridge sentence, explanation, or justification.
- For each item:
  - from_paragraph: 1-based index of the source paragraph.
  - to_paragraph: 1-based index of the target paragraph.
  - from_paragraph_summary: 1–2 sentence summary of the source paragraph.
  - to_paragraph_summary: 1–2 sentence summary of the target paragraph.
  - coherence_score: float between 0 and 1 (1 = very coherent, 0 = no connection).
  - flag: short label like "abrupt_topic_shift" or "missing_explanation".
  - severity: one of ["high", "medium", "low"] (based on how harmful the jump is).
  - explanation: why this is considered a logical jump.
  - suggestion: how to add a bridge or restructure paragraphs.
- Only include items where coherence_score < 0.7.
- total_found MUST equal the length of items.

------------------------------------------
### SUBTASK 5 – SPELLING ERRORS (EN + VI)

- Detect spelling mistakes in both English and Vietnamese in the CONTENT.
- Include common typos, extra letters, missing letters, swapped letters,
  or obviously wrong spellings of common words or phrases.
- BE CONSERVATIVE:
  - Do NOT "correct" brand names, product names, or custom model names
    if they look intentional (e.g., "iPhone", "YouTube", "NavierGreen", "Z-Trax").
  - Do NOT "correct" technical AI terms unless they are clearly misspelled
    (e.g., "deeplearnnig" → "deep learning").
  - If you are uncertain whether a word is wrong, DO NOT mark it as an error.
- Examples of words that SHOULD be flagged as spelling errors:
  - "deeplearnnig" → "deep learning"
  - "databaes" → "database"
  - "algoritm" → "algorithm"
  - "platfomr" → "platform"
  - "tạoo" → "tạo" (when used in a Vietnamese sentence about "trí tuệ nhân tạoo")
- For each spelling error item:
  - original: exact substring from CONTENT that is misspelled.
  - suggested: corrected spelling.
  - start_pos: 0-based character index in CONTENT where the misspelled substring starts.
  - end_pos: exclusive 0-based index where it ends (like content[start_pos:end_pos]).
  - language: "en" or "vi" (best guess).
  - reason: short explanation why this is considered a spelling error.
- If there are no obvious spelling errors, set total_found = 0 and items = [].
- total_found MUST equal the length of items.

------------------------------------------
### JSON OUTPUT FORMAT (STRICT)

Return JSON with exactly this structure (field names must match):

{{
    "analysis_metadata": {{
        "analyzed_at": "ISO timestamp",
        "writing_type": "{writing_type}",
        "total_paragraphs": <int>,
        "total_sentences": <int>
    }},
    
    "contradictions": {{
        "total_found": <int>,
        "items": [
            {{
                "id": 1,
                "sentence1": "Full text of first statement",
                "sentence2": "Full text of contradicting statement",
                "sentence1_location": "Paragraph X, Sentence Y",
                "sentence2_location": "Paragraph A, Sentence B",
                "contradiction_type": "factual|numerical|temporal|logical",
                "severity": "high|medium|low",
                "explanation": "Why these two statements contradict each other",
                "suggestion": "How to resolve or clarify the conflict"
            }}
        ]
    }},
    
    "undefined_terms": {{
        "total_found": <int>,
        "items": [
            {{
                "term": "gradient clipping",
                "first_appeared": "Paragraph 3, Sentence 1",
                "context_snippet": "Short excerpt showing where the term appears...",
                "is_defined": false,
                "reason": "Term appears without definition or clear explanation",
                "suggestion": "Provide a short definition or explanation the first time it appears"
            }}
        ]
    }},
    
    "unsupported_claims": {{
        "total_found": <int>,
        "items": [
            {{
                "claim": "AI can perfectly predict human emotions.",
                "location": "Paragraph 2, Sentence 3",
                "status": "unsupported",
                "claim_type": "absolute|comparative|causal|predictive",
                "reason": "No supporting data, examples, or citations within ±2 sentences",
                "surrounding_context": "Short excerpt around the claim...",
                "suggestion": "Add concrete evidence, cite research, or weaken the claim."
            }}
        ]
    }},
    
    "logical_jumps": {{
        "total_found": <int>,
        "items": [
            {{
                "from_paragraph": 5,
                "to_paragraph": 6,
                "from_paragraph_summary": "Short summary of paragraph 5 topic",
                "to_paragraph_summary": "Short summary of paragraph 6 topic",
                "coherence_score": 0.32,
                "flag": "logical_jump",
                "severity": "high|medium|low",
                "explanation": "Why this transition feels abrupt or poorly connected",
                "suggestion": "Add a linking sentence, reorder paragraphs, or clarify why the topic changes."
            }}
        ]
    }},
    
    "spelling_errors": {{
        "total_found": <int>,
        "items": [
            {{
                "original": "deeplearnnig",
                "suggested": "deep learning",
                "start_pos": 120,
                "end_pos": 132,
                "language": "en",
                "reason": "Common English AI term misspelled (letters swapped)"
            }}
        ]
    }},
    
    "summary": {{
        "total_issues": <int>,
        "critical_issues": <int>,
        "document_quality_score": <int>,
        "key_recommendations": [
            "Most important recommendation 1",
            "Most important recommendation 2",
            "Most important recommendation 3"
        ]
    }}
}}

- total_issues should approximately equal:
  contradictions.total_found
  + undefined_terms.total_found
  + unsupported_claims.total_found
  + logical_jumps.total_found
  + spelling_errors.total_found

------------------------------------------
Return ONLY valid JSON. Do NOT include markdown, comments, or any text outside the JSON.
"""
    return prompt


# =======================================
# 4. UNIFIED ANALYSIS – VIETNAMESE
# =======================================

def prompt_analysis_vi(context: Dict[str, Any], content: str) -> str:
    """
    Unified Vietnamese prompt – 5 nhiệm vụ:
    1) Mâu thuẫn logic
    2) Thuật ngữ chưa định nghĩa
    3) Luận điểm thiếu chứng cứ
    4) Nhảy logic
    5) Lỗi chính tả (VI + EN trong văn bản)
    """

    writing_type = context.get("writing_type", "Văn bản")
    main_goal = context.get("main_goal", "")
    criteria = context.get("criteria", [])
    constraints = context.get("constraints", [])

    context_lines = []
    context_lines.append(f"Loại văn bản: {writing_type}")
    if main_goal:
        context_lines.append(f"Mục tiêu chính: {main_goal}")
    if criteria:
        context_lines.append("Tiêu chí đánh giá:")
        for c in criteria:
            context_lines.append(f"  - {c}")
    if constraints:
        context_lines.append("Ràng buộc:")
        for r in constraints:
            context_lines.append(f"  - {r}")
    context_block = "\n".join(context_lines)

    prompt = f"""
Bạn là LogicGuard – AI phân tích logic và cấu trúc cho các tài liệu {writing_type}.

Nhiệm vụ: phân tích văn bản theo 5 chiều:
1) Mâu thuẫn logic (Contradictions)
2) Thuật ngữ chưa định nghĩa (Undefined Terms)
3) Luận điểm thiếu chứng cứ (Unsupported Claims)
4) Nhảy logic (Logical Jumps)
5) Lỗi chính tả (tiếng Việt + tiếng Anh xuất hiện trong văn bản)

Bạn nhận được:
- CONTEXT: thông tin tổng quan về nhiệm vụ viết.
- CONTENT: toàn bộ văn bản gốc dạng chuỗi.

QUY TẮC CHUNG QUAN TRỌNG:
- CHỈ trả về MỘT object JSON duy nhất.
- JSON PHẢI hợp lệ (không dấu phẩy thừa, không comment).
- KHÔNG dùng markdown, KHÔNG dùng ``` trong output.
- KHÔNG ghi thêm bất kỳ giải thích nào ngoài JSON.
- Mọi vị trí (start_pos, end_pos) dùng cho spelling_errors
  đều là chỉ số ký tự 0-based trên CHUỖI CONTENT GỐC
  (chính xác như trong block VĂN BẢN bên dưới).
- end_pos là chỉ số kết thúc dạng exclusive (giống content[start:end] trong Python).
- KHÔNG coi tên thương hiệu / tên sản phẩm / tên mô hình có vẻ cố ý
  (ví dụ: "iPhone", "YouTube", "Z-Trax", "NeuroLearn-X") là lỗi chính tả.

------------------------------------------
### NGỮ CẢNH
{context_block}

------------------------------------------
### VĂN BẢN (CONTENT GỐC CẦN PHÂN TÍCH)
<<<BẮT ĐẦU VĂN BẢN>>>
{content}
<<<KẾT THÚC VĂN BẢN>>>

Bạn PHẢI dùng chính xác chuỗi CONTENT trên để:
- Phát hiện mâu thuẫn, thuật ngữ chưa định nghĩa, luận điểm thiếu chứng cứ, nhảy logic.
- Phát hiện lỗi chính tả (tiếng Việt + tiếng Anh).
- Tính mọi start_pos / end_pos cho spelling_errors.

------------------------------------------
### 1) MÂU THUẪN LOGIC (contradictions)

- Tìm các cặp câu / phát biểu không thể cùng đúng.
- Tập trung vào xung đột về số liệu, ngày tháng, sự kiện, hoặc khẳng định đối lập trực tiếp.
- Mỗi item:
  - sentence1, sentence2: toàn bộ hai câu mâu thuẫn.
  - sentence1_location, sentence2_location: mô tả ngắn, ví dụ "Đoạn 1, Câu 2".
  - contradiction_type: "factual" | "numerical" | "temporal" | "logical".
  - severity: "high" | "medium" | "low".
  - explanation: 1–3 câu giải thích vì sao hai câu mâu thuẫn.
  - suggestion: gợi ý cụ thể để sửa hoặc làm rõ.
- total_found PHẢI bằng số lượng items.

------------------------------------------
### 2) THUẬT NGỮ CHƯA ĐỊNH NGHĨA (undefined_terms)

- Tìm các thuật ngữ kỹ thuật, tên mô hình, tên sản phẩm, từ viết tắt,
  khái niệm chuyên ngành quan trọng nhưng KHÔNG được giải thích rõ ở lần xuất hiện đầu.
- Một thuật ngữ được xem là "đã định nghĩa" nếu:
  - Có câu giải thích kiểu "X là...", "X được hiểu là...", HOẶC
  - Có giải thích ngắn trong ngoặc đơn, HOẶC
  - Ý nghĩa hiển nhiên với đối tượng độc giả mục tiêu.
- KHÔNG coi các lỗi chính tả hiển nhiên (deeplearnnig, algoritm, platfomr, tạoo, ...)
  là "thuật ngữ". Nếu có vẻ chỉ là typo cho một từ phổ biến, hãy bỏ qua trong undefined_terms.
- Mỗi item:
  - term: đúng chuỗi trong CONTENT (giữ nguyên chữ hoa, dấu, ...).
  - first_appeared: ví dụ "Đoạn 2, Câu 1".
  - context_snippet: trích đoạn ngắn (< 150 ký tự) xung quanh lần xuất hiện đầu.
  - is_defined: thường false cho thuật ngữ chưa định nghĩa; có thể true nếu có giải thích nhưng vẫn chưa rõ.
  - reason: vì sao xem là chưa định nghĩa / chưa rõ.
  - suggestion: gợi ý cách bổ sung định nghĩa.
- total_found PHẢI bằng số lượng items.

------------------------------------------
### 3) LUẬN ĐIỂM THIẾU CHỨNG CỨ (unsupported_claims)

Luận điểm là:
- Khẳng định về sự thật, xu hướng, quan hệ, dự đoán, so sánh, hay nhân quả.

Chứng cứ có thể là:
- Dữ liệu, thống kê, ví dụ, trích dẫn, hoặc lập luận logic rõ ràng.

Một luận điểm chỉ được xem là "có chứng cứ" nếu:
- Có chứng cứ trong cùng câu, HOẶC
- Trong khoảng ±2 câu lân cận, HOẶC
- Rõ ràng trong cùng đoạn và có liên kết trực tiếp.

Mỗi item:
- claim: câu hoặc mệnh đề chứa luận điểm.
- location: ví dụ "Đoạn 3, Câu 2".
- status: "unsupported" | "weak" | "partially_supported".
- claim_type: "absolute" | "comparative" | "causal" | "predictive" | ...
- reason: giải thích vì sao chứng cứ thiếu hoặc yếu.
- surrounding_context: trích đoạn ngắn xung quanh luận điểm.
- suggestion: gợi ý loại chứng cứ cần bổ sung hoặc cách giảm mức độ tuyệt đối của câu.

total_found PHẢI bằng số lượng items.

------------------------------------------
### 4) NHẢY LOGIC (logical_jumps)

- Xem xét sự chuyển ý giữa các đoạn văn.
- Nhảy logic xảy ra khi chủ đề hoặc lập luận đổi hướng đột ngột,
  thiếu câu nối, giải thích, hoặc mối liên hệ rõ ràng.
- Mỗi item:
  - from_paragraph: số thứ tự đoạn nguồn (bắt đầu từ 1).
  - to_paragraph: số thứ tự đoạn đích (bắt đầu từ 1).
  - from_paragraph_summary: tóm tắt 1–2 câu nội dung đoạn nguồn.
  - to_paragraph_summary: tóm tắt 1–2 câu nội dung đoạn đích.
  - coherence_score: số thực 0–1 (1 = rất mạch lạc, 0 = hầu như không liên quan).
  - flag: nhãn ngắn, ví dụ "abrupt_topic_shift", "missing_explanation".
  - severity: "high" | "medium" | "low".
  - explanation: tại sao xem đây là nhảy logic.
  - suggestion: gợi ý thêm câu chuyển ý, sắp xếp lại đoạn, hoặc giải thích liên kết.
- Chỉ đưa vào các item có coherence_score < 0.7.
- total_found PHẢI bằng số lượng items.

------------------------------------------
### 5) LỖI CHÍNH TẢ (spelling_errors – tiếng Việt + tiếng Anh)

- Phát hiện lỗi chính tả rõ ràng trong cả tiếng Việt và tiếng Anh xuất hiện trong CONTENT.
- Bao gồm: thiếu chữ, thừa chữ, đảo chữ, gõ nhầm, nhầm dấu trong từ phổ biến.
- CẦN THẬN TRỌNG:
  - KHÔNG "sửa" tên thương hiệu, tên riêng, tên mô hình nếu chúng có vẻ cố ý
    (ví dụ: "iPhone", "YouTube", "NavierGreen", "Z-Trax").
  - KHÔNG "sửa" các thuật ngữ AI nếu không chắc chắn đó là lỗi (ví dụ: tên model, tên framework).
  - Nếu không chắc đó có phải lỗi chính tả hay không → BỎ QUA, KHÔNG đánh dấu.
- Ví dụ các từ NÊN gắn cờ:
  - "deeplearnnig" → "deep learning"
  - "databaes" → "database"
  - "algoritm" → "algorithm"
  - "platfomr" → "platform"
  - "tạoo" → "tạo" (trong ngữ cảnh "trí tuệ nhân tạoo")
- Mỗi item:
  - original: chuỗi gốc trong CONTENT bị sai chính tả.
  - suggested: phiên bản chính tả đúng.
  - start_pos: index ký tự bắt đầu (0-based) trong CONTENT.
  - end_pos: index ký tự kết thúc dạng exclusive (0-based).
  - language: "vi" hoặc "en" (ước lượng tốt nhất).
  - reason: giải thích ngắn vì sao đây là lỗi chính tả.
- Nếu không có lỗi rõ ràng, đặt total_found = 0 và items = [].
- total_found PHẢI bằng số lượng items.

------------------------------------------
### ĐỊNH DẠNG JSON ĐẦU RA (CHUẨN)

Bạn PHẢI trả về JSON với cấu trúc (tên trường y hệt):

{{
    "analysis_metadata": {{
        "analyzed_at": "Timestamp ISO",
        "writing_type": "{writing_type}",
        "total_paragraphs": <số nguyên>,
        "total_sentences": <số nguyên>
    }},
    
    "contradictions": {{
        "total_found": <số nguyên>,
        "items": [
            {{
                "id": 1,
                "sentence1": "Toàn bộ câu thứ nhất",
                "sentence2": "Toàn bộ câu mâu thuẫn",
                "sentence1_location": "Đoạn X, Câu Y",
                "sentence2_location": "Đoạn A, Câu B",
                "contradiction_type": "factual|numerical|temporal|logical",
                "severity": "high|medium|low",
                "explanation": "Giải thích tại sao hai câu mâu thuẫn",
                "suggestion": "Gợi ý cách chỉnh sửa hoặc làm rõ"
            }}
        ]
    }},
    
    "undefined_terms": {{
        "total_found": <số nguyên>,
        "items": [
            {{
                "term": "Tên thuật ngữ",
                "first_appeared": "Đoạn X, Câu Y",
                "context_snippet": "Trích đoạn ngắn có chứa thuật ngữ...",
                "is_defined": false,
                "reason": "Vì sao xem là chưa được định nghĩa rõ",
                "suggestion": "Gợi ý cách thêm định nghĩa hoặc giải thích"
            }}
        ]
    }},
    
    "unsupported_claims": {{
        "total_found": <số nguyên>,
        "items": [
            {{
                "claim": "Nội dung luận điểm",
                "location": "Đoạn X, Câu Y",
                "status": "unsupported",
                "claim_type": "absolute|comparative|causal|predictive",
                "reason": "Luận điểm thiếu dữ liệu / ví dụ / trích dẫn trong phạm vi cho phép",
                "surrounding_context": "Trích bối cảnh xung quanh luận điểm...",
                "suggestion": "Đề xuất bổ sung chứng cứ hoặc điều chỉnh câu chữ"
            }}
        ]
    }},
    
    "logical_jumps": {{
        "total_found": <số nguyên>,
        "items": [
            {{
                "from_paragraph": <số nguyên>,
                "to_paragraph": <số nguyên>,
                "from_paragraph_summary": "Tóm tắt ngắn đoạn xuất phát",
                "to_paragraph_summary": "Tóm tắt ngắn đoạn đích",
                "coherence_score": <số thực>,
                "flag": "logical_jump",
                "severity": "high|medium|low",
                "explanation": "Giải thích vì sao bị xem là nhảy logic",
                "suggestion": "Gợi ý cách thêm câu chuyển ý, sắp xếp lại, hoặc liên kết chủ đề"
            }}
        ]
    }},
    
    "spelling_errors": {{
        "total_found": <số nguyên>,
        "items": [
            {{
                "original": "deeplearnnig",
                "suggested": "deep learning",
                "start_pos": 120,
                "end_pos": 132,
                "language": "en",
                "reason": "Thuật ngữ tiếng Anh phổ biến nhưng bị gõ sai thứ tự chữ cái"
            }}
        ]
    }},
    
    "summary": {{
        "total_issues": <tổng số vấn đề phát hiện>,
        "critical_issues": <số vấn đề mức high>,
        "document_quality_score": <0-100>,
        "key_recommendations": [
            "Khuyến nghị quan trọng 1",
            "Khuyến nghị quan trọng 2",
            "Khuyến nghị quan trọng 3"
        ]
    }}
}}

- total_issues nên xấp xỉ:
  contradictions.total_found
  + undefined_terms.total_found
  + unsupported_claims.total_found
  + logical_jumps.total_found
  + spelling_errors.total_found

------------------------------------------
Chỉ trả về JSON hợp lệ. KHÔNG trả lời thêm, KHÔNG dùng markdown, KHÔNG giải thích ngoài JSON.
"""
    return prompt
