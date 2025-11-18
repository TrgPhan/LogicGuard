

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


def prompt_analysis(context, content):
    """
    Tạo prompt tổng hợp để phân tích toàn diện văn bản với 4 subtasks:
    1. Contradictions (Mâu thuẫn logic)
    2. Undefined Terms (Thuật ngữ chưa định nghĩa)
    3. Unsupported Claims (Luận điểm thiếu chứng cứ)
    4. Logical Jumps (Nhảy logic)
    
    Args:
        context: Dictionary chứa thông tin ngữ cảnh
            - writing_type: Loại văn bản
            - main_goal: Mục tiêu chính
            - criteria: Danh sách các tiêu chí đánh giá
            - constraints: Các ràng buộc
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
    
    prompt = f"""You are LogicGuard, an expert AI writing analyst specialized in comprehensive document analysis for {writing_type} documents.

### Mission Overview
Perform a complete logical and structural analysis of the document across FOUR critical dimensions:
1. **Contradictions** - Detect logical inconsistencies between statements
2. **Undefined Terms** - Identify terminology without proper definitions
3. **Unsupported Claims** - Find assertions lacking evidence
4. **Logical Jumps** - Detect abrupt topic transitions with low coherence

### Context Information
{context_block}

### Document Content
<<<BEGIN DOCUMENT>>>
{content}
<<<END DOCUMENT>>>

---

## SUBTASK 1: CONTRADICTIONS

### What to Look For
- Statements that directly oppose each other
- Conflicting data, numbers, dates, or facts
- Incompatible claims about the same subject
- Statements that cannot both be true simultaneously

### Detection Rules
- Compare all sentence pairs for logical contradiction
- Flag numerical/temporal conflicts (different numbers, dates for same thing)
- Consider context: some apparent contradictions may be intentional contrasts
- Severity: "high" (direct contradiction), "medium" (likely conflict), "low" (potential conflict)

---

## SUBTASK 2: UNDEFINED TERMS
### What to Look For
Technical terms, specialized concepts, acronyms, or domain-specific vocabulary that appear WITHOUT proper definition or explanation at their FIRST occurrence.

### Definition Patterns to Recognize
- "X là..." (X is...)
- "X được hiểu là..." (X is understood as...)
- "X gọi là..." (called X...)
- "X (viết tắt của...)" (X, abbreviation for...)
- "X, hay còn gọi là..." (X, also known as...)
- Parenthetical explanations immediately after the term
- Contextual clues that make meaning clear

### Rules
- Track FIRST occurrence of each term
- Check for definition patterns within same sentence or ±1 sentence
- Consider audience: {writing_type} may assume certain knowledge
- Common knowledge terms don't need definitions

---

## SUBTASK 3: UNSUPPORTED CLAIMS

### What Constitutes a Claim
- Assertions about facts, trends, or relationships
- Opinions presented as facts
- Predictions or generalizations
- Cause-and-effect statements
- Comparative or evaluative statements

### What Constitutes Evidence
- **Data/Statistics**: Numbers, percentages, measurements
- **Examples**: Case studies, real-world scenarios, specific instances
- **Citations**: References to studies, experts, publications
- **Logical reasoning**: Step-by-step explanations based on facts
- **Quotations**: Statements from credible sources

### Evidence Proximity Rule (Critical!)
A claim is "supported" ONLY if evidence appears:
- In the SAME sentence, OR
- Within ±2 sentences (before or after), OR
- In the same paragraph with CLEAR connection

### Special Attention
- Absolute claims ("always", "never", "all") need STRONG evidence
- Comparative claims ("better", "faster") need comparative data
- Quantified claims ("80% reduction") need supporting calculations
- Causal claims ("causes", "leads to") need logical/empirical support

---

## SUBTASK 4: LOGICAL JUMPS

### What to Look For
Abrupt topic transitions where semantic coherence between consecutive paragraphs is LOW, indicating poor logical flow.

### Detection Rules
- Analyze topic similarity between consecutive paragraphs
- Flag transitions where topics change drastically without proper bridging
- Low coherence = similarity < 0.4 (approximate conceptual threshold)
- Consider: Does the transition feel jarring? Is there a missing link?

### What Makes a Good Transition
- Topic continuity (similar concepts, related ideas)
- Explicit transition phrases ("Furthermore", "However", "As a result")
- Logical progression (cause→effect, problem→solution, general→specific)
- Shared keywords or concepts

### What Makes a Logical Jump (Bad)
- Sudden topic change without preparation
- No connecting phrases or ideas
- Reader confusion about relevance
- Missing intermediate reasoning steps

---

## OUTPUT FORMAT

Return ONLY valid JSON with this EXACT structure:

{{
    "analysis_metadata": {{
        "analyzed_at": "ISO timestamp",
        "writing_type": "{writing_type}",
        "total_paragraphs": <number>,
        "total_sentences": <number>
    }},
    
    "contradictions": {{
        "total_found": <number>,
        "items": [
            {{
                "id": 1,
                "sentence1": "Full text of first statement",
                "sentence2": "Full text of contradicting statement",
                "sentence1_location": "Paragraph X, Sentence Y",
                "sentence2_location": "Paragraph A, Sentence B",
                "contradiction_type": "factual|numerical|temporal|logical",
                "severity": "high|medium|low",
                "explanation": "Clear explanation of why these contradict",
                "suggestion": "How to resolve this contradiction"
            }}
        ]
    }},
    
    "undefined_terms": {{
        "total_found": <number>,
        "items": [
            {{
                "term": "gradient clipping",
                "first_appeared": "Paragraph 3, Sentence 1",
                "context_snippet": "Brief excerpt showing where term appears...",
                "is_defined": false,
                "reason": "Term appears without explanation or definition pattern",
                "suggestion": "Add definition: 'Gradient clipping, a technique that limits...' or explain in context"
            }}
        ]
    }},
    
    "unsupported_claims": {{
        "total_found": <number>,
        "items": [
            {{
                "claim": "AI can perfectly predict human emotions",
                "location": "Paragraph 2, Sentence 3",
                "status": "unsupported",
                "claim_type": "absolute|comparative|causal|predictive",
                "reason": "Absolute claim with no supporting data, research, or examples within ±2 sentences",
                "surrounding_context": "Brief excerpt showing claim in context...",
                "suggestion": "Add citation to research, provide accuracy metrics, or qualify the statement"
            }}
        ]
    }},
    
    "logical_jumps": {{
        "total_found": <number>,
        "items": [
            {{
                "from_paragraph": 5,
                "to_paragraph": 6,
                "from_paragraph_summary": "Brief summary of paragraph 5 topic",
                "to_paragraph_summary": "Brief summary of paragraph 6 topic",
                "coherence_score": 0.32,
                "flag": "logical_jump",
                "severity": "high|medium|low",
                "explanation": "Why this transition is jarring or disconnected",
                "suggestion": "Add transitional paragraph, use connecting phrase, or reorder content"
            }}
        ]
    }},
    
    "summary": {{
        "total_issues": <sum of all issues>,
        "critical_issues": <count of high severity>,
        "document_quality_score": <0-100>,
        "key_recommendations": [
            "Most important recommendation 1",
            "Most important recommendation 2",
            "Most important recommendation 3"
        ]
    }}
}}

---

## IMPORTANT GUIDELINES

### For ALL Subtasks:
1. **Be thorough but practical** - Find real issues, not nitpicks
2. **Consider the writing type** - {writing_type} has specific standards
3. **Provide actionable suggestions** - Tell writer HOW to fix, not just WHAT is wrong
4. **Prioritize by severity** - Flag critical issues as "high", minor ones as "low"
5. **Be consistent** - Use the exact JSON structure specified

### Quality Standards by Writing Type:
- **Technical Proposal**: High evidence standards, technical precision, clear definitions
- **Academic Essay**: Strong citation requirements, formal terminology, logical flow
- **Business Document**: Data-driven claims, ROI focus, executive clarity
- **Opinion Piece**: Logical reasoning, examples to support views, clear stance

### Analysis Philosophy:
- **Contradictions**: Zero tolerance - they undermine credibility
- **Undefined Terms**: Define domain-specific terms; common knowledge okay
- **Unsupported Claims**: Evidence within ±2 sentences is MANDATORY
- **Logical Jumps**: Smooth flow enhances readability and persuasion

Return ONLY the JSON output. Do NOT include markdown code blocks, commentary, or explanations outside the JSON structure.
"""
    
    return prompt


def prompt_analysis_vi(context, content):
    """
    Tạo prompt TIẾNG VIỆT tổng hợp để phân tích toàn diện văn bản với 4 subtasks:
    1. Contradictions (Mâu thuẫn logic)
    2. Undefined Terms (Thuật ngữ chưa định nghĩa)
    3. Unsupported Claims (Luận điểm thiếu chứng cứ)
    4. Logical Jumps (Nhảy logic)
    
    Args:
        context: Dictionary chứa thông tin ngữ cảnh
            - writing_type: Loại văn bản
            - main_goal: Mục tiêu chính
            - criteria: Danh sách các tiêu chí đánh giá
            - constraints: Các ràng buộc
        content: Nội dung văn bản cần phân tích
        
    Returns:
        str: Prompt đầy đủ bằng tiếng Việt để gửi đến LLM
    """
    
    # Trích xuất thông tin từ context
    writing_type = context.get("writing_type", "Văn bản")
    main_goal = context.get("main_goal", "")
    criteria = context.get("criteria", [])
    constraints = context.get("constraints", [])
    
    # Format context information
    context_lines = []
    context_lines.append(f"Loại văn bản: {writing_type}")
    if main_goal:
        context_lines.append(f"Mục tiêu chính: {main_goal}")
    if criteria:
        formatted_criteria = "\n".join(f"  - {item}" for item in criteria)
        context_lines.append(f"Tiêu chí đánh giá:\n{formatted_criteria}")
    if constraints:
        formatted_constraints = "\n".join(f"  - {item}" for item in constraints)
        context_lines.append(f"Ràng buộc:\n{formatted_constraints}")
    
    context_block = "\n".join(context_lines)
    
    prompt = f"""Bạn là LogicGuard, một chuyên gia AI phân tích văn bản chuyên sâu, đặc biệt hóa trong việc phân tích toàn diện các tài liệu {writing_type}.

### Nhiệm Vụ Tổng Quan
Thực hiện phân tích logic và cấu trúc hoàn chỉnh của văn bản qua BỐN chiều quan trọng:
1. **Mâu thuẫn logic (Contradictions)** - Phát hiện các mâu thuẫn logic giữa các phát biểu
2. **Thuật ngữ chưa định nghĩa (Undefined Terms)** - Xác định thuật ngữ không có định nghĩa rõ ràng
3. **Luận điểm thiếu chứng cứ (Unsupported Claims)** - Tìm các khẳng định thiếu bằng chứng
4. **Nhảy logic (Logical Jumps)** - Phát hiện chuyển đề đột ngột với độ liên kết thấp

### Thông Tin Ngữ Cảnh
{context_block}

### Nội Dung Văn Bản
<<<BẮT ĐẦU VĂN BẢN>>>
{content}
<<<KẾT THÚC VĂN BẢN>>>

---

## NHIỆM VỤ PHỤ 1: MÂU THUẪN LOGIC

### Cần Tìm Kiếm Gì
- Các phát biểu trực tiếp đối lập nhau
- Dữ liệu, con số, ngày tháng, sự kiện xung đột
- Các khẳng định không tương thích về cùng một chủ đề
- Các phát biểu không thể cùng đúng đồng thời

### Quy Tắc Phát Hiện
- So sánh tất cả các cặp câu để tìm mâu thuẫn logic
- Đánh dấu xung đột về số liệu/thời gian (số khác nhau, ngày khác nhau cho cùng một điều)
- Xem xét ngữ cảnh: một số mâu thuẫn có thể là sự đối chiếu có chủ đích
- Mức độ nghiêm trọng: "high" (mâu thuẫn trực tiếp), "medium" (xung đột có khả năng), "low" (xung đột tiềm ẩn)

---

## NHIỆM VỤ PHỤ 2: THUẬT NGỮ CHƯA ĐỊNH NGHĨA

### Cần Tìm Kiếm Gì
Thuật ngữ kỹ thuật, khái niệm chuyên môn, từ viết tắt, hoặc từ vựng chuyên ngành xuất hiện KHÔNG có định nghĩa hoặc giải thích đúng cách tại lần xuất hiện ĐẦU TIÊN.

### Các Mẫu Định Nghĩa Cần Nhận Biết
- "X là..." (X is...)
- "X được hiểu là..." (X is understood as...)
- "X gọi là..." (called X...)
- "X (viết tắt của...)" (X, abbreviation for...)
- "X, hay còn gọi là..." (X, also known as...)
- Giải thích trong ngoặc đơn ngay sau thuật ngữ
- Manh mối ngữ cảnh làm rõ nghĩa

### Quy Tắc
- Theo dõi lần xuất hiện ĐẦU TIÊN của mỗi thuật ngữ
- Kiểm tra các mẫu định nghĩa trong cùng câu hoặc câu liền kề (±1 câu)
- Xem xét độc giả: {writing_type} có thể giả định một số kiến thức nhất định
- Thuật ngữ thông dụng không cần định nghĩa

---

## NHIỆM VỤ PHỤ 3: LUẬN ĐIỂM THIẾU CHỨNG CỨ

### Điều Gì Tạo Thành Một Luận Điểm
- Khẳng định về sự kiện, xu hướng, hoặc mối quan hệ
- Ý kiến được trình bày như sự thật
- Dự đoán hoặc khái quát hóa
- Phát biểu nhân quả
- Phát biểu so sánh hoặc đánh giá

### Điều Gì Tạo Thành Chứng Cứ
- **Dữ liệu/Thống kê**: Số liệu, phần trăm, đo lường
- **Ví dụ**: Nghiên cứu tình huống, kịch bản thực tế, trường hợp cụ thể
- **Trích dẫn**: Tham chiếu đến nghiên cứu, chuyên gia, ấn phẩm
- **Lý luận logic**: Giải thích từng bước dựa trên sự kiện
- **Trích dẫn trực tiếp**: Phát biểu từ nguồn đáng tin cậy

### Quy Tắc Khoảng Cách Chứng Cứ (Quan Trọng!)
Một luận điểm được "hỗ trợ" CHỈ KHI chứng cứ xuất hiện:
- Trong CÙNG câu, HOẶC
- Trong phạm vi ±2 câu (trước hoặc sau), HOẶC
- Trong cùng đoạn văn với mối liên kết RÕ RÀNG

### Chú Ý Đặc Biệt
- Khẳng định tuyệt đối ("luôn luôn", "không bao giờ", "tất cả") cần chứng cứ MẠNH
- Khẳng định so sánh ("tốt hơn", "nhanh hơn") cần dữ liệu so sánh
- Khẳng định định lượng ("giảm 80%") cần phép tính hỗ trợ
- Khẳng định nhân quả ("gây ra", "dẫn đến") cần hỗ trợ logic/thực nghiệm

---

## NHIỆM VỤ PHỤ 4: NHẢY LOGIC

### Cần Tìm Kiếm Gì
Chuyển đề đột ngột khi độ liên kết ngữ nghĩa giữa các đoạn liên tiếp THẤP, cho thấy luồng logic kém.

### Quy Tắc Phát Hiện
- Phân tích độ tương đồng chủ đề giữa các đoạn liên tiếp
- Đánh dấu các chuyển đoạn mà chủ đề thay đổi đột ngột không có cầu nối phù hợp
- Độ liên kết thấp = độ tương đồng < 0.4 (ngưỡng khái niệm gần đúng)
- Xem xét: Liệu chuyển đoạn có cảm giác gượng ép không? Có thiếu mắt xích nào không?

### Điều Gì Tạo Nên Chuyển Đoạn Tốt
- Tính liên tục chủ đề (khái niệm tương tự, ý tưởng liên quan)
- Cụm từ chuyển tiếp rõ ràng ("Hơn nữa", "Tuy nhiên", "Kết quả là")
- Tiến triển logic (nguyên nhân→kết quả, vấn đề→giải pháp, chung→cụ thể)
- Từ khóa hoặc khái niệm chung

### Điều Gì Tạo Nên Nhảy Logic (Xấu)
- Thay đổi chủ đề đột ngột không có chuẩn bị
- Không có cụm từ hoặc ý tưởng kết nối
- Người đọc bối rối về mức độ liên quan
- Thiếu các bước lý luận trung gian

---

## ĐỊNH DẠNG ĐẦU RA

Chỉ trả về JSON hợp lệ với cấu trúc CHÍNH XÁC này:

{{
    "analysis_metadata": {{
        "analyzed_at": "Timestamp ISO",
        "writing_type": "{writing_type}",
        "total_paragraphs": <số>,
        "total_sentences": <số>
    }},
    
    "contradictions": {{
        "total_found": <số>,
        "items": [
            {{
                "id": 1,
                "sentence1": "Toàn bộ văn bản của phát biểu thứ nhất",
                "sentence2": "Toàn bộ văn bản của phát biểu mâu thuẫn",
                "sentence1_location": "Đoạn X, Câu Y",
                "sentence2_location": "Đoạn A, Câu B",
                "contradiction_type": "factual|numerical|temporal|logical",
                "severity": "high|medium|low",
                "explanation": "Giải thích rõ ràng tại sao hai câu này mâu thuẫn",
                "suggestion": "Cách giải quyết mâu thuẫn này"
            }}
        ]
    }},
    
    "undefined_terms": {{
        "total_found": <số>,
        "items": [
            {{
                "term": "gradient clipping",
                "first_appeared": "Đoạn 3, Câu 1",
                "context_snippet": "Trích đoạn ngắn cho thấy thuật ngữ xuất hiện ở đâu...",
                "is_defined": false,
                "reason": "Thuật ngữ xuất hiện không có giải thích hoặc mẫu định nghĩa",
                "suggestion": "Thêm định nghĩa: 'Gradient clipping, một kỹ thuật giới hạn...' hoặc giải thích trong ngữ cảnh"
            }}
        ]
    }},
    
    "unsupported_claims": {{
        "total_found": <số>,
        "items": [
            {{
                "claim": "AI có thể dự đoán hoàn hảo cảm xúc con người",
                "location": "Đoạn 2, Câu 3",
                "status": "unsupported",
                "claim_type": "absolute|comparative|causal|predictive",
                "reason": "Khẳng định tuyệt đối không có dữ liệu hỗ trợ, nghiên cứu, hoặc ví dụ trong phạm vi ±2 câu",
                "surrounding_context": "Trích đoạn ngắn cho thấy luận điểm trong ngữ cảnh...",
                "suggestion": "Thêm trích dẫn nghiên cứu, cung cấp chỉ số độ chính xác, hoặc làm rõ phát biểu"
            }}
        ]
    }},
    
    "logical_jumps": {{
        "total_found": <số>,
        "items": [
            {{
                "from_paragraph": 5,
                "to_paragraph": 6,
                "from_paragraph_summary": "Tóm tắt ngắn gọn chủ đề đoạn 5",
                "to_paragraph_summary": "Tóm tắt ngắn gọn chủ đề đoạn 6",
                "coherence_score": 0.32,
                "flag": "logical_jump",
                "severity": "high|medium|low",
                "explanation": "Tại sao chuyển đoạn này gượng ép hoặc không liên kết",
                "suggestion": "Thêm đoạn chuyển tiếp, dùng cụm từ kết nối, hoặc sắp xếp lại nội dung"
            }}
        ]
    }},
    
    "summary": {{
        "total_issues": <tổng số vấn đề>,
        "critical_issues": <số lượng vấn đề nghiêm trọng cao>,
        "document_quality_score": <0-100>,
        "key_recommendations": [
            "Khuyến nghị quan trọng nhất số 1",
            "Khuyến nghị quan trọng nhất số 2",
            "Khuyến nghị quan trọng nhất số 3"
        ]
    }}
}}

---

## HƯỚNG DẪN QUAN TRỌNG

### Cho TẤT CẢ Nhiệm Vụ Phụ:
1. **Kỹ lưỡng nhưng thực tế** - Tìm vấn đề thực sự, không nitpick
2. **Xem xét loại văn bản** - {writing_type} có tiêu chuẩn cụ thể
3. **Đưa ra gợi ý khả thi** - Nói cho người viết CÁCH sửa, không chỉ CHỖ sai
4. **Ưu tiên theo mức độ nghiêm trọng** - Đánh dấu vấn đề nghiêm trọng là "high", vấn đề nhỏ là "low"
5. **Nhất quán** - Sử dụng đúng cấu trúc JSON đã chỉ định

### Tiêu Chuẩn Chất Lượng Theo Loại Văn Bản:
- **Đề xuất kỹ thuật**: Tiêu chuẩn chứng cứ cao, độ chính xác kỹ thuật, định nghĩa rõ ràng
- **Bài luận học thuật**: Yêu cầu trích dẫn mạnh, thuật ngữ chính thống, luồng logic
- **Văn bản kinh doanh**: Khẳng định dựa trên dữ liệu, tập trung ROI, rõ ràng cho cấp quản lý
- **Bài viết ý kiến**: Lý luận logic, ví dụ hỗ trợ quan điểm, quan điểm rõ ràng

### Triết Lý Phân Tích:
- **Mâu thuẫn logic**: Không khoan nhượng - chúng làm suy yếu độ tin cậy
- **Thuật ngữ chưa định nghĩa**: Định nghĩa thuật ngữ chuyên ngành; kiến thức thông thường OK
- **Luận điểm thiếu chứng cứ**: Chứng cứ trong phạm vi ±2 câu là BẮT BUỘC
- **Nhảy logic**: Luồng mượt mà tăng khả năng đọc và thuyết phục

Chỉ trả về đầu ra JSON. KHÔNG bao gồm code blocks markdown, bình luận, hoặc giải thích bên ngoài cấu trúc JSON.
"""
    
    return prompt