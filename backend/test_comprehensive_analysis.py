"""
Test Comprehensive Analysis - Gộp 4 Subtasks
============================================
Test tất cả 4 subtasks trong một lần phân tích:
1. Contradictions
2. Undefined Terms
3. Unsupported Claims
4. Logical Jumps
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'ai', 'models'))

from Analysis import analyze_comprehensive, get_analysis_summary


def test_comprehensive_prompt_generation():
    """Test 1: Kiểm tra prompt generation"""
    print("\n" + "="*80)
    print("TEST 1: COMPREHENSIVE PROMPT GENERATION")
    print("="*80)
    
    from promptStore import prompt_analysis
    
    context = {
        "writing_type": "Academic Essay",
        "main_goal": "Argue thesis on climate change",
        "criteria": ["evidence-based", "logical"],
        "constraints": ["1500-2000 words"]
    }
    
    content = "Climate change is real. The Earth is getting warmer."
    
    prompt = prompt_comprehensive_analysis(context, content)
    
    print(f"✅ Generated prompt length: {len(prompt)} characters")
    print(f"✅ Contains 'SUBTASK 1': {('SUBTASK 1' in prompt or 'Subtask 1' in prompt)}")
    print(f"✅ Contains 'SUBTASK 2': {('SUBTASK 2' in prompt or 'Subtask 2' in prompt)}")
    print(f"✅ Contains 'SUBTASK 3': {('SUBTASK 3' in prompt or 'Subtask 3' in prompt)}")
    print(f"✅ Contains 'SUBTASK 4': {('SUBTASK 4' in prompt or 'Subtask 4' in prompt)}")
    print(f"✅ Contains 'contradictions': {'contradictions' in prompt.lower()}")
    print(f"✅ Contains 'undefined_terms': {'undefined_terms' in prompt.lower()}")
    print(f"✅ Contains 'unsupported_claims': {'unsupported_claims' in prompt.lower()}")
    print(f"✅ Contains 'logical_jumps': {'logical_jumps' in prompt.lower()}")
    
    print("\n📋 Prompt Preview (first 500 chars):")
    print("-" * 80)
    print(prompt[:500])
    print("...")
    print("-" * 80)
    
    return True


def test_input_validation():
    """Test 2: Kiểm tra validation"""
    print("\n" + "="*80)
    print("TEST 2: INPUT VALIDATION")
    print("="*80)
    
    # Test empty content
    result = analyze_document_comprehensive(
        context={"writing_type": "Test"},
        content=""
    )
    print(f"✅ Empty content rejected: {not result['success']}")
    print(f"   Error message: {result['metadata']['error']}")
    
    # Test invalid context
    result = analyze_document_comprehensive(
        context=None,
        content="Some content"
    )
    print(f"✅ Invalid context rejected: {not result['success']}")
    print(f"   Error message: {result['metadata']['error']}")
    
    return True


def test_api_integration():
    """Test 3: Kiểm tra integration với Gemini API"""
    print("\n" + "="*80)
    print("TEST 3: API INTEGRATION")
    print("="*80)
    
    context = {
        "writing_type": "Research Paper",
        "main_goal": "Present findings on AI and education",
        "criteria": ["scientific rigor", "clear evidence"],
        "constraints": ["3000 words", "peer-reviewed sources"]
    }
    
    # Complex test document với TẤT CẢ 4 loại issues
    content = """
    Introduction
    
    Artificial intelligence will revolutionize education completely. Machine learning algorithms 
    have been proven to increase student performance by 300%. This is the most important 
    technological advancement in human history.
    
    Background on Neural Networks
    
    Neural networks use backpropagation and gradient descent to learn patterns. The architecture 
    typically involves convolutional layers and recurrent units. Deep learning models require 
    GPU acceleration for training.
    
    Research Methods
    
    We collected data from 500 students over 2 years. The control group received traditional 
    instruction while the experimental group used AI tutoring. However, AI tutoring is harmful 
    to students and should be banned from all schools.
    
    Results and Discussion
    
    Our results show that AI tutoring improves test scores. The effect size was significant 
    (p < 0.05). Students reported higher satisfaction with AI-based learning.
    
    Future Implications
    
    Quantum computing will solve all remaining challenges. Within 5 years, human teachers 
    will become completely obsolete. Educational institutions must prepare for this inevitable 
    transformation by investing in superintelligent AI systems.
    
    Conclusion
    
    Therefore, climate change policies must be reformed immediately. The integration of 
    blockchain technology in supply chain management demonstrates the viability of our approach.
    """
    
    print("📄 Analyzing comprehensive test document...")
    result = analyze_document_comprehensive(context, content)
    
    print(f"\n✅ API call success: {result['success']}")
    print(f"✅ Has metadata: {'analysis_metadata' in result}")
    
    # Check all 4 subtasks
    print("\n📊 SUBTASK RESULTS:")
    print(f"  🔴 Contradictions: {result['contradictions']['total_found']} found")
    print(f"  📚 Undefined Terms: {result['undefined_terms']['total_found']} found")
    print(f"  ⚠️  Unsupported Claims: {result['unsupported_claims']['total_found']} found")
    print(f"  🔀 Logical Jumps: {result['logical_jumps']['total_found']} found")
    
    print(f"\n📈 SUMMARY:")
    print(f"  Total Issues: {result['summary']['total_issues']}")
    print(f"  Critical Issues: {result['summary']['critical_issues']}")
    print(f"  Quality Score: {result['summary']['document_quality_score']}/100")
    
    # Show some examples from each subtask
    if result['contradictions']['items']:
        print(f"\n🔴 Example Contradiction:")
        item = result['contradictions']['items'][0]
        print(f"   Sentence 1: {item.get('sentence1', 'N/A')[:80]}...")
        print(f"   Sentence 2: {item.get('sentence2', 'N/A')[:80]}...")
        print(f"   Type: {item.get('type', 'N/A')}")
    
    if result['undefined_terms']['items']:
        print(f"\n📚 Example Undefined Terms:")
        for term in result['undefined_terms']['items'][:3]:
            print(f"   - {term.get('term', 'N/A')}: {term.get('context', 'N/A')[:60]}...")
    
    if result['unsupported_claims']['items']:
        print(f"\n⚠️  Example Unsupported Claim:")
        item = result['unsupported_claims']['items'][0]
        print(f"   Claim: {item.get('claim', 'N/A')[:80]}...")
        print(f"   Severity: {item.get('severity', 'N/A')}")
    
    if result['logical_jumps']['items']:
        print(f"\n🔀 Example Logical Jump:")
        item = result['logical_jumps']['items'][0]
        print(f"   From: P{item.get('from_paragraph', '?')}: {item.get('from_topic', 'N/A')[:50]}...")
        print(f"   To: P{item.get('to_paragraph', '?')}: {item.get('to_topic', 'N/A')[:50]}...")
        print(f"   Coherence: {item.get('coherence_score', 0)}/10")
    
    # Show key recommendations
    if result['summary'].get('key_recommendations'):
        print(f"\n💡 KEY RECOMMENDATIONS:")
        for i, rec in enumerate(result['summary']['key_recommendations'][:3], 1):
            print(f"   {i}. {rec}")
    
    return result


def test_response_structure():
    """Test 4: Kiểm tra cấu trúc JSON response"""
    print("\n" + "="*80)
    print("TEST 4: RESPONSE STRUCTURE VALIDATION")
    print("="*80)
    
    context = {
        "writing_type": "Essay",
        "main_goal": "Argue about technology impact"
    }
    
    content = """
    Technology has changed our lives. Social media platforms have connected billions 
    of people worldwide. However, social media destroys human connections and isolates people.
    
    Artificial intelligence uses neural networks. Machine learning algorithms require 
    extensive training data. These systems will achieve artificial general intelligence 
    next year according to all experts.
    
    Therefore, we must invest in renewable energy immediately. The blockchain revolution 
    demonstrates that decentralized systems are superior.
    """
    
    result = analyze_document_comprehensive(context, content)
    
    # Validate required top-level keys
    required_keys = [
        "success", "content", "context", "analysis_metadata",
        "contradictions", "undefined_terms", "unsupported_claims",
        "logical_jumps", "summary", "metadata"
    ]
    
    print("✅ Checking required keys:")
    for key in required_keys:
        exists = key in result
        print(f"   - {key}: {'✓' if exists else '✗'}")
        if not exists:
            print(f"     WARNING: Missing required key '{key}'")
    
    # Validate contradictions structure
    if "contradictions" in result:
        contra = result["contradictions"]
        print(f"\n✅ Contradictions structure:")
        print(f"   - Has 'total_found': {'total_found' in contra}")
        print(f"   - Has 'items': {'items' in contra}")
        if "items" in contra and contra["items"]:
            item = contra["items"][0]
            print(f"   - Item has 'sentence1': {'sentence1' in item}")
            print(f"   - Item has 'sentence2': {'sentence2' in item}")
            print(f"   - Item has 'type': {'type' in item}")
    
    # Validate undefined_terms structure
    if "undefined_terms" in result:
        terms = result["undefined_terms"]
        print(f"\n✅ Undefined Terms structure:")
        print(f"   - Has 'total_found': {'total_found' in terms}")
        print(f"   - Has 'items': {'items' in terms}")
        if "items" in terms and terms["items"]:
            item = terms["items"][0]
            print(f"   - Item has 'term': {'term' in item}")
            print(f"   - Item has 'context': {'context' in item}")
    
    # Validate unsupported_claims structure
    if "unsupported_claims" in result:
        claims = result["unsupported_claims"]
        print(f"\n✅ Unsupported Claims structure:")
        print(f"   - Has 'total_found': {'total_found' in claims}")
        print(f"   - Has 'items': {'items' in claims}")
        if "items" in claims and claims["items"]:
            item = claims["items"][0]
            print(f"   - Item has 'claim': {'claim' in item}")
            print(f"   - Item has 'severity': {'severity' in item}")
    
    # Validate logical_jumps structure
    if "logical_jumps" in result:
        jumps = result["logical_jumps"]
        print(f"\n✅ Logical Jumps structure:")
        print(f"   - Has 'total_found': {'total_found' in jumps}")
        print(f"   - Has 'items': {'items' in jumps}")
        if "items" in jumps and jumps["items"]:
            item = jumps["items"][0]
            print(f"   - Item has 'from_paragraph': {'from_paragraph' in item}")
            print(f"   - Item has 'to_paragraph': {'to_paragraph' in item}")
            print(f"   - Item has 'coherence_score': {'coherence_score' in item}")
    
    # Validate summary structure
    if "summary" in result:
        summary = result["summary"]
        print(f"\n✅ Summary structure:")
        print(f"   - Has 'total_issues': {'total_issues' in summary}")
        print(f"   - Has 'critical_issues': {'critical_issues' in summary}")
        print(f"   - Has 'document_quality_score': {'document_quality_score' in summary}")
        print(f"   - Has 'key_recommendations': {'key_recommendations' in summary}")
    
    return result


def test_human_readable_summary():
    """Test 5: Kiểm tra summary generator"""
    print("\n" + "="*80)
    print("TEST 5: HUMAN-READABLE SUMMARY")
    print("="*80)
    
    context = {
        "writing_type": "Blog Post",
        "main_goal": "Discuss technology trends"
    }
    
    content = """
    Quantum computing will revolutionize everything. Qubits use superposition and 
    entanglement to perform calculations. These computers will be 1000x faster than 
    classical computers within 2 years.
    
    Machine learning algorithms have proven their value. Companies are investing 
    billions in AI research. However, AI poses an existential threat and should 
    be immediately banned worldwide.
    
    In conclusion, organic farming practices reduce pesticide use significantly.
    """
    
    result = analyze_document_comprehensive(context, content)
    
    if result['success']:
        summary_text = get_analysis_summary(result)
        print(summary_text)
        
        print("\n✅ Summary generated successfully")
        print(f"   Length: {len(summary_text)} characters")
        print(f"   Lines: {len(summary_text.split(chr(10)))}")
    else:
        print(f"❌ Analysis failed: {result['metadata']['error']}")
    
    return result


def run_all_tests():
    """Chạy tất cả các tests"""
    print("\n" + "🚀"*40)
    print(" COMPREHENSIVE ANALYSIS TEST SUITE - ALL 4 SUBTASKS ".center(80, "="))
    print("🚀"*40)
    
    tests = [
        ("Prompt Generation", test_comprehensive_prompt_generation),
        ("Input Validation", test_input_validation),
        ("API Integration", test_api_integration),
        ("Response Structure", test_response_structure),
        ("Human-Readable Summary", test_human_readable_summary)
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
    
    return results


if __name__ == "__main__":
    print("\n🔬 Starting Comprehensive Analysis Test Suite...")
    print("⚙️  Testing all 4 subtasks in unified analysis:")
    print("   1. Contradictions")
    print("   2. Undefined Terms")
    print("   3. Unsupported Claims")
    print("   4. Logical Jumps (NEW)")
    
    results = run_all_tests()
    
    # Return exit code
    all_passed = all(success for _, success, _ in results)
    sys.exit(0 if all_passed else 1)
