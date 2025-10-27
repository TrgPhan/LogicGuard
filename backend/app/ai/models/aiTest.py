from app.ai.models.contradictions import check_contradictions
import time


for i in range(2):
    start = time.time()
    text = "Minh luôn nói rằng anh chưa bao giờ rời khỏi Việt Nam. Anh kể rằng lần đầu đến Nhật Bản là vào năm 2019. Anh cho biết mình ghét sự ồn ào nên hiếm khi ra ngoài vào buổi tối. Tối nào Minh cũng đi uống cà phê cùng bạn bè để thư giãn. Minh bảo anh không thích công nghệ và chưa bao giờ dùng mạng xã hội. Tài khoản TikTok của anh có hơn 100 nghìn người theo dõi. Anh nói rằng mình ăn chay trường suốt 5 năm nay. Tuần trước anh đăng ảnh ăn thịt nướng trên Facebook. Minh khẳng định luôn dậy lúc 6 giờ sáng để tập thể dục. Hôm qua anh kể rằng thường ngủ đến tận 9 giờ mới dậy."
    result = check_contradictions(mode="finetuned", text=text)
    end = time.time()


    print("KẾT QUẢ")
    print(f"Thời gian: {end - start:.4f}")
    print(f"Success: {result['success']}")
    print(f"Mode: {result['mode']}")
    print(f"Model Path: {result['model_path']}")
    print(f"Total Sentences: {result['total_sentences']}")
    print(f"Total Contradictions: {result['total_contradictions']}")

    if result['sentences']:
        for idx, sentence in enumerate(result['sentences']):
            print(f"  [{idx}] {sentence}")

    if result['contradictions']:
        for c in result['contradictions']:
            print(f"[{c['id']}] Confidence: {c['confidence']:.2%}")
            print(f"    Câu {c['sentence1_index']}: {c['sentence1']}")
            print(f"    Câu {c['sentence2_index']}: {c['sentence2']}\n")
    else:
        print(f"\nKhông tìm thấy mâu thuẫn nào (threshold={result['metadata']['threshold']})")

    if result['metadata'].get('error'):
        print(f"\nError: {result['metadata']['error']}")

