def format_context(context):
    writing_type = context.get("writing_type", "Document")
    main_goal = context.get("main_goal", "")
    return f"Writing Type: {writing_type}\nMain Goal: {main_goal}".strip()


def prompt_undefined_terms(context, content):
    ctx = format_context(context)

    return f"""
You are a writing clarity editor. Identify technical terms, acronyms, or domain-specific vocabulary that appear without definition at first occurrence. Rewrite the sentence so the meaning of that term becomes clear.

RULES (MANDATORY):
- suggested_text MUST be a complete replacement sentence
- MUST naturally include a brief definition
- Keep original tone, intent, length, POV, tense
- NO explanation, NO reasoning, NO instructions, NO bullet points
- Output ONLY JSON — no markdown, no commentary

OUTPUT FORMAT:
{{
  "undefined_terms": [
    {{
      "term": "<term>",
      "original_text": "<original sentence>",
      "suggested_text": "<rewritten sentence including definition>",
      "replacement_type": "inline_definition"
    }}
  ]
}}

FEW-SHOT EXAMPLES:

Original:
"The model uses gradient clipping to prevent exploding gradients."
Replacement:
"The model uses gradient clipping, a technique that limits gradient magnitude during training, to prevent exploding gradients."

Original:
"Our pipeline applies PCA for preprocessing."
Replacement:
"Our pipeline applies principal component analysis (PCA), a method used to reduce feature dimensionality, for preprocessing."

CONTEXT:
{ctx}

DOCUMENT:
<<<BEGIN>>>
{content}
<<<END>>>
"""


def prompt_unsupported_claims(context, content):
    ctx = format_context(context)

    return f"""
You are an evidence-focused writing editor. Find claims presented as fact but lacking support. Replace each with a strengthened version that adds an example, data, citation, or qualification.

RULES (MANDATORY):
- suggested_text MUST be a full replacement sentence
- MUST add evidence OR soften the claim
- Keep tone, meaning, style, POV, tense consistent
- NO meta-suggestion, NO instructions, NO analysis
- Output ONLY JSON

OUTPUT FORMAT:
{{
  "unsupported_claims": [
    {{
      "original_text": "<sentence>",
      "suggested_text": "<improved supported sentence>",
      "replacement_type": "add_example|add_data|add_citation|qualify"
    }}
  ]
}}

FEW-SHOT EXAMPLES:

Original:
"Pineapple elevates every dish."
Replacement:
"Pineapple can enhance certain dishes, such as Thai curries or grilled meats, by adding acidity and sweetness."

Original:
"NoSQL databases are always faster than SQL."
Replacement:
"NoSQL databases can be faster for document-heavy workloads, as shown in 2023 MongoDB benchmark results."

Original:
"The new app will double revenue."
Replacement:
"Early pilot testing showed the new app increased revenue by 18% during its first quarter."

CONTEXT:
{ctx}

DOCUMENT:
<<<BEGIN>>>
{content}
<<<END>>>
"""


def prompt_contradictions(context, content):
    ctx = format_context(context)

    return f"""
You are a logical consistency editor. Detect statements that conflict with each other. Rewrite the conflicting sentence so the information becomes logically consistent.

RULES:
- suggested_text MUST directly resolve the contradiction
- Preserve original intent and writing style
- Output ONLY JSON — no explanation

OUTPUT FORMAT:
{{
  "contradictions": [
    {{
      "original_text": "<contradicting sentence>",
      "suggested_text": "<corrected replacement>",
      "replacement_type": "resolve_contradiction"
    }}
  ]
}}

FEW-SHOT EXAMPLE:

Sentence A:
"The project launched in 2024."
Sentence B:
"The project has been operating since 2022."
Replacement:
"The project began pilot testing in 2022 and officially launched in 2024."

CONTEXT:
{ctx}

DOCUMENT:
<<<BEGIN>>>
{content}
<<<END>>>
"""


def prompt_logical_jumps(context, content):
    ctx = format_context(context)

    return f"""
You are a writing cohesion editor. Identify places where ideas shift abruptly without explanation. Suggest ONE bridging sentence.

RULES:
- suggested_text must be a standalone sentence
- It should logically connect surrounding ideas
- Keep style, tone, topic consistent
- Output ONLY JSON

OUTPUT FORMAT:
{{
  "logical_jumps": [
    {{
      "location": "between paragraph X and Y",
      "suggested_text": "<bridge sentence>",
      "replacement_type": "add_transition"
    }}
  ]
}}

FEW-SHOT EXAMPLE:

Bridge:
"To address this growing demand, our team developed a scalable automation platform."

CONTEXT:
{ctx}

DOCUMENT:
<<<BEGIN>>>
{content}
<<<END>>>
"""


def prompt_analysis(context, content):
    ctx = format_context(context)

    return f"""
You are an expert writing improvement system. Analyze the document and return ONLY issues that require text replacement, each with a usable suggested_text.

TARGET ISSUE TYPES:
- contradictions
- undefined_terms
- unsupported_claims
- logical_jumps

RULES:
- Each item MUST include original_text + suggested_text + replacement_type
- suggested_text MUST be a usable replacement sentence or bridge
- NO explanations, NO analysis, NO justification
- Output ONLY JSON

OUTPUT FORMAT:
{{
  "contradictions": [...],
  "undefined_terms": [...],
  "unsupported_claims": [...],
  "logical_jumps": [...]
}}

CONTEXT:
{ctx}

DOCUMENT:
<<<BEGIN>>>
{content}
<<<END>>>
"""


def prompt_analysis_vi(context, content):
    ctx = format_context(context)

    return f"""
Bạn là một hệ thống cải thiện văn bản chuyên nghiệp. Phân tích tài liệu và chỉ trả về các vấn đề cần thay thế văn bản, mỗi vấn đề phải có suggested_text có thể sử dụng được.

CÁC LOẠI VẤN ĐỀ CẦN TÌM:
- contradictions (mâu thuẫn logic)
- undefined_terms (thuật ngữ chưa định nghĩa)
- unsupported_claims (luận điểm thiếu chứng cứ)
- logical_jumps (nhảy logic)

QUY TẮC:
- Mỗi mục PHẢI bao gồm original_text + suggested_text + replacement_type
- suggested_text PHẢI là câu thay thế hoặc cầu nối có thể sử dụng được
- KHÔNG giải thích, KHÔNG phân tích, KHÔNG biện minh
- Chỉ trả về JSON

ĐỊNH DẠNG ĐẦU RA:
{{
  "contradictions": [...],
  "undefined_terms": [...],
  "unsupported_claims": [...],
  "logical_jumps": [...]
}}

NGỮ CẢNH:
{ctx}

TÀI LIỆU:
<<<BẮT ĐẦU>>>
{content}
<<<KẾT THÚC>>>
"""
