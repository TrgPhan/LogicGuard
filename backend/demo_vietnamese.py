"""
Demo Script - Vietnamese Prompt Analysis
========================================
Script demo đơn giản để test prompt tiếng Việt
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'ai', 'models'))

from promptStore import prompt_analysis_vi


def demo_basic():
    """Demo 1: Ví dụ cơ bản"""
    print("\n" + "="*80)
    print("DEMO 1: VÍ DỤ CƠ BẢN - BÀI VIẾT BLOG")
    print("="*80)
    
    context = {
        "writing_type": "Bài viết blog",
        "main_goal": "Chia sẻ kinh nghiệm học lập trình",
        "criteria": ["dễ hiểu", "có ví dụ thực tế"],
        "constraints": ["800-1200 từ"]
    }
    
    content = """
    Học lập trình không khó như bạn nghĩ!
    
    Tôi đã học được Python chỉ trong 2 tuần và trở thành senior developer. 
    Bạn chỉ cần kiên trì và luyện tập mỗi ngày là sẽ thành công.
    
    Neural networks và deep learning là những kỹ thuật rất quan trọng. 
    Bạn nên học về backpropagation và gradient descent ngay từ đầu.
    
    Tuy nhiên, lập trình rất nguy hiểm và gây hại cho sức khỏe. 
    Bạn nên tránh xa máy tính và học một nghề khác.
    
    Do đó, chúng ta cần cải cách hệ thống giáo dục toàn cầu ngay lập tức.
    """
    
    print("📝 Nội dung văn bản:")
    print("-" * 80)
    print(content)
    print("-" * 80)
    
    prompt = prompt_analysis_vi(context, content)
    
    print(f"\n✅ Prompt đã được tạo!")
    print(f"   Độ dài: {len(prompt)} ký tự")
    print(f"   Số dòng: {len(prompt.split(chr(10)))}")
    
    print(f"\n🔍 Prompt này sẽ phát hiện:")
    print("   ✓ Mâu thuẫn: 'học lập trình dễ' vs 'lập trình nguy hiểm'")
    print("   ✓ Thuật ngữ chưa định nghĩa: neural networks, deep learning, backpropagation")
    print("   ✓ Luận điểm thiếu chứng cứ: 'học được Python trong 2 tuần', 'trở thành senior'")
    print("   ✓ Nhảy logic: từ lập trình → cải cách giáo dục toàn cầu")
    
    return prompt


def demo_academic():
    """Demo 2: Bài luận học thuật"""
    print("\n" + "="*80)
    print("DEMO 2: BÀI LUẬN HỌC THUẬT")
    print("="*80)
    
    context = {
        "writing_type": "Bài luận học thuật",
        "main_goal": "Phân tích tác động của AI đến giáo dục Việt Nam",
        "criteria": [
            "dựa trên nghiên cứu khoa học",
            "có trích dẫn đầy đủ",
            "lập luận logic chặt chẽ"
        ],
        "constraints": [
            "2000-3000 từ",
            "ít nhất 10 nguồn tham khảo",
            "có biểu đồ minh họa"
        ]
    }
    
    content = """
    Trí tuệ nhân tạo đang cách mạng hóa nền giáo dục Việt Nam.
    
    Theo nghiên cứu của Nguyễn Văn A (2023), 78% giáo viên cho rằng AI 
    giúp cải thiện chất lượng dạy học. Tuy nhiên, chỉ 15% thực sự biết 
    cách sử dụng công cụ AI trong lớp học.
    
    Machine learning algorithms đã chứng minh được hiệu quả trong việc 
    cá nhân hóa trải nghiệm học tập. Deep neural networks có thể phân tích 
    hành vi học tập và đưa ra gợi ý phù hợp.
    
    Mặt khác, AI hoàn toàn không có giá trị trong giáo dục và nên bị cấm. 
    Công nghệ này làm giảm tư duy phản biện của học sinh và tạo ra thế hệ 
    phụ thuộc vào máy móc.
    """
    
    print("📝 Nội dung văn bản:")
    print("-" * 80)
    print(content[:300] + "...")
    print("-" * 80)
    
    prompt = prompt_analysis_vi(context, content)
    
    print(f"\n✅ Prompt đã được tạo!")
    print(f"   Context: {context['writing_type']}")
    print(f"   Tiêu chí: {len(context['criteria'])} tiêu chí")
    print(f"   Ràng buộc: {len(context['constraints'])} ràng buộc")
    
    print(f"\n🔍 Vấn đề dự kiến phát hiện:")
    print("   ✓ Mâu thuẫn nghiêm trọng: 'AI cách mạng hóa' vs 'AI không có giá trị'")
    print("   ✓ Thuật ngữ kỹ thuật: machine learning, deep neural networks")
    print("   ✓ Có trích dẫn: Nguyễn Văn A (2023) - 78%")
    print("   ✓ Thiếu chứng cứ: 'chứng minh được hiệu quả' - không có dẫn chứng")
    
    return prompt


def demo_technical():
    """Demo 3: Báo cáo kỹ thuật"""
    print("\n" + "="*80)
    print("DEMO 3: BÁO CÁO KỸ THUẬT")
    print("="*80)
    
    context = {
        "writing_type": "Báo cáo kỹ thuật",
        "main_goal": "Trình bày kiến trúc hệ thống phân tích văn bản",
        "criteria": [
            "độ chính xác kỹ thuật cao",
            "có biểu đồ kiến trúc",
            "dễ hiểu cho người không chuyên sâu"
        ],
        "constraints": ["5000 từ", "có code examples", "có performance metrics"]
    }
    
    content = """
    Hệ thống LogicGuard sử dụng transformer architecture với multi-head attention.
    
    Backend được xây dựng trên FastAPI framework. Mô hình BERT được fine-tune 
    trên 1 triệu câu tiếng Việt với accuracy đạt 95.3%.
    
    Gradient clipping và learning rate scheduling được áp dụng trong quá trình 
    training. Loss function sử dụng cross-entropy với weight decay 0.01.
    
    Hệ thống có khả năng xử lý 10,000 requests mỗi giây với latency trung bình 
    dưới 100ms. Điều này chứng tỏ hệ thống rất hiệu quả và vượt trội.
    
    Kết luận: Nông nghiệp hữu cơ là tương lai của nhân loại.
    """
    
    print("📝 Nội dung văn bản:")
    print("-" * 80)
    print(content[:300] + "...")
    print("-" * 80)
    
    prompt = prompt_analysis_vi(context, content)
    
    print(f"\n✅ Prompt đã được tạo!")
    print(f"   Loại: Báo cáo kỹ thuật")
    print(f"   Yêu cầu: Độ chính xác cao + Dễ hiểu")
    
    print(f"\n🔍 Vấn đề dự kiến phát hiện:")
    print("   ✓ Nhiều thuật ngữ chưa định nghĩa:")
    print("     - transformer architecture")
    print("     - multi-head attention")
    print("     - gradient clipping")
    print("     - learning rate scheduling")
    print("   ✓ Có số liệu cụ thể: 95.3%, 10,000 requests, 100ms")
    print("   ✓ Nhảy logic NGHIÊM TRỌNG: từ hệ thống AI → nông nghiệp hữu cơ")
    
    return prompt


def demo_comparison():
    """Demo 4: So sánh với phiên bản tiếng Anh"""
    print("\n" + "="*80)
    print("DEMO 4: SO SÁNH TIẾNG VIỆT vs TIẾNG ANH")
    print("="*80)
    
    from promptStore import prompt_analysis  # English version
    
    # Same content, different language
    context_vi = {
        "writing_type": "Bài viết blog",
        "main_goal": "Chia sẻ kinh nghiệm",
    }
    
    context_en = {
        "writing_type": "Blog Post",
        "main_goal": "Share experience",
    }
    
    content = "AI is changing education. However, AI is useless."
    
    prompt_vi = prompt_analysis_vi(context_vi, content)
    prompt_en = prompt_analysis(context_en, content)
    
    print("📊 Thống kê so sánh:")
    print(f"   Tiếng Việt: {len(prompt_vi):,} ký tự")
    print(f"   Tiếng Anh:  {len(prompt_en):,} ký tự")
    print(f"   Chênh lệch: +{((len(prompt_vi)/len(prompt_en)-1)*100):.1f}%")
    
    print(f"\n🔍 Cấu trúc JSON output:")
    print("   ✅ Cả hai đều output JSON giống nhau")
    print("   ✅ Cả hai đều có 4 subtasks")
    print("   ✅ Tương thích hoàn toàn")
    
    print(f"\n💡 Khi nào dùng phiên bản nào?")
    print("   📝 Văn bản tiếng Việt → dùng prompt_analysis_vi()")
    print("   📝 Văn bản tiếng Anh → dùng prompt_analysis()")
    print("   📝 Văn bản song ngữ → dùng prompt_analysis() (tiếng Anh)")


def interactive_demo():
    """Demo tương tác - cho phép nhập văn bản"""
    print("\n" + "="*80)
    print("DEMO TƯƠNG TÁC - NHẬP VĂN BẢN CỦA BẠN")
    print("="*80)
    
    print("\n📝 Nhập loại văn bản (hoặc Enter để dùng mặc định 'Bài viết'):")
    writing_type = input(">>> ").strip() or "Bài viết"
    
    print("\n📝 Nhập văn bản cần phân tích (Enter 2 lần để kết thúc):")
    print(">>> ", end="")
    lines = []
    while True:
        line = input()
        if not line and lines:  # Empty line and we have content
            break
        lines.append(line)
    
    content = "\n".join(lines)
    
    if not content.strip():
        print("❌ Không có nội dung! Dùng ví dụ mặc định...")
        content = "AI rất hữu ích. Tuy nhiên, AI hoàn toàn vô dụng."
    
    context = {
        "writing_type": writing_type,
        "main_goal": "Phân tích văn bản",
    }
    
    prompt = prompt_analysis_vi(context, content)
    
    print(f"\n✅ Prompt đã được tạo thành công!")
    print(f"   Độ dài: {len(prompt):,} ký tự")
    print(f"   Loại văn bản: {writing_type}")
    
    print(f"\n📋 Prompt preview (300 ký tự đầu):")
    print("-" * 80)
    print(prompt[:300] + "...")
    print("-" * 80)
    
    return prompt


def main():
    """Main function - chạy tất cả demos"""
    print("\n" + "🇻🇳"*40)
    print(" VIETNAMESE PROMPT DEMO ".center(80, "="))
    print("🇻🇳"*40)
    
    print("\n📚 Các demo có sẵn:")
    print("   1. Demo cơ bản - Bài viết blog")
    print("   2. Bài luận học thuật")
    print("   3. Báo cáo kỹ thuật")
    print("   4. So sánh tiếng Việt vs Anh")
    print("   5. Demo tương tác (nhập văn bản)")
    print("   6. Chạy tất cả demos")
    
    choice = input("\n👉 Chọn demo (1-6) hoặc Enter để chạy tất cả: ").strip()
    
    if choice == "1":
        demo_basic()
    elif choice == "2":
        demo_academic()
    elif choice == "3":
        demo_technical()
    elif choice == "4":
        demo_comparison()
    elif choice == "5":
        interactive_demo()
    else:
        # Run all
        demo_basic()
        demo_academic()
        demo_technical()
        demo_comparison()
    
    print("\n" + "="*80)
    print("✅ DEMO HOÀN TẤT!")
    print("="*80)
    
    print("\n💡 Để sử dụng trong code của bạn:")
    print("""
    from promptStore import prompt_analysis_vi
    
    context = {
        "writing_type": "Bài viết blog",
        "main_goal": "Chia sẻ kinh nghiệm"
    }
    
    content = "Nội dung văn bản của bạn..."
    
    prompt = prompt_analysis_vi(context, content)
    
    # Gửi prompt đến Gemini/GPT
    # response = model.generate_content(prompt)
    """)
    
    print("\n📚 Xem thêm:")
    print("   - README_VIETNAMESE.md - Hướng dẫn chi tiết")
    print("   - COMPARISON_EN_VI.md - So sánh 2 phiên bản")
    print("   - test_vietnamese_prompt.py - Test suite đầy đủ")


if __name__ == "__main__":
    main()
