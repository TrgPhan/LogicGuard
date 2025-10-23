import google.generativeai as genai
import json
from typing import List, Dict, Any, Optional
from app.core.config import get_settings

settings = get_settings()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class LLMService:
    """Service for LLM operations using Google Gemini"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def extract_criteria_from_rubric(
        self,
        rubric_text: str,
        writing_type: Optional[str] = None,
        key_constraints: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Extract structured criteria from rubric text using LLM
        
        Args:
            rubric_text: The rubric text to analyze
            writing_type: Optional writing type context (essay, proposal, etc.)
            key_constraints: Optional constraints (word limit, etc.)
            
        Returns:
            {
                "criteria": [
                    {
                        "label": str,
                        "description": str,
                        "weight": float (0-1),
                        "is_mandatory": bool,
                        "order_index": int
                    }
                ],
                "main_goal": str,
                "success_indicators": [str]
            }
        """
        
        # Build context-aware prompt
        context_lines: List[str] = []
        if writing_type:
            context_lines.append(f"Writing Type: {writing_type}")
        if key_constraints:
            formatted_constraints = "\n".join(f"- {item}" for item in key_constraints)
            context_lines.append(f"Key Constraints:\n{formatted_constraints}")
        context_block = "\n".join(context_lines)

        writing_domain = writing_type or "the specified writing task"

        prompt = f"""You are LogicGuard, an expert rubric analyst that converts {writing_domain} rubrics into structured evaluation criteria for an AI writing coach.

### Domain Context
- Audience: Professional reviewers who evaluate clarity, logic, structure, and goal alignment.
- Output usage: Criteria will guide automated feedback, so they must be precise, measurable, and action-oriented.
- Constraint handling: Honor explicit constraints (word count, tone, sources, timeline) as high-priority checks.

### Weighting Guidelines (use these exact bands)
- 1.0 = Critical | Failure means the submission cannot be accepted.
- 0.9 = Essential | Major deduction if missing (core logical or structural expectation).
- 0.7–0.8 = Important | Strongly influences perceived quality and rubric score.
- 0.5–0.6 = Supportive | Adds depth or polish but is not a pass/fail item.
- 0.3–0.4 = Nice to have | Bonus insight, optional polish.
- <= 0.2 = Only if rubric explicitly calls out minor extras.

### Few-shot Example
Input rubric excerpt:
<<<BEGIN EXAMPLE RUBRIC>>>
The essay must present a clear thesis in the introduction, provide evidence in each body paragraph, and close with a synthesized conclusion. Cite at least three scholarly sources and keep between 1,500-1,800 words.
<<<END EXAMPLE RUBRIC>>>

Expected JSON output:
{{
    "main_goal": "Produce a thesis-driven essay supported by scholarly evidence",
    "criteria": [
        {{
            "label": "Thesis Clarity",
            "description": "Introduction presents a specific, arguable thesis that frames the essay's direction",
            "weight": 1.0,
            "is_mandatory": true,
            "order_index": 0
        }},
        {{
            "label": "Evidence Integration",
            "description": "Each body paragraph incorporates at least one scholarly source that supports the main claim",
            "weight": 0.9,
            "is_mandatory": true,
            "order_index": 1
        }},
        {{
            "label": "Conclusion Synthesis",
            "description": "Conclusion synthesizes key insights and reinforces the thesis without repetition",
            "weight": 0.7,
            "is_mandatory": true,
            "order_index": 2
        }},
        {{
            "label": "Word Count Compliance",
            "description": "Total length stays between 1,500 and 1,800 words",
            "weight": 0.6,
            "is_mandatory": true,
            "order_index": 3
        }}
    ],
    "success_indicators": [
        "Thesis clearly stated in the introduction",
        "Body paragraphs reference scholarly sources",
        "Conclusion synthesizes insights",
        "Word count between 1,500-1,800"
    ]
}}

### Actual Rubric to Process
{context_block}

Rubric Text:
<<<BEGIN RUBRIC>>>
{rubric_text}
<<<END RUBRIC>>>

### Instructions
- Produce criteria that cover clarity, logical soundness, structure, and goal alignment.
- Ensure descriptions are specific enough for automated checks.
- Respect the requested weighting bands.
- Order criteria from most to least important.
- Include 2-5 success indicators that describe observable outcomes.

Return ONLY valid JSON matching the example schema. Do not include commentary, markdown fences, or explanations.
"""

        try:
            # Generate response
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response (remove markdown code blocks if present)
            if response_text.startswith("```json"):
                response_text = response_text[7:]  # Remove ```json
            if response_text.startswith("```"):
                response_text = response_text[3:]  # Remove ```
            if response_text.endswith("```"):
                response_text = response_text[:-3]  # Remove trailing ```
            response_text = response_text.strip()
            
            # Parse JSON
            result = json.loads(response_text)
            
            # Validate structure
            if "criteria" not in result or not isinstance(result["criteria"], list):
                raise ValueError("Invalid response structure: missing or invalid 'criteria'")
            
            if "main_goal" not in result:
                result["main_goal"] = "Document writing goal"
            
            if "success_indicators" not in result:
                result["success_indicators"] = []
            
            return result
            
        except json.JSONDecodeError as e:
            # Fallback: return basic structure
            return {
                "main_goal": "Parse rubric and meet criteria",
                "criteria": [
                    {
                        "label": "Meet rubric requirements",
                        "description": rubric_text[:200],
                        "weight": 1.0,
                        "is_mandatory": True,
                        "order_index": 0
                    }
                ],
                "success_indicators": [],
                "error": f"Failed to parse LLM response: {str(e)}"
            }
        except Exception as e:
            raise ValueError(f"LLM extraction failed: {str(e)}")
    
    async def validate_criteria_alignment(
        self,
        criteria: List[Dict[str, Any]],
        writing_type: str,
    ) -> Dict[str, Any]:
        """
        Validate if extracted criteria align with writing type expectations
        
        Args:
            criteria: List of extracted criteria
            writing_type: The writing type (essay, proposal, etc.)
            
        Returns:
            {
                "is_valid": bool,
                "suggestions": [str],
                "missing_elements": [str]
            }
        """
        
        criteria_text = "\n".join(
            [f"- {c['label']}: {c.get('description', '')}" for c in criteria]
        )

        prompt = f"""You are LogicGuard, a senior rubric auditor for {writing_type} assignments.

### Provided Criteria
{criteria_text}

### Evaluation Goals
1. Confirm the set covers core {writing_type} outcomes (clarity, logic, structure, goal alignment, domain-specific needs).
2. Flag any missing critical checks based on typical {writing_type} rubrics.
3. Suggest refinements that make criteria more measurable or aligned with rubric language.

### Reference Weighting Expectations
- 1.0 = critical pass/fail checkpoint.
- 0.9 = essential pillar for success.
- 0.7–0.8 = strongly influences quality.
- <= 0.6 = supportive / polish elements.

### Output Format
Return ONLY valid JSON:
{{
    "is_valid": true/false,
    "suggestions": ["string", ...],
    "missing_elements": ["string", ...]
}}

Guidance:
- Keep suggestions actionable and concise (max 2 sentences each).
- Missing elements should reference rubric-aligned concepts (e.g., "No criterion ensures timeline feasibility").
- If everything looks strong, set "is_valid" to true and leave lists empty.
"""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean markdown
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            result = json.loads(response_text)
            return result
            
        except Exception as e:
            return {
                "is_valid": True,
                "suggestions": [],
                "missing_elements": [],
                "error": str(e)
            }


# Singleton instance
llm_service = LLMService()
