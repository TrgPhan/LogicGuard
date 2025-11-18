"""
Test Language Switching - Chuyển đổi giữa tiếng Anh và tiếng Việt
====================================================================
Test tính năng chuyển đổi ngôn ngữ trong hàm analyze_document()
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'ai', 'models'))

from Analysis import analyze_document


def test_english_language():
    """Test 1: Sử dụng tiếng Anh"""
    print("\n" + "="*80)
    print("TEST 1: ENGLISH LANGUAGE (language='en')")
    print("="*80)
    
    context = {
        "writing_type": "Blog Post",
        "main_goal": "Share programming experience",
        "criteria": ["clear", "practical"],
        "constraints": ["800-1200 words"]
    }
    
    content = """
    Learning programming is not as hard as you think!
    
    I learned Python in just 2 weeks. You just need to practice every day.
    Neural networks are very important. You should learn backpropagation immediately.
    
    However, programming is very dangerous and harmful. You should avoid computers.
    
    Therefore, we need to reform global education immediately.
    """
    
    print("🔍 Analyzing with English prompt (language='en')...")
    result = analyze_document(context, content, language="en")
    
    print(f"\n✅ Success: {result['success']}")
    print(f"✅ Language used: {result['analysis_metadata'].get('language', 'N/A')}")
    print(f"✅ Total issues: {result['summary']['total_issues']}")
    
    print("\n📊 Issues breakdown:")
    print(f"   - Contradictions: {result['contradictions']['total_found']}")
    print(f"   - Undefined Terms: {result['undefined_terms']['total_found']}")
    print(f"   - Unsupported Claims: {result['unsupported_claims']['total_found']}")
    print(f"   - Logical Jumps: {result['logical_jumps']['total_found']}")
    
    return result


def test_vietnamese_language():
    """Test 2: Sử dụng tiếng Việt"""
    print("\n" + "="*80)
    print("TEST 2: VIETNAMESE LANGUAGE (language='vi')")
    print("="*80)
    
    context = {
        "writing_type": "Bài viết blog",
        "main_goal": "Chia sẻ kinh nghiệm lập trình",
        "criteria": ["rõ ràng", "thực tế"],
        "constraints": ["800-1200 từ"]
    }
    
    content = """
    Học lập trình không khó như bạn nghĩ!
    
    Tôi đã học được Python chỉ trong 2 tuần. Bạn chỉ cần luyện tập mỗi ngày.
    Neural networks rất quan trọng. Bạn nên học backpropagation ngay.
    
    Tuy nhiên, lập trình rất nguy hiểm và gây hại. Bạn nên tránh xa máy tính.
    
    Do đó, chúng ta cần cải cách giáo dục toàn cầu ngay lập tức.
    """
    
    print("🔍 Phân tích với prompt tiếng Việt (language='vi')...")
    result = analyze_document(context, content, language="vi")
    
    print(f"\n✅ Thành công: {result['success']}")
    print(f"✅ Ngôn ngữ sử dụng: {result['analysis_metadata'].get('language', 'N/A')}")
    print(f"✅ Tổng số vấn đề: {result['summary']['total_issues']}")
    
    print("\n📊 Chi tiết vấn đề:")
    print(f"   - Mâu thuẫn logic: {result['contradictions']['total_found']}")
    print(f"   - Thuật ngữ chưa định nghĩa: {result['undefined_terms']['total_found']}")
    print(f"   - Luận điểm thiếu chứng cứ: {result['unsupported_claims']['total_found']}")
    print(f"   - Nhảy logic: {result['logical_jumps']['total_found']}")
    
    return result


def test_default_language():
    """Test 3: Ngôn ngữ mặc định (không truyền tham số)"""
    print("\n" + "="*80)
    print("TEST 3: DEFAULT LANGUAGE (no language parameter)")
    print("="*80)
    
    context = {
        "writing_type": "Essay",
        "main_goal": "Discuss AI impact"
    }
    
    content = "AI is useful. However, AI is useless."
    
    print("🔍 Analyzing without language parameter (should default to 'en')...")
    result = analyze_document(context, content)  # No language parameter
    
    print(f"\n✅ Success: {result['success']}")
    print(f"✅ Language used: {result['analysis_metadata'].get('language', 'N/A')}")
    print(f"   Expected: 'en' (default)")
    
    assert result['analysis_metadata'].get('language') == 'en', "Default language should be 'en'"
    print("✅ Default language test PASSED!")
    
    return result


def test_invalid_language():
    """Test 4: Ngôn ngữ không hợp lệ"""
    print("\n" + "="*80)
    print("TEST 4: INVALID LANGUAGE (language='fr')")
    print("="*80)
    
    context = {
        "writing_type": "Article",
        "main_goal": "Test invalid language"
    }
    
    content = "Some content here."
    
    print("🔍 Trying invalid language 'fr'...")
    result = analyze_document(context, content, language="fr")
    
    print(f"\n❌ Success: {result['success']} (should be False)")
    print(f"❌ Error: {result['metadata']['error']}")
    
    assert result['success'] == False, "Should fail with invalid language"
    assert "Invalid language" in result['metadata']['error'], "Error message should mention invalid language"
    print("✅ Invalid language handling test PASSED!")
    
    return result


def test_language_comparison():
    """Test 5: So sánh kết quả giữa 2 ngôn ngữ"""
    print("\n" + "="*80)
    print("TEST 5: LANGUAGE COMPARISON (EN vs VI)")
    print("="*80)
    
    # Same content, different languages
    content = """
    AI will revolutionize education completely.
    Machine learning algorithms improve student performance.
    However, AI is harmful and should be banned from schools.
    
    Therefore, organic farming is the future.
    """
    
    context_en = {
        "writing_type": "Essay",
        "main_goal": "Discuss AI in education"
    }
    
    context_vi = {
        "writing_type": "Bài luận",
        "main_goal": "Thảo luận về AI trong giáo dục"
    }
    
    print("🔍 Analyzing with ENGLISH prompt...")
    result_en = analyze_document(context_en, content, language="en")
    
    print("\n🔍 Analyzing with VIETNAMESE prompt...")
    result_vi = analyze_document(context_vi, content, language="vi")
    
    print("\n📊 Comparison:")
    print(f"{'Metric':<30} {'English':>15} {'Vietnamese':>15}")
    print("-" * 62)
    print(f"{'Success':<30} {str(result_en['success']):>15} {str(result_vi['success']):>15}")
    print(f"{'Total Issues':<30} {result_en['summary']['total_issues']:>15} {result_vi['summary']['total_issues']:>15}")
    print(f"{'Contradictions':<30} {result_en['contradictions']['total_found']:>15} {result_vi['contradictions']['total_found']:>15}")
    print(f"{'Undefined Terms':<30} {result_en['undefined_terms']['total_found']:>15} {result_vi['undefined_terms']['total_found']:>15}")
    print(f"{'Unsupported Claims':<30} {result_en['unsupported_claims']['total_found']:>15} {result_vi['unsupported_claims']['total_found']:>15}")
    print(f"{'Logical Jumps':<30} {result_en['logical_jumps']['total_found']:>15} {result_vi['logical_jumps']['total_found']:>15}")
    print(f"{'Quality Score':<30} {result_en['summary']['document_quality_score']:>15} {result_vi['summary']['document_quality_score']:>15}")
    
    print("\n💡 Observation:")
    print("   Both languages should detect similar issues in the same content.")
    print("   Minor variations are acceptable due to LLM interpretation differences.")
    
    return result_en, result_vi


def demo_usage():
    """Demo: Cách sử dụng tính năng chuyển đổi ngôn ngữ"""
    print("\n" + "="*80)
    print("DEMO: USAGE EXAMPLES")
    print("="*80)
    
    print("\n📝 Example 1: Analyze English content with English prompt")
    print("-" * 80)
    print("""
from Analysis import analyze_document

context = {
    "writing_type": "Research Paper",
    "main_goal": "Present AI findings"
}
content = "Your English content..."

# Use English prompt
result = analyze_document(context, content, language="en")
    """)
    
    print("\n📝 Example 2: Analyze Vietnamese content with Vietnamese prompt")
    print("-" * 80)
    print("""
from Analysis import analyze_document

context = {
    "writing_type": "Bài nghiên cứu",
    "main_goal": "Trình bày kết quả về AI"
}
content = "Nội dung tiếng Việt của bạn..."

# Use Vietnamese prompt
result = analyze_document(context, content, language="vi")
    """)
    
    print("\n📝 Example 3: Default behavior (English)")
    print("-" * 80)
    print("""
# If you don't specify language, it defaults to English
result = analyze_document(context, content)  # language="en" by default
    """)
    
    print("\n💡 Tips:")
    print("   - Use language='en' for English content")
    print("   - Use language='vi' for Vietnamese content")
    print("   - Both output the same JSON structure")
    print("   - Vietnamese prompt better understands Vietnamese context")


def run_all_tests():
    """Chạy tất cả tests"""
    print("\n" + "🌐"*40)
    print(" LANGUAGE SWITCHING TEST SUITE ".center(80, "="))
    print("🌐"*40)
    
    tests = [
        ("English Language", test_english_language),
        ("Vietnamese Language", test_vietnamese_language),
        ("Default Language", test_default_language),
        ("Invalid Language", test_invalid_language),
        ("Language Comparison", test_language_comparison),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*80}")
            print(f"Running: {test_name}")
            print(f"{'='*80}")
            result = test_func()
            results.append((test_name, True, result))
            print(f"\n✅ {test_name} PASSED")
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"\n❌ {test_name} FAILED")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    # Demo usage
    demo_usage()
    
    # Final summary
    print("\n" + "="*80)
    print(" TEST SUMMARY ".center(80, "="))
    print("="*80)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, _ in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*80)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print("="*80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Language switching works perfectly!")
        print("🌐 You can now use both English and Vietnamese prompts!")
    
    return results


if __name__ == "__main__":
    print("\n🔬 Starting Language Switching Test Suite...")
    print("🌐 Testing analyze_document() with language parameter")
    print("   - language='en' → English prompt")
    print("   - language='vi' → Vietnamese prompt")
    
    results = run_all_tests()
    
    # Return exit code
    all_passed = all(success for _, success, _ in results)
    sys.exit(0 if all_passed else 1)
