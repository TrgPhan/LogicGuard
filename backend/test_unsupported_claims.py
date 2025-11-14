"""
Test Suite for Unsupported Claims Detection
============================================
File này test toàn bộ chức năng của unsupportedClaims.py

Yêu cầu:
1. Conda environment: logicguard
2. GEMINI_API_KEY trong file .env

Chạy test:
    conda activate logicguard
    cd /home/duo/work/naver/LogicGuard/backend
    python test_unsupported_claims.py
"""

import sys
import os
import json
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Import the functions to test
from app.ai.models.promptStore import prompt_unsupported_claims
from app.ai.models.unsupportedClaims import check_unsupported_claims


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
    """Test 1: Kiểm tra prompt generation"""
    print_section("TEST 1: PROMPT GENERATION")
    
    context = {
        "writing_type": "Technical Proposal",
        "main_goal": "Chứng minh NoSQL có khả năng mở rộng tốt hơn",
        "criteria": ["nhắc đến scalability", "có luận cứ kỹ thuật", "xem xét chi phí"],
        "constraints": ["word_limit: 1000"]
    }
    
    content = """
    NoSQL databases are much better than SQL databases.
    They provide superior performance in all scenarios.
    Our system will reduce costs by 50% with no downsides.
    
    According to a study by Smith et al. (2023), MongoDB achieved 
    2x faster query times in distributed environments with datasets 
    over 1TB.
    """
    
    print("\n📥 Input Context:")
    print(json.dumps(context, indent=2, ensure_ascii=False))
    
    print("\n📄 Input Content:")
    print(content.strip()[:300] + "...")
    
    try:
        prompt = prompt_unsupported_claims(context, content)
        
        print("\n✅ Prompt generated successfully!")
        print(f"📊 Prompt length: {len(prompt)} characters")
        print(f"📊 Prompt lines: {len(prompt.split(chr(10)))} lines")
        
        # Verify prompt contains key elements
        checks = {
            "Contains 'LogicGuard'": "LogicGuard" in prompt,
            "Contains context info": context["writing_type"] in prompt,
            "Contains content": "NoSQL" in prompt,
            "Contains claim definition": "claim" in prompt.lower() or "assertion" in prompt.lower(),
            "Contains evidence types": "data" in prompt.lower() or "evidence" in prompt.lower(),
            "Contains ±2 sentences rule": "±2" in prompt or "+/-2" in prompt or "within 2" in prompt.lower(),
            "Contains output format": "JSON" in prompt or "json" in prompt,
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
            "content": "Some content with claims",
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
            "content": "AI is transforming healthcare. Studies show 90% improvement.",
            "should_fail": False
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        
        try:
            result = check_unsupported_claims(test_case["context"], test_case["content"])
            
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
    print_section("TEST 3: GEMINI API INTEGRATION")
    
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
    
    # Test case with mixed supported and unsupported claims
    context = {
        "writing_type": "Technical Proposal",
        "main_goal": "Propose a new database solution",
        "criteria": ["technical evidence", "cost analysis", "performance data"],
        "constraints": []
    }
    
    content = """
    NoSQL databases are always faster than SQL databases. They provide better 
    scalability and are the future of data storage.
    
    According to a benchmark study by TechResearch (2023), MongoDB processed 
    10,000 queries per second, which is 2.5x faster than PostgreSQL under 
    similar conditions with 1TB datasets.
    
    Our proposed solution will reduce costs by 80%. The system is infinitely 
    scalable and will never experience downtime.
    
    In our pilot test with 100 concurrent users, the response time averaged 
    45ms, meeting the requirement of under 100ms specified in the SLA.
    
    This approach is obviously superior to all alternatives. Everyone knows 
    that cloud solutions are more secure than on-premise systems.
    """
    
    print("\n📄 Testing with sample content...")
    print(f"Content length: {len(content)} characters")
    print(f"Expected: Multiple unsupported claims + some supported claims")
    
    try:
        print("\n⏳ Calling Gemini API (may take a few seconds)...")
        result = check_unsupported_claims(context, content)
        
        print("\n📥 API Response:")
        print(f"  Success: {result['success']}")
        print(f"  Total claims found: {result['total_claims_found']}")
        print(f"  Unsupported claims: {result['total_unsupported']}")
        print(f"  Supported claims: {len(result.get('supported_claims', []))}")
        
        if result["success"]:
            print("\n🔍 Unsupported Claims:")
            if result["unsupported_claims"]:
                for i, claim in enumerate(result["unsupported_claims"][:5], 1):
                    print(f"\n  {i}. {claim['claim'][:80]}...")
                    print(f"     Location: {claim.get('location', 'N/A')}")
                    print(f"     Reason: {claim.get('reason', 'N/A')[:100]}...")
                    print(f"     Suggestion: {claim.get('suggestion', 'N/A')[:100]}...")
                
                if len(result["unsupported_claims"]) > 5:
                    print(f"\n  ... and {len(result['unsupported_claims']) - 5} more")
            else:
                print("  (None found)")
            
            print("\n✅ Supported Claims:")
            if result["supported_claims"]:
                for i, claim in enumerate(result["supported_claims"][:3], 1):
                    print(f"\n  {i}. {claim['claim'][:80]}...")
                    print(f"     Evidence Type: {claim.get('evidence_type', 'N/A')}")
                    print(f"     Evidence: {claim.get('evidence', 'N/A')[:80]}...")
            else:
                print("  (None found)")
            
            # Validate we found both types
            has_unsupported = len(result["unsupported_claims"]) > 0
            has_supported = len(result["supported_claims"]) > 0
            
            if has_unsupported and has_supported:
                print("\n🎉 Test 3 PASSED: API correctly identified both supported and unsupported claims!")
                return True
            elif has_unsupported or has_supported:
                print("\n⚠️  Test 3 PARTIAL: API identified claims but may have missed some")
                return True
            else:
                print("\n❌ Test 3 FAILED: No claims identified")
                return False
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
    content = "AI is revolutionary. Studies show 95% accuracy."
    
    try:
        result = check_unsupported_claims(context, content)
        
        print("\n🔍 Checking response structure...")
        
        required_keys = [
            "success",
            "content",
            "context",
            "total_claims_found",
            "total_unsupported",
            "unsupported_claims",
            "supported_claims",
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
            "total_claims_found is int": isinstance(result["total_claims_found"], int),
            "total_unsupported is int": isinstance(result["total_unsupported"], int),
            "unsupported_claims is list": isinstance(result["unsupported_claims"], list),
            "supported_claims is list": isinstance(result["supported_claims"], list),
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
    print_section("🧪 UNSUPPORTED CLAIMS TEST SUITE", "=")
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
        print("\nModule unsupportedClaims.py hoạt động hoàn toàn bình thường!")
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
║               UNSUPPORTED CLAIMS DETECTION TEST SUITE                      ║
║                                                                            ║
║  This test suite validates all functionality of unsupportedClaims.py       ║
║  including prompt generation, validation, and API integration.             ║
╚════════════════════════════════════════════════════════════════════════════╝
""")
    
    run_all_tests()
    
    print("\n\n💡 Tips:")
    print("  - Để test đầy đủ API integration, set GEMINI_API_KEY trong .env")
    print("  - Module này sử dụng ±2 sentence rule để detect unsupported claims")
    print("  - Claims cần evidence như: data, examples, citations, reasoning")
    print()
