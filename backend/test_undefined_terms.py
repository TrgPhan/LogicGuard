"""
Test Suite for Undefined Terms Detection
=========================================
File này test toàn bộ chức năng của undefinedTerms.py

Yêu cầu:
1. Conda environment: logicguard
2. GEMINI_API_KEY trong file .env

Chạy test:
    conda activate logicguard
    cd /home/duo/work/naver/LogicGuard/backend
    python test_undefined_terms_full.py
"""

import sys
import os
import json
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import the functions to test
from app.ai.models.promptStore import prompt_undefined_terms
from app.ai.models.undefinedTerms import check_undefined_terms


def print_section(title, char="="):
    """Print a formatted section header"""
    width = 80
    print("\n" + char * width)
    print(title.center(width))
    print(char * width)


def print_subsection(title):
    """Print a formatted subsection"""
    print("\n" + "-" * 80)
    print(title)
    print("-" * 80)


def test_prompt_generation():
    """Test 1: Kiểm tra prompt generation (Task 1)"""
    print_section("TEST 1: PROMPT GENERATION (Task 1)")
    
    context = {
        "writing_type": "Technical Proposal",
        "main_goal": "Chứng minh NoSQL có khả năng mở rộng tốt hơn",
        "criteria": ["nhắc đến scalability", "có luận cứ kỹ thuật", "xem xét chi phí"],
        "constraints": ["word_limit: 1000"]
    }
    
    content = """
    NoSQL databases provide horizontal scalability for modern applications.
    Gradient clipping is used in deep learning training.
    Sharding allows distribution of data across multiple servers.
    
    Scalability, which is the ability to handle growing workload, is crucial.
    ACID properties ensure data consistency.
    """
    
    print("\n📥 Input Context:")
    print(json.dumps(context, indent=2, ensure_ascii=False))
    
    print("\n📄 Input Content:")
    print(content.strip()[:200] + "...")
    
    try:
        prompt = prompt_undefined_terms(context, content)
        
        print("\n✅ Prompt generated successfully!")
        print(f"📊 Prompt length: {len(prompt)} characters")
        print(f"📊 Prompt lines: {len(prompt.split(chr(10)))} lines")
        
        # Verify prompt contains key elements
        checks = {
            "Contains 'LogicGuard'": "LogicGuard" in prompt,
            "Contains context info": context["writing_type"] in prompt,
            "Contains content": "NoSQL" in prompt,
            "Contains definition patterns": "là" in prompt or "is..." in prompt,
            "Contains output format": "JSON" in prompt or "json" in prompt,
            "Contains instructions": "Instructions" in prompt or "instructions" in prompt,
        }
        
        print("\n🔍 Prompt Validation:")
        all_passed = True
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"  {status} {check}")
            if not result:
                all_passed = False
        
        if all_passed:
            print("\n🎉 Test 1 PASSED: Prompt generation hoạt động tốt!")
            return True
        else:
            print("\n⚠️  Test 1 WARNING: Một số checks không pass")
            return False
            
    except Exception as e:
        print(f"\n❌ Test 1 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_input_validation():
    """Test 2: Kiểm tra input validation"""
    print_section("TEST 2: INPUT VALIDATION")
    
    test_cases = [
        {
            "name": "Empty content",
            "context": {"writing_type": "Essay"},
            "content": "",
            "should_fail": True
        },
        {
            "name": "None content",
            "context": {"writing_type": "Essay"},
            "content": None,
            "should_fail": True
        },
        {
            "name": "Invalid context (None)",
            "context": None,
            "content": "Some content",
            "should_fail": True
        },
        {
            "name": "Invalid context (not dict)",
            "context": "not a dict",
            "content": "Some content",
            "should_fail": True
        },
        {
            "name": "Valid inputs",
            "context": {"writing_type": "Essay"},
            "content": "Machine learning is a subset of AI.",
            "should_fail": False
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        
        try:
            result = check_undefined_terms(test_case["context"], test_case["content"])
            
            if test_case["should_fail"]:
                if not result["success"]:
                    print(f"  ✅ Correctly rejected invalid input")
                    print(f"     Error: {result['metadata']['error']}")
                    passed += 1
                else:
                    print(f"  ❌ Should have failed but succeeded")
                    failed += 1
            else:
                # For valid inputs, we expect either success or API error (if no key)
                if result["success"] or "GEMINI_API_KEY" in str(result.get("metadata", {}).get("error", "")):
                    print(f"  ✅ Accepted valid input")
                    passed += 1
                else:
                    print(f"  ❌ Unexpected error: {result['metadata']['error']}")
                    failed += 1
                    
        except Exception as e:
            if test_case["should_fail"]:
                print(f"  ✅ Correctly raised exception: {str(e)[:50]}...")
                passed += 1
            else:
                print(f"  ❌ Unexpected exception: {str(e)}")
                failed += 1
    
    print(f"\n📊 Results: {passed}/{len(test_cases)} passed")
    
    if failed == 0:
        print("🎉 Test 2 PASSED: Input validation hoạt động đúng!")
        return True
    else:
        print("❌ Test 2 FAILED: Một số validation checks failed")
        return False


def test_api_integration():
    """Test 3: Kiểm tra API integration với Gemini (cần API key)"""
    print_section("TEST 3: GEMINI API INTEGRATION (Task 2)")
    
    # Check if API key is available
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or api_key == "your-gemini-api-key-here":
        print("\n⚠️  SKIPPING: GEMINI_API_KEY not set in .env file")
        print("To run this test:")
        print("1. Get API key from: https://makersuite.google.com/app/apikey")
        print("2. Add to .env: GEMINI_API_KEY=your-key-here")
        return None
    
    print(f"\n✅ API Key found (length: {len(api_key)})")
    print(f"✅ Model: {os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')}")
    
    # Test case with mixed definitions
    context = {
        "writing_type": "Technical Article",
        "main_goal": "Explain machine learning concepts",
        "criteria": ["clear definitions", "technical accuracy"],
        "constraints": []
    }
    
    content = """
    Machine learning is a subset of artificial intelligence that enables systems to learn from data.
    
    Neural networks use gradient descent for optimization. Backpropagation calculates gradients.
    
    Overfitting occurs when a model learns the training data too well, including noise.
    
    Regularization techniques like dropout and L2 help prevent overfitting.
    """
    
    print("\n📄 Testing with sample content...")
    print(f"Content length: {len(content)} characters")
    
    try:
        print("\n⏳ Calling Gemini API (may take a few seconds)...")
        result = check_undefined_terms(context, content)
        
        print("\n📥 API Response:")
        print(f"  Success: {result['success']}")
        print(f"  Total terms found: {result['total_terms_found']}")
        print(f"  Undefined terms: {result['total_undefined']}")
        print(f"  Defined terms: {len(result.get('defined_terms', []))}")
        
        if result["success"]:
            print("\n🔍 Undefined Terms:")
            if result["undefined_terms"]:
                for i, term in enumerate(result["undefined_terms"], 1):
                    print(f"\n  {i}. {term['term']}")
                    print(f"     Location: {term.get('first_appeared', 'N/A')}")
                    print(f"     Reason: {term.get('reason', 'N/A')[:80]}...")
            else:
                print("  (None found - all terms were defined)")
            
            print("\n✅ Defined Terms:")
            if result["defined_terms"]:
                for i, term in enumerate(result["defined_terms"][:3], 1):
                    print(f"  {i}. {term['term']} - {term.get('definition_found', 'N/A')[:60]}...")
            else:
                print("  (None found)")
            
            print("\n🎉 Test 3 PASSED: API integration hoạt động tốt!")
            return True
        else:
            print(f"\n❌ API call failed: {result['metadata']['error']}")
            return False
            
    except Exception as e:
        print(f"\n❌ Test 3 FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_response_structure():
    """Test 4: Kiểm tra cấu trúc response"""
    print_section("TEST 4: RESPONSE STRUCTURE")
    
    context = {"writing_type": "Essay"}
    content = "Test content"
    
    try:
        result = check_undefined_terms(context, content)
        
        print("\n🔍 Checking response structure...")
        
        required_keys = [
            "success",
            "content",
            "context",
            "total_terms_found",
            "total_undefined",
            "undefined_terms",
            "defined_terms",
            "metadata"
        ]
        
        metadata_keys = ["analyzed_at", "model", "error"]
        
        # Check top-level keys
        missing_keys = []
        for key in required_keys:
            if key not in result:
                missing_keys.append(key)
        
        if missing_keys:
            print(f"❌ Missing keys: {missing_keys}")
            return False
        else:
            print("✅ All required top-level keys present")
        
        # Check metadata
        metadata_missing = []
        for key in metadata_keys:
            if key not in result["metadata"]:
                metadata_missing.append(key)
        
        if metadata_missing:
            print(f"❌ Missing metadata keys: {metadata_missing}")
            return False
        else:
            print("✅ All metadata keys present")
        
        # Check data types
        type_checks = {
            "success is bool": isinstance(result["success"], bool),
            "total_terms_found is int": isinstance(result["total_terms_found"], int),
            "total_undefined is int": isinstance(result["total_undefined"], int),
            "undefined_terms is list": isinstance(result["undefined_terms"], list),
            "defined_terms is list": isinstance(result["defined_terms"], list),
            "metadata is dict": isinstance(result["metadata"], dict),
        }
        
        print("\n🔍 Type validation:")
        all_passed = True
        for check, passed in type_checks.items():
            status = "✅" if passed else "❌"
            print(f"  {status} {check}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n🎉 Test 4 PASSED: Response structure đúng format!")
            return True
        else:
            print("\n❌ Test 4 FAILED: Một số type checks không pass")
            return False
            
    except Exception as e:
        print(f"\n❌ Test 4 FAILED: {str(e)}")
        return False


def run_all_tests():
    """Run all tests and generate report"""
    print_section("🧪 UNDEFINED TERMS TEST SUITE", "=")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"Python Path: {sys.executable}")
    
    tests = [
        ("Prompt Generation", test_prompt_generation),
        ("Input Validation", test_input_validation),
        ("API Integration", test_api_integration),
        ("Response Structure", test_response_structure),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {str(e)}")
            results[test_name] = False
    
    # Final report
    print_section("📊 TEST SUMMARY", "=")
    
    passed_count = sum(1 for r in results.values() if r is True)
    failed_count = sum(1 for r in results.values() if r is False)
    skipped_count = sum(1 for r in results.values() if r is None)
    total_count = len(results)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASSED"
        elif result is False:
            status = "❌ FAILED"
        else:
            status = "⏭️  SKIPPED"
        print(f"{status:12} - {test_name}")
    
    print("\n" + "=" * 80)
    print(f"Total: {total_count} tests")
    print(f"Passed: {passed_count} ✅")
    print(f"Failed: {failed_count} ❌")
    print(f"Skipped: {skipped_count} ⏭️")
    
    if failed_count == 0 and passed_count > 0:
        print("\n🎉🎉🎉 ALL TESTS PASSED! 🎉🎉🎉")
        print("\nModule undefinedTerms.py hoạt động hoàn toàn bình thường!")
    elif failed_count == 0 and skipped_count > 0:
        print("\n✅ All run tests passed!")
        print("💡 Set GEMINI_API_KEY to run skipped tests")
    else:
        print("\n⚠️  SOME TESTS FAILED")
        print("Please review the errors above")
    
    print("=" * 80)


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                   UNDEFINED TERMS DETECTION TEST SUITE                     ║
║                                                                            ║
║  This test suite validates all functionality of undefinedTerms.py          ║
║  including prompt generation, validation, and API integration.             ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    run_all_tests()
    
    print("\n\n💡 Tips:")
    print("  - Để test đầy đủ API integration, set GEMINI_API_KEY trong .env")
    print("  - Xem README_UNDEFINED_TERMS.md để biết thêm chi tiết")
    print("  - Chạy demo_undefined_terms.py để xem interactive demo")
    print()
