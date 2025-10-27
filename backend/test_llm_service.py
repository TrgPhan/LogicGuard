"""
Test script for LLM Service - Context Setup (Task 1)
Tests the extraction of criteria from rubric text using Gemini
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.llm_service import llm_service
import json


async def test_basic_extraction():
    """Test basic criteria extraction"""
    print("\n" + "="*80)
    print("TEST 1: Basic Criteria Extraction")
    print("="*80)
    
    rubric_text = """
    Bài essay phải có:
    - Thesis statement rõ ràng
    - Ít nhất 3 luận điểm chính với dẫn chứng cụ thể
    - Kết luận tóm tắt đầy đủ
    """
    
    print(f"\nRubric Text:\n{rubric_text}")
    print("\nExtracting...")
    
    result = await llm_service.extract_criteria_from_rubric(
        rubric_text=rubric_text,
        writing_type="Essay"
    )
    
    print("\n📊 Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"\n✅ Extracted {len(result.get('criteria', []))} criteria")
    return result


async def test_technical_proposal():
    """Test technical proposal extraction"""
    print("\n" + "="*80)
    print("TEST 2: Technical Proposal Extraction")
    print("="*80)
    
    rubric_text = """
    Đề xuất kỹ thuật phải chứng minh NoSQL có khả năng mở rộng tốt hơn.
    Yêu cầu:
    - Có luận cứ kỹ thuật về scalability
    - Phân tích chi phí so với SQL
    - Timeline triển khai thực tế
    - So sánh performance với RDBMS
    """
    
    constraints = "word_limit: 1000, deadline: 2 weeks"
    
    print(f"\nRubric Text:\n{rubric_text}")
    print(f"\nConstraints: {constraints}")
    print("\nExtracting...")
    
    result = await llm_service.extract_criteria_from_rubric(
        rubric_text=rubric_text,
        writing_type="Technical Proposal",
        key_constraints=constraints
    )
    
    print("\n📊 Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Analyze result
    criteria = result.get('criteria', [])
    print(f"\n✅ Extracted {len(criteria)} criteria")
    
    if criteria:
        print("\n📋 Criteria Summary:")
        for c in criteria:
            mandatory = "🔴 MANDATORY" if c.get('is_mandatory') else "⚪ Optional"
            weight = c.get('weight', 0)
            print(f"  {mandatory} [{weight:.1f}] {c.get('label')}")
            print(f"    └─ {c.get('description', '')[:100]}...")
    
    return result


async def test_validation():
    """Test criteria validation"""
    print("\n" + "="*80)
    print("TEST 3: Criteria Validation")
    print("="*80)
    
    test_criteria = [
        {
            "label": "Scalability demonstration",
            "description": "Chứng minh NoSQL mở rộng tốt",
            "weight": 1.0,
            "is_mandatory": True
        },
        {
            "label": "Cost analysis",
            "description": "Phân tích chi phí",
            "weight": 0.7,
            "is_mandatory": False
        }
    ]
    
    print("\nCriteria to validate:")
    print(json.dumps(test_criteria, indent=2, ensure_ascii=False))
    print("\nValidating for 'Technical Proposal'...")
    
    result = await llm_service.validate_criteria_alignment(
        criteria=test_criteria,
        writing_type="Technical Proposal"
    )
    
    print("\n📊 Validation Result:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result.get('is_valid'):
        print("\n✅ Criteria are valid")
    else:
        print("\n⚠️ Criteria need improvement")
    
    if result.get('suggestions'):
        print("\n💡 Suggestions:")
        for s in result['suggestions']:
            print(f"  - {s}")
    
    if result.get('missing_elements'):
        print("\n❌ Missing elements:")
        for m in result['missing_elements']:
            print(f"  - {m}")
    
    return result


async def test_edge_cases():
    """Test edge cases"""
    print("\n" + "="*80)
    print("TEST 4: Edge Cases")
    print("="*80)
    
    # Test 1: Very short rubric
    print("\n📝 Test 4.1: Very short rubric")
    result1 = await llm_service.extract_criteria_from_rubric(
        rubric_text="Viết tốt và rõ ràng.",
        writing_type="Blog Post"
    )
    print(f"✅ Extracted {len(result1.get('criteria', []))} criteria from minimal text")
    
    # Test 2: Vietnamese + English mixed
    print("\n📝 Test 4.2: Mixed language rubric")
    result2 = await llm_service.extract_criteria_from_rubric(
        rubric_text="""
        Technical report must include:
        - Executive summary bằng tiếng Việt
        - Data analysis với charts
        - Recommendations dựa trên findings
        """,
        writing_type="Report"
    )
    print(f"✅ Extracted {len(result2.get('criteria', []))} criteria from mixed language")
    
    # Test 3: Long detailed rubric
    print("\n📝 Test 4.3: Long detailed rubric")
    long_rubric = """
    Bài pitch deck cho startup cần:
    1. Problem statement: Mô tả vấn đề thị trường một cách sinh động, dùng data để support
    2. Solution: Giải pháp độc đáo, có demo/prototype nếu có thể
    3. Market size: TAM, SAM, SOM với số liệu cụ thể
    4. Business model: Rõ ràng cách kiếm tiền, pricing strategy
    5. Traction: Metrics, users, revenue (nếu có)
    6. Team: Background của founders, advisors
    7. Competition: So sánh với đối thủ, competitive advantage
    8. Financial projections: 3-5 năm, realistic
    9. Ask: Cần bao nhiêu vốn, dùng vào đâu
    """
    result3 = await llm_service.extract_criteria_from_rubric(
        rubric_text=long_rubric,
        writing_type="Pitch Deck",
        key_constraints="10-15 slides, 10 minutes presentation"
    )
    print(f"✅ Extracted {len(result3.get('criteria', []))} criteria from detailed rubric")
    print(f"   Main goal: {result3.get('main_goal', 'N/A')[:80]}...")
    
    return result1, result2, result3


async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 LogicGuard LLM Service - Context Setup Tests")
    print("="*80)
    print("Testing Gemini 2.5 Flash for criteria extraction from rubric text")
    
    try:
        # Run tests
        await test_basic_extraction()
        await test_technical_proposal()
        await test_validation()
        await test_edge_cases()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nNext steps:")
        print("1. Check if criteria are accurate and well-structured")
        print("2. Verify weights and mandatory flags are appropriate")
        print("3. Test with real rubrics from your use cases")
        print("4. Proceed to Step 3: Create Goal validation endpoints")
        
    except Exception as e:
        print("\n" + "="*80)
        print("❌ TEST FAILED")
        print("="*80)
        print(f"\nError: {str(e)}")
        print("\nPlease check:")
        print("1. GEMINI_API_KEY is set correctly in .env")
        print("2. API key is valid and active")
        print("3. Internet connection is working")
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
