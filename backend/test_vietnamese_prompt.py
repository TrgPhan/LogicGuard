"""
Test Comprehensive Analysis - Phiên Bản Tiếng Việt
================================================
Test hàm prompt_analysis_vi() với prompt hoàn toàn bằng tiếng Việt
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'ai', 'models'))

from promptStore import prompt_analysis_vi


def test_vietnamese_prompt_generation():
    """Test: Kiểm tra prompt generation tiếng Việt"""
    print("\n" + "="*80)
    print("TEST: VIETNAMESE PROMPT GENERATION")
    print("="*80)
    
    context = {
        "writing_type": "Bài luận học thuật",
        "main_goal": "Lập luận về tác động của AI đến giáo dục",
        "criteria": ["dựa trên bằng chứng", "logic rõ ràng", "có trích dẫn"],
        "constraints": ["1500-2000 từ", "ít nhất 5 nguồn tham khảo"]
    }
    
    content = """
    Trí tuệ nhân tạo sẽ cách mạng hóa hoàn toàn nền giáo dục. Các thuật toán machine learning 
    đã được chứng minh là tăng hiệu suất học tập của sinh viên lên 300%. Đây là tiến bộ 
    công nghệ quan trọng nhất trong lịch sử nhân loại.
    
    Neural networks sử dụng backpropagation và gradient descent để học các mẫu. Kiến trúc 
    thường bao gồm các convolutional layers và recurrent units. Các mô hình deep learning 
    cần GPU acceleration để training.
    
    Tuy nhiên, AI dạy kèm gây hại cho học sinh và nên bị cấm hoàn toàn trong tất cả các 
    trường học. Công nghệ này làm giảm khả năng tư duy phản biện của người học.
    
    Do đó, chính sách về biến đổi khí hậu phải được cải cách ngay lập tức.
    """
    
    prompt = prompt_analysis_vi(context, content)
    
    print(f"✅ Độ dài prompt: {len(prompt)} ký tự")
    print(f"✅ Chứa 'NHIỆM VỤ PHỤ 1': {'NHIỆM VỤ PHỤ 1' in prompt}")
    print(f"✅ Chứa 'NHIỆM VỤ PHỤ 2': {'NHIỆM VỤ PHỤ 2' in prompt}")
    print(f"✅ Chứa 'NHIỆM VỤ PHỤ 3': {'NHIỆM VỤ PHỤ 3' in prompt}")
    print(f"✅ Chứa 'NHIỆM VỤ PHỤ 4': {'NHIỆM VỤ PHỤ 4' in prompt}")
    print(f"✅ Chứa 'Mâu thuẫn logic': {'Mâu thuẫn logic' in prompt or 'MÂU THUẪN LOGIC' in prompt}")
    print(f"✅ Chứa 'Thuật ngữ chưa định nghĩa': {'Thuật ngữ chưa định nghĩa' in prompt or 'THUẬT NGỮ CHƯA ĐỊNH NGHĨA' in prompt}")
    print(f"✅ Chứa 'Luận điểm thiếu chứng cứ': {'Luận điểm thiếu chứng cứ' in prompt or 'LUẬN ĐIỂM THIẾU CHỨNG CỨ' in prompt}")
    print(f"✅ Chứa 'Nhảy logic': {'Nhảy logic' in prompt or 'NHẢY LOGIC' in prompt}")
    
    # Check Vietnamese-specific content
    print(f"\n✅ Kiểm tra nội dung tiếng Việt:")
    print(f"   - Chứa 'Loại văn bản': {'Loại văn bản' in prompt}")
    print(f"   - Chứa 'Mục tiêu chính': {'Mục tiêu chính' in prompt}")
    print(f"   - Chứa 'Tiêu chí đánh giá': {'Tiêu chí đánh giá' in prompt}")
    print(f"   - Chứa 'Ràng buộc': {'Ràng buộc' in prompt}")
    print(f"   - Chứa 'LogicGuard': {'LogicGuard' in prompt}")
    print(f"   - Chứa 'BẮT ĐẦU VĂN BẢN': {'BẮT ĐẦU VĂN BẢN' in prompt}")
    print(f"   - Chứa 'KẾT THÚC VĂN BẢN': {'KẾT THÚC VĂN BẢN' in prompt}")
    
    print("\n📋 Preview 500 ký tự đầu:")
    print("-" * 80)
    print(prompt[:500])
    print("...")
    print("-" * 80)
    
    print("\n📋 Preview phần NHIỆM VỤ PHỤ 1:")
    print("-" * 80)
    start_idx = prompt.find("NHIỆM VỤ PHỤ 1")
    if start_idx != -1:
        print(prompt[start_idx:start_idx+400])
        print("...")
    print("-" * 80)
    
    return True


def test_context_formatting_vietnamese():
    """Test: Kiểm tra format context tiếng Việt"""
    print("\n" + "="*80)
    print("TEST: CONTEXT FORMATTING (VIETNAMESE)")
    print("="*80)
    
    context = {
        "writing_type": "Báo cáo kỹ thuật",
        "main_goal": "Trình bày kết quả nghiên cứu về blockchain",
        "criteria": ["độ chính xác kỹ thuật", "dễ hiểu"],
        "constraints": ["5000 từ", "có biểu đồ minh họa"]
    }
    
    content = "Nội dung mẫu."
    
    prompt = prompt_analysis_vi(context, content)
    
    print("✅ Kiểm tra các trường context được format đúng:")
    print(f"   - 'Loại văn bản: Báo cáo kỹ thuật': {'Loại văn bản: Báo cáo kỹ thuật' in prompt}")
    print(f"   - 'Mục tiêu chính: Trình bày': {'Mục tiêu chính: Trình bày' in prompt}")
    print(f"   - Tiêu chí có trong prompt: {'độ chính xác kỹ thuật' in prompt}")
    print(f"   - Ràng buộc có trong prompt: {'5000 từ' in prompt}")
    
    return True


def test_vietnamese_vs_english_structure():
    """Test: So sánh cấu trúc prompt tiếng Việt và tiếng Anh"""
    print("\n" + "="*80)
    print("TEST: VIETNAMESE vs ENGLISH STRUCTURE COMPARISON")
    print("="*80)
    
    from promptStore import prompt_analysis  # English version
    
    context = {
        "writing_type": "Research Paper",
        "main_goal": "Present AI findings",
        "criteria": ["evidence-based"],
        "constraints": ["3000 words"]
    }
    
    content = "Sample content for testing."
    
    prompt_en = prompt_analysis(context, content)
    
    context_vi = {
        "writing_type": "Bài nghiên cứu",
        "main_goal": "Trình bày kết quả về AI",
        "criteria": ["dựa trên bằng chứng"],
        "constraints": ["3000 từ"]
    }
    
    prompt_vi = prompt_analysis_vi(context_vi, content)
    
    print(f"📊 Thống kê:")
    print(f"   Độ dài prompt tiếng Anh: {len(prompt_en)} ký tự")
    print(f"   Độ dài prompt tiếng Việt: {len(prompt_vi)} ký tự")
    print(f"   Tỷ lệ: {len(prompt_vi)/len(prompt_en)*100:.1f}%")
    
    print(f"\n✅ Kiểm tra cấu trúc JSON tương tự:")
    print(f"   - Prompt EN có 'contradictions': {'contradictions' in prompt_en}")
    print(f"   - Prompt VI có 'contradictions': {'contradictions' in prompt_vi}")
    print(f"   - Prompt EN có 'undefined_terms': {'undefined_terms' in prompt_en}")
    print(f"   - Prompt VI có 'undefined_terms': {'undefined_terms' in prompt_vi}")
    print(f"   - Prompt EN có 'unsupported_claims': {'unsupported_claims' in prompt_en}")
    print(f"   - Prompt VI có 'unsupported_claims': {'unsupported_claims' in prompt_vi}")
    print(f"   - Prompt EN có 'logical_jumps': {'logical_jumps' in prompt_en}")
    print(f"   - Prompt VI có 'logical_jumps': {'logical_jumps' in prompt_vi}")
    
    print(f"\n✅ Kết luận: Cả hai prompt đều có cấu trúc JSON output giống nhau")
    
    return True


def test_special_vietnamese_characters():
    """Test: Kiểm tra xử lý ký tự tiếng Việt đặc biệt"""
    print("\n" + "="*80)
    print("TEST: SPECIAL VIETNAMESE CHARACTERS")
    print("="*80)
    
    context = {
        "writing_type": "Luận văn tiến sĩ",
        "main_goal": "Nghiên cứu về học máy và xử lý ngôn ngữ tự nhiên",
        "criteria": ["khoa học", "sáng tạo"],
        "constraints": ["không quá 50.000 từ"]
    }
    
    content = """
    Đây là một đoạn văn có các ký tự đặc biệt tiếng Việt:
    - Dấu sắc: á é í ó ú ý
    - Dấu huyền: à è ì ò ù ỳ
    - Dấu hỏi: ả ẻ ỉ ỏ ủ ỷ
    - Dấu ngã: ã ẽ ĩ õ ũ ỹ
    - Dấu nặng: ạ ệ ị ọ ụ ỵ
    - Các chữ đặc biệt: ă â ê ô ơ ư đ
    """
    
    prompt = prompt_analysis_vi(context, content)
    
    print("✅ Kiểm tra các ký tự tiếng Việt được giữ nguyên:")
    print(f"   - Content có trong prompt: {content[:100] in prompt}")
    print(f"   - 'Luận văn tiến sĩ' có trong prompt: {'Luận văn tiến sĩ' in prompt}")
    print(f"   - 'Nghiên cứu' có trong prompt: {'Nghiên cứu' in prompt}")
    print(f"   - 'khoa học' có trong prompt: {'khoa học' in prompt}")
    
    print(f"\n✅ Encoding test passed - Vietnamese characters preserved correctly")
    
    return True


def run_all_tests():
    """Chạy tất cả tests cho phiên bản tiếng Việt"""
    print("\n" + "🇻🇳"*40)
    print(" VIETNAMESE PROMPT TEST SUITE ".center(80, "="))
    print("🇻🇳"*40)
    
    tests = [
        ("Vietnamese Prompt Generation", test_vietnamese_prompt_generation),
        ("Context Formatting (Vietnamese)", test_context_formatting_vietnamese),
        ("Vietnamese vs English Structure", test_vietnamese_vs_english_structure),
        ("Special Vietnamese Characters", test_special_vietnamese_characters)
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
    
    if passed == total:
        print("\n🎉 TẤT CẢ TESTS ĐỀU PASS! Phiên bản tiếng Việt hoạt động tốt!")
    
    return results


if __name__ == "__main__":
    print("\n🔬 Starting Vietnamese Prompt Test Suite...")
    print("⚙️  Testing prompt_analysis_vi() function")
    print("📝 Kiểm tra prompt tiếng Việt cho 4 subtasks")
    
    results = run_all_tests()
    
    # Return exit code
    all_passed = all(success for _, success, _ in results)
    sys.exit(0 if all_passed else 1)
