# Comprehensive Analysis - 4 Subtasks Unified

## 📋 Tổng Quan

Module này gộp **4 subtasks phân tích văn bản** vào một lần gọi API duy nhất để tối ưu hiệu suất và chi phí:

1. **SUBTASK 1: Contradictions** - Phát hiện mâu thuẫn logic
2. **SUBTASK 2: Undefined Terms** - Phát hiện thuật ngữ chưa định nghĩa
3. **SUBTASK 3: Unsupported Claims** - Phát hiện luận điểm thiếu chứng cứ
4. **SUBTASK 4: Logical Jumps** (NEW) - Phát hiện nhảy logic giữa các đoạn

## 🎯 Mục Tiêu

- **Hiệu quả**: 1 API call thay vì 4 calls riêng lẻ → Tiết kiệm thời gian và chi phí
- **Toàn diện**: Phân tích đồng thời tất cả khía cạnh logic, terminology, evidence, và coherence
- **Thông minh**: Summary section cung cấp insights xuyên suốt 4 subtasks

## 🏗️ Kiến Trúc

### Files

```
backend/app/ai/models/
├── promptStore.py                    # Chứa prompt_comprehensive_analysis()
├── comprehensiveAnalysis.py          # Implementation
└── README_COMPREHENSIVE.md           # Documentation này

backend/
└── test_comprehensive_analysis.py    # Test suite (5 tests)
```

### Functions

#### 1. `prompt_comprehensive_analysis(context, content)`
**Location**: `promptStore.py`

Tạo unified prompt cho LLM phân tích 4 subtasks cùng lúc.

**Input**:
```python
context = {
    "writing_type": "Research Paper",
    "main_goal": "Present findings on AI",
    "criteria": ["scientific rigor", "clear evidence"],
    "constraints": ["3000 words", "peer-reviewed"]
}
content = "Full document text..."
```

**Output**: String prompt ~8,600 characters

**Structure**:
- Role definition: LogicGuard expert AI analyst
- Mission: 4-dimensional comprehensive analysis
- Context information
- Document content
- Detailed rules for each subtask
- Unified JSON output format
- Quality guidelines

---

#### 2. `analyze_document_comprehensive(context, content)`
**Location**: `comprehensiveAnalysis.py`

Main analysis function sử dụng Gemini API.

**Input**:
- `context`: Dict với writing_type, main_goal, criteria, constraints
- `content`: String văn bản cần phân tích

**Output**: Dict với structure:

```python
{
    "success": bool,
    "content": str,                    # Original content
    "context": dict,                   # Original context
    
    "analysis_metadata": {
        "analyzed_at": "2024-07-30T12:00:00Z",
        "writing_type": "Research Paper",
        "total_paragraphs": 10,
        "total_sentences": 45,
        "model": "gemini-2.5-flash"
    },
    
    "contradictions": {
        "total_found": 2,
        "items": [
            {
                "sentence1": "AI will revolutionize education",
                "sentence2": "AI should be banned from schools",
                "paragraph1": 1,
                "paragraph2": 3,
                "distance": 2,
                "explanation": "Direct contradiction...",
                "type": "direct",
                "severity": "high"
            }
        ]
    },
    
    "undefined_terms": {
        "total_found": 5,
        "items": [
            {
                "term": "Neural networks",
                "first_occurrence": "Paragraph 2",
                "context": "Neural networks use backpropagation...",
                "defined": false,
                "reason": "Technical term without definition",
                "importance": "high"
            }
        ]
    },
    
    "unsupported_claims": {
        "total_found": 3,
        "items": [
            {
                "claim": "AI improves test scores by 300%",
                "paragraph": 4,
                "proximity_check": "No evidence within ±2 sentences",
                "evidence_type": "none",
                "severity": "high",
                "suggestion": "Add citation or data source"
            }
        ]
    },
    
    "logical_jumps": {
        "total_found": 2,
        "items": [
            {
                "from_paragraph": 5,
                "to_paragraph": 6,
                "from_topic": "Machine learning in education",
                "to_topic": "Climate change policy",
                "coherence_score": 0.1,
                "missing_link": "No connection established",
                "severity": "critical"
            }
        ]
    },
    
    "summary": {
        "total_issues": 12,
        "critical_issues": 4,
        "document_quality_score": 35,  # 0-100
        "key_recommendations": [
            "Resolve contradictions about AI impact",
            "Define all technical terms on first use",
            "Add citations for quantitative claims",
            "Improve paragraph transitions"
        ]
    },
    
    "metadata": {
        "error": null  # or error message if failed
    }
}
```

**Process**:
1. Validate inputs (content not empty, context is dict)
2. Generate comprehensive prompt
3. Call Gemini API
4. Parse unified JSON response
5. Extract all 4 subtask results
6. Calculate summary metrics
7. Return structured result

---

#### 3. `get_analysis_summary(analysis_result)`
**Location**: `comprehensiveAnalysis.py`

Tạo human-readable text summary từ JSON result.

**Input**: Dict từ `analyze_document_comprehensive()`

**Output**: Formatted string summary

**Example**:
```
================================================================================
DOCUMENT ANALYSIS SUMMARY
================================================================================

Writing Type: Research Paper
Total Paragraphs: 10
Total Sentences: 45
Analyzed At: 2024-07-30T12:00:00Z

📊 OVERALL QUALITY SCORE: 35/100
Total Issues Found: 12
Critical Issues: 4

🔴 CONTRADICTIONS: 2 found
  - AI will revolutionize education... ↔ AI should be banned...

📚 UNDEFINED TERMS: 5 found
  - Neural networks
  - Backpropagation
  - Gradient descent

⚠️  UNSUPPORTED CLAIMS: 3 found
  - AI improves test scores by 300%...

🔀 LOGICAL JUMPS: 2 found
  - Paragraph 5 → 6 (coherence: 0.1/10)

💡 KEY RECOMMENDATIONS:
  1. Resolve contradictions about AI impact
  2. Define technical terms on first use
  3. Add citations for claims
  4. Improve paragraph transitions
```

---

## 🚀 Usage

### Basic Usage

```python
from comprehensiveAnalysis import analyze_document_comprehensive, get_analysis_summary

# Setup context
context = {
    "writing_type": "Academic Essay",
    "main_goal": "Argue thesis on climate change",
    "criteria": ["evidence-based", "logical coherence"],
    "constraints": ["1500-2000 words", "peer-reviewed sources"]
}

# Your document
content = """
Your document text here...
Multiple paragraphs...
"""

# Run comprehensive analysis
result = analyze_document_comprehensive(context, content)

# Check success
if result["success"]:
    print(f"✅ Analysis complete!")
    print(f"Total issues: {result['summary']['total_issues']}")
    print(f"Quality score: {result['summary']['document_quality_score']}/100")
    
    # Get individual subtask results
    print(f"Contradictions: {result['contradictions']['total_found']}")
    print(f"Undefined Terms: {result['undefined_terms']['total_found']}")
    print(f"Unsupported Claims: {result['unsupported_claims']['total_found']}")
    print(f"Logical Jumps: {result['logical_jumps']['total_found']}")
    
    # Print formatted summary
    summary_text = get_analysis_summary(result)
    print(summary_text)
else:
    print(f"❌ Error: {result['metadata']['error']}")
```

### Advanced Usage - Access Specific Issues

```python
result = analyze_document_comprehensive(context, content)

# Get all contradictions
for contra in result["contradictions"]["items"]:
    print(f"Contradiction: {contra['sentence1']} ↔ {contra['sentence2']}")
    print(f"Severity: {contra['severity']}")
    print(f"Distance: {contra['distance']} paragraphs")
    print()

# Get critical undefined terms
for term in result["undefined_terms"]["items"]:
    if term.get("importance") == "high":
        print(f"❗ Define term: {term['term']}")
        print(f"   Context: {term['context']}")

# Get high-severity unsupported claims
for claim in result["unsupported_claims"]["items"]:
    if claim.get("severity") == "high":
        print(f"⚠️  Needs evidence: {claim['claim']}")
        print(f"   Suggestion: {claim['suggestion']}")

# Get critical logical jumps
for jump in result["logical_jumps"]["items"]:
    if jump["coherence_score"] < 0.3:
        print(f"🔀 Critical jump detected:")
        print(f"   From P{jump['from_paragraph']}: {jump['from_topic']}")
        print(f"   To P{jump['to_paragraph']}: {jump['to_topic']}")
        print(f"   Coherence: {jump['coherence_score']}/10")
```

---

## 🔧 Configuration

### Environment Variables

Required in `.env`:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### Dependencies

```python
google-generativeai
python-dotenv
typing
datetime
json
```

---

## 🧪 Testing

### Run Tests

```bash
cd backend
conda activate logicguard
python test_comprehensive_analysis.py
```

### Test Suite (5 Tests)

1. **Prompt Generation**: Validates unified prompt structure
2. **Input Validation**: Tests empty content and invalid context
3. **API Integration**: Full end-to-end test with complex document
4. **Response Structure**: Validates JSON output schema
5. **Human-Readable Summary**: Tests summary generator

**Expected Result**: ✅ 5/5 tests passed (100%)

---

## 📊 Comparison: Unified vs Individual

### Individual Approach (Old)

```python
# 4 separate API calls
result1 = check_contradictions(context, content)
result2 = check_undefined_terms(context, content) 
result3 = check_unsupported_claims(context, content)
result4 = check_logical_jumps(context, content)

# Combine results manually
total_issues = (
    result1["total"] + result2["total"] + 
    result3["total"] + result4["total"]
)
```

**Drawbacks**:
- ❌ 4x API calls → 4x cost, 4x latency
- ❌ No cross-subtask insights
- ❌ Manual result aggregation
- ❌ Harder to maintain consistency

### Unified Approach (New)

```python
# 1 API call for all 4 subtasks
result = analyze_document_comprehensive(context, content)

# All results in one structure
total_issues = result["summary"]["total_issues"]
```

**Benefits**:
- ✅ 1 API call → 75% cost reduction, faster
- ✅ Cross-subtask analysis in summary
- ✅ Automatic aggregation
- ✅ Consistent analysis context

---

## 🎓 Subtask Details

### SUBTASK 1: Contradictions

**What it detects**:
- Direct contradictions between statements
- Contradictory implications
- Conflicting evidence/data
- Logical inconsistencies

**Example**:
```
"AI will revolutionize education" ↔ "AI should be banned from schools"
Type: direct
Severity: high
```

---

### SUBTASK 2: Undefined Terms

**What it detects**:
- Technical terminology without definition
- Specialized jargon
- Domain-specific terms
- Acronyms not expanded

**Rules**:
- Check first occurrence
- Consider audience (writing_type)
- Common terms may not need definition
- Technical papers need more definitions

**Example**:
```
Term: "Neural networks"
Context: "Neural networks use backpropagation..."
Defined: false
Importance: high
Reason: "Technical term without definition for general audience"
```

---

### SUBTASK 3: Unsupported Claims

**What it detects**:
- Assertions without evidence
- Claims lacking citations
- Unsubstantiated statistics
- Opinions stated as facts

**Proximity Rule**: Check ±2 sentences for supporting evidence

**Example**:
```
Claim: "AI improves test scores by 300%"
Proximity: "No evidence within ±2 sentences"
Evidence type: none
Severity: high
Suggestion: "Add citation with source data"
```

---

### SUBTASK 4: Logical Jumps (NEW)

**What it detects**:
- Abrupt topic changes between paragraphs
- Missing transitional connections
- Incoherent document flow
- Non-sequitur conclusions

**Coherence Score**: 0.0 (worst) to 1.0 (perfect)
- < 0.3: Critical jump
- 0.3-0.6: Moderate jump
- > 0.6: Good transition

**Example**:
```
From P5: "Machine learning in education"
To P6: "Climate change policy reform"
Coherence: 0.1/10
Missing link: "No connection established between topics"
Severity: critical
```

---

## 💡 Key Recommendations Logic

Summary section generates smart recommendations by analyzing patterns across all 4 subtasks:

**Examples**:
- "Resolve all direct contradictions to ensure consistent thesis" ← from contradictions
- "Define technical terms on first use" ← from undefined_terms
- "Add citations for quantitative claims" ← from unsupported_claims  
- "Improve paragraph transitions" ← from logical_jumps
- "Address critical issues before submission" ← from overall severity

---

## 🎯 Quality Score Calculation

`document_quality_score` (0-100):

```
Base score: 100
Deductions:
- Each critical issue: -15 points
- Each high severity issue: -10 points
- Each moderate issue: -5 points
- Each low severity issue: -2 points
- Logical jumps penalty: -(10 - coherence_score * 10) each

Minimum: 0
Maximum: 100
```

**Interpretation**:
- 90-100: Excellent
- 70-89: Good
- 50-69: Needs improvement
- 30-49: Significant issues
- 0-29: Major revision required

---

## 🔍 Best Practices

### When to Use Comprehensive Analysis

✅ **Use unified approach when**:
- Analyzing complete documents
- Need holistic quality assessment
- Want cross-subtask insights
- Need to minimize API costs
- Time efficiency matters

❌ **Use individual subtasks when**:
- Debugging specific issue type
- Only need one type of analysis
- Testing/development
- Already using contradictions.py (NLI-based)

### Document Preparation

```python
# Good: Clean, structured content
content = """
Introduction

Clear topic sentence. Supporting evidence with citation [1]. 
Logical flow to next point.

Body Paragraph 1

Technical term is defined as "...". Evidence follows claim. 
Smooth transition to next topic.
"""

# Bad: Messy, unstructured
content = "random text no paragraphs lots of claims AI is 300% better!!!"
```

---

## ⚠️ Known Limitations

1. **LLM Consistency**: Results may vary slightly between runs
2. **Language**: Optimized for English and Vietnamese
3. **Context Window**: Very long documents (>10,000 words) may need chunking
4. **API Costs**: Still uses paid Gemini API (cheaper than 4 calls)
5. **Response Time**: ~10-30 seconds depending on document length

---

## 🔄 Migration Guide

### From Individual Subtasks

**Old code**:
```python
from undefinedTerms import check_undefined_terms
from unsupportedClaims import check_unsupported_claims

terms_result = check_undefined_terms(context, content)
claims_result = check_unsupported_claims(context, content)
```

**New code**:
```python
from comprehensiveAnalysis import analyze_document_comprehensive

result = analyze_document_comprehensive(context, content)
terms = result["undefined_terms"]["items"]
claims = result["unsupported_claims"]["items"]
```

**Benefits**: 1 API call instead of 2, unified format, better insights

---

## 📚 API Reference

### Function Signatures

```python
def prompt_comprehensive_analysis(
    context: Dict[str, Any], 
    content: str
) -> str:
    """Generate unified prompt for 4 subtasks"""
    pass

def analyze_document_comprehensive(
    context: Dict[str, Any], 
    content: str
) -> Dict[str, Any]:
    """Run comprehensive analysis via Gemini API"""
    pass

def get_analysis_summary(
    analysis_result: Dict[str, Any]
) -> str:
    """Generate human-readable summary"""
    pass
```

### Type Definitions

```python
Context = {
    "writing_type": str,          # Required
    "main_goal": str,             # Optional
    "criteria": List[str],        # Optional
    "constraints": List[str]      # Optional
}

AnalysisResult = {
    "success": bool,
    "content": str,
    "context": Context,
    "analysis_metadata": Metadata,
    "contradictions": SubtaskResult,
    "undefined_terms": SubtaskResult,
    "unsupported_claims": SubtaskResult,
    "logical_jumps": SubtaskResult,
    "summary": Summary,
    "metadata": {"error": Optional[str]}
}
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "GEMINI_API_KEY not found"**
```bash
# Check .env file exists
ls -la backend/.env

# Verify key is set
grep GEMINI_API_KEY backend/.env
```

**2. "JSON parse error"**
- LLM response may have markdown wrappers
- Code automatically strips ```json blocks
- Check raw response in error message

**3. "Empty content error"**
```python
# Ensure content is not empty
if not content.strip():
    print("Content is empty!")
```

**4. Import errors in tests**
```python
# Tests add correct path
sys.path.insert(0, 'app/ai/models')
```

---

## 📈 Performance Metrics

### Test Results

**Document**: 300 words, 3 paragraphs, intentionally flawed

**Results**:
- Contradictions: 2 found
- Undefined Terms: 10 found
- Unsupported Claims: 7 found
- Logical Jumps: 3 found
- **Total**: 22 issues
- **Quality Score**: 5/100 (intentionally poor document)
- **Processing Time**: ~15 seconds

**Test Suite**: 5/5 passed ✅

---

## 🎉 Success Criteria

✅ **Implementation Complete**:
- [x] Unified prompt function
- [x] Comprehensive analysis function
- [x] Summary generator
- [x] Full test suite (5/5 passed)
- [x] Comprehensive documentation

✅ **Quality Metrics**:
- [x] All 4 subtasks functional
- [x] JSON parsing robust
- [x] Error handling complete
- [x] Human-readable output

✅ **Performance**:
- [x] Single API call
- [x] < 30 seconds for typical document
- [x] Accurate issue detection

---

## 🚀 Next Steps

### Potential Enhancements

1. **Caching**: Cache results for identical documents
2. **Streaming**: Stream partial results as analysis progresses
3. **Confidence Scores**: Add confidence levels to each finding
4. **Multi-language**: Expand beyond English/Vietnamese
5. **Integration**: Connect to contradictions.py NLI models
6. **UI**: Build frontend visualization for results
7. **Batch Processing**: Analyze multiple documents in parallel

---

## 📞 Support

For issues or questions:
1. Check test results: `python test_comprehensive_analysis.py`
2. Review error messages in `result["metadata"]["error"]`
3. Verify environment setup (conda, .env, API key)
4. Check documentation for similar issues

---

**Created**: 2024-11-18  
**Version**: 1.0.0  
**Status**: ✅ Production Ready  
**Test Coverage**: 5/5 tests passing (100%)
