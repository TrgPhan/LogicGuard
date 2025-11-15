

def prompt_undefined_terms(context, content):
    """
    Tạo prompt để phát hiện các thuật ngữ chưa được định nghĩa trong văn bản
    
    Args:
        context: Dictionary chứa thông tin ngữ cảnh
            - writing_type: Loại văn bản (Technical Proposal, Academic Essay, etc.)
            - main_goal: Mục tiêu chính của bài viết
            - criteria: Danh sách các tiêu chí đánh giá
            - constraints: Các ràng buộc (word_limit, etc.)
        content: Nội dung văn bản cần phân tích
        
    Returns:
        str: Prompt đầy đủ để gửi đến LLM
    """
    
    # Trích xuất thông tin từ context
    writing_type = context.get("writing_type", "Document")
    main_goal = context.get("main_goal", "")
    criteria = context.get("criteria", [])
    constraints = context.get("constraints", [])
    
    # Format context information
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

### Context Information
{context_block}

### Document Content
<<<BEGIN DOCUMENT>>>
{content}
<<<END DOCUMENT>>>

### Definition Patterns to Look For
When checking if a term is defined, look for these patterns at or near the first occurrence:
- "X là..." (X is...)
- "X được hiểu là..." (X is understood as...)
- "X gọi là..." (called X...)
- "X (viết tắt của...)" (X, abbreviation for...)
- "X, hay còn gọi là..." (X, also known as...)
- Parenthetical explanations immediately after the term
- Contextual clues that make the meaning clear to a general audience

### Instructions
1. Read through the entire document and identify ALL specialized terms, technical concepts, and acronyms
2. For each term found:
   - Locate its FIRST occurrence in the document
   - Check if there is a definition or explanation at or near that occurrence
   - Note the paragraph or section where it first appears
3. Flag terms that are NOT adequately defined for a general reader
4. Consider the document type: {writing_type} - some terms may be assumed knowledge for the expected audience

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
- Include BOTH undefined_terms and defined_terms for transparency
- Be thorough but avoid false positives (common terms don't need definition)
- Consider the intended audience's expected knowledge level
- Focus on domain-specific terminology that requires clarification
- Paragraph numbers should match the logical structure of the document

Return ONLY the JSON output. Do not include any markdown code blocks, commentary, or explanations outside the JSON structure.
"""
    
    return prompt


def prompt_unsupported_claims(context, content):
    """
    Tạo prompt để phát hiện các luận điểm thiếu chứng cứ trong văn bản
    
    Args:
        context: Dictionary chứa thông tin ngữ cảnh
            - writing_type: Loại văn bản (Technical Proposal, Academic Essay, etc.)
            - main_goal: Mục tiêu chính của bài viết
            - criteria: Danh sách các tiêu chí đánh giá
            - constraints: Các ràng buộc (word_limit, etc.)
        content: Nội dung văn bản cần phân tích
        
    Returns:
        str: Prompt đầy đủ để gửi đến LLM
    """
    
    # Trích xuất thông tin từ context
    writing_type = context.get("writing_type", "Document")
    main_goal = context.get("main_goal", "")
    criteria = context.get("criteria", [])
    constraints = context.get("constraints", [])
    
    # Format context information
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
- Makes an assertion about facts, trends, or relationships
- Presents an opinion as if it were fact
- Makes predictions or generalizations
- States cause-and-effect relationships
- Compares or evaluates things

### What Constitutes Evidence
Evidence includes:
- **Data/Statistics**: Numbers, percentages, measurements, research findings
- **Examples**: Specific instances, case studies, real-world scenarios
- **Citations**: References to studies, experts, publications, or authoritative sources
- **Logical reasoning**: Step-by-step explanations that build on established facts
- **Quotations**: Direct statements from credible sources
- **Visual data**: Graphs, charts, tables (when mentioned)

### Evidence Proximity Rule
A claim is considered "supported" if evidence appears:
- In the same sentence
- Within ±2 sentences (before or after the claim)
- In the same paragraph with clear connection to the claim

### Instructions
1. Read through the document sentence by sentence
2. Identify all claims (assertive statements that require support)
3. For each claim:
   - Check if there is supporting evidence within ±2 sentences
   - Evaluate if the evidence is sufficient and relevant
   - Classify as "supported" or "unsupported"
4. For unsupported claims, provide specific suggestions for improvement

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
            "suggestion": "Add source, data, or example to support this claim. Consider: cite research studies, provide statistical evidence, or qualify the statement (e.g., 'AI can predict some human emotions with 70% accuracy according to...')"
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
- **Be strict but fair**: Claims need evidence, but obvious facts don't
- **Consider the writing type**: {writing_type} may have different evidence standards
- **Watch for weasel words**: "probably", "might", "could" don't make unsupported claims acceptable
- **Absolute statements**: "always", "never", "all", "none" require strong evidence
- **Comparative claims**: "better", "faster", "more efficient" need comparative data
- **Causal claims**: "causes", "leads to", "results in" need logical or empirical support
- **Opinion vs Fact**: Distinguish between stated opinions and assertions presented as fact
- **Common knowledge**: Well-established facts don't always need citations (e.g., "water boils at 100°C")

### Special Cases
- **Technical proposals**: Should have data, benchmarks, or technical specifications
- **Academic essays**: Should have citations, references, or scholarly support
- **Business documents**: Should have market data, case studies, or ROI figures
- **Opinion pieces**: Even opinions benefit from supporting examples or reasoning

Return ONLY the JSON output. Do not include any markdown code blocks, commentary, or explanations outside the JSON structure.
"""
    
    return prompt