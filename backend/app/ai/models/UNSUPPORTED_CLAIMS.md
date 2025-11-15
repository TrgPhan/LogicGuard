# Unsupported Claims Detection

## Tổng Quan


**Prompt Structure:**
```
1. Task Overview
2. Context Information
3. Document Content
4. What Constitutes a Claim
5. What Constitutes Evidence
6. Evidence Proximity Rule (±2 sentences)
7. Instructions
8. Output Format (JSON)
9. Important Guidelines
10. Special Cases per writing type
```
## Cách Sử Dụng

### Basic Usage:

```python
from app.ai.models.unsupportedClaims import check_unsupported_claims

context = {
    "writing_type": "Technical Proposal",
    "main_goal": "Propose database solution",
    "criteria": ["technical evidence", "cost analysis"],
    "constraints": []
}

content = """
NoSQL databases are always faster than SQL databases.

According to Smith (2023), MongoDB achieved 2x faster 
query times in distributed environments.
"""

result = check_unsupported_claims(context, content)

if result["success"]:
    print(f"Found {result['total_unsupported']} unsupported claims")
    
    for claim in result["unsupported_claims"]:
        print(f"\nClaim: {claim['claim']}")
        print(f"Reason: {claim['reason']}")
        print(f"Suggestion: {claim['suggestion']}")
```

## Output Structure

```python
{
    "success": bool,
    "content": str,
    "context": dict,
    "total_claims_found": int,
    "total_unsupported": int,
    "unsupported_claims": [
        {
            "claim": str,
            "location": str,  # "Paragraph 2, Sentence 3"
            "status": "unsupported",
            "reason": str,
            "surrounding_context": str,
            "suggestion": str  # Specific improvement suggestions
        }
    ],
    "supported_claims": [
        {
            "claim": str,
            "location": str,
            "status": "supported",
            "evidence_type": str,  # "citation with data", "example", etc.
            "evidence": str
        }
    ],
    "metadata": {
        "analyzed_at": str,
        "model": str,
        "error": Optional[str]
    }
}
```

## Key Features

### 1. Evidence Proximity Rule (±2 Sentences)
Claims được coi là "supported" nếu evidence xuất hiện:
- Trong cùng câu
- Trong ±2 câu (trước hoặc sau)
- Trong cùng paragraph với clear connection

### 2. Claim Classification
- **Factual claims**: Assertions về facts, trends
- **Opinion as fact**: Opinions presented as facts
- **Predictions**: Future-oriented claims
- **Comparisons**: "better", "faster", "more"
- **Causal claims**: "causes", "leads to", "results in"

### 3. Evidence Types Recognized
- **Data/Statistics**: Numbers, percentages, measurements
- **Examples**: Case studies, scenarios, instances
- **Citations**: References to studies, experts, sources
- **Logical reasoning**: Step-by-step explanations
- **Quotations**: Direct statements from credible sources

### 4. Special Handling

**Absolute statements** ("always", "never", "all"):
- Require STRONG evidence
- Flagged as high-priority unsupported if lacking

**Comparative claims** ("better", "faster"):
- Need comparative data or benchmarks
- Should specify conditions

**Quantified claims** ("80% reduction", "2x faster"):
- Need supporting calculations or measurements
- Should cite sources

## Examples from Test

### Unsupported Claims Detected:

1. **"NoSQL databases are always faster than SQL databases"**
   - Reason: Absolute comparative claim without benchmarks
   - Suggestion: Provide specific benchmarks, specify conditions

2. **"Our proposed solution will reduce costs by 80%"**
   - Reason: Specific quantifiable claim without cost analysis
   - Suggestion: Provide detailed cost breakdown, ROI calculations

3. **"The system is infinitely scalable"**
   - Reason: Absolute claim without technical specifications
   - Suggestion: Provide architectural details, stress test results

### Supported Claims Detected:

1. **"MongoDB processed 10,000 qps, 2.5x faster (TechResearch 2023)"**
   - Evidence Type: Citation with data
   - Evidence: References study + specific metrics

2. **"Response time averaged 45ms in pilot test with 100 users"**
   - Evidence Type: Data from testing
   - Evidence: Specific quantifiable metrics from experiment


## ⚙️ Configuration

Same as `undefinedTerms.py`:

```bash
# .env file
GEMINI_API_KEY_UNSUPPORTED_CLAIMSGEMINI_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash
```
