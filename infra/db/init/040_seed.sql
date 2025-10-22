-- WRITING_TYPE mặc định với templates (khớp với ERROR_CATEGORY và ERROR_TYPE)
INSERT INTO "WRITING_TYPE" (id, name, display_name, description, default_checks, structure_template)
VALUES
  -- Essay
  (
    gen_random_uuid(), 
    'essay', 
    'Essay', 
    'Bài luận học thuật hoặc phân tích',
    '{
      "clarity": ["unclear_term", "undefined_technical_term", "ambiguous_reference", "vague_language"],
      "logic": ["contradiction", "unsupported_claim", "logic_gap"],
      "structure": ["off_topic"],
      "goal_alignment": ["missing_rubric_element", "weak_evidence"]
    }'::jsonb,
    '{
      "sections": [
        {"type": "intro", "label": "Introduction", "required": true, "guidelines": "Giới thiệu chủ đề, nêu thesis statement rõ ràng"},
        {"type": "body", "label": "Body Paragraphs", "required": true, "guidelines": "Triển khai luận điểm với dẫn chứng cụ thể"},
        {"type": "conclusion", "label": "Conclusion", "required": true, "guidelines": "Tóm tắt và kết luận mạch lạc"}
      ],
      "suggested_criteria": [
        {"label": "Thesis statement rõ ràng", "weight": 1.0, "mandatory": true, "description": "Có thesis statement được nêu rõ ràng"},
        {"label": "Luận điểm có dẫn chứng", "weight": 0.9, "mandatory": true, "description": "Mỗi luận điểm đều có dẫn chứng hỗ trợ"},
        {"label": "Kết luận mạch lạc", "weight": 0.7, "mandatory": false, "description": "Kết luận tóm tắt đầy đủ các luận điểm"},
        {"label": "Thuật ngữ được định nghĩa", "weight": 0.6, "mandatory": false, "description": "Thuật ngữ chuyên môn được giải thích rõ ràng"}
      ]
    }'::jsonb
  ),
  
  -- Technical Proposal
  (
    gen_random_uuid(), 
    'proposal', 
    'Proposal', 
    'Đề xuất kỹ thuật hoặc dự án',
    '{
      "clarity": ["unclear_term", "undefined_technical_term", "ambiguous_reference", "vague_language"],
      "logic": ["contradiction", "unsupported_claim", "logic_gap"],
      "structure": ["off_topic"],
      "goal_alignment": ["missing_rubric_element", "weak_evidence"]
    }'::jsonb,
    '{
      "sections": [
        {"type": "intro", "label": "Executive Summary", "required": true, "guidelines": "Tóm tắt đề xuất một cách súc tích"},
        {"type": "body", "label": "Problem Statement", "required": true, "guidelines": "Mô tả vấn đề cần giải quyết rõ ràng"},
        {"type": "body", "label": "Proposed Solution", "required": true, "guidelines": "Giải pháp đề xuất chi tiết với luận cứ kỹ thuật"},
        {"type": "body", "label": "Implementation Plan", "required": true, "guidelines": "Kế hoạch triển khai với timeline cụ thể"},
        {"type": "conclusion", "label": "Conclusion & Next Steps", "required": true, "guidelines": "Tổng kết và các bước tiếp theo"}
      ],
      "suggested_criteria": [
        {"label": "Vấn đề được định nghĩa rõ ràng", "weight": 1.0, "mandatory": true, "description": "Problem statement cụ thể và đo lường được"},
        {"label": "Giải pháp khả thi về kỹ thuật", "weight": 1.0, "mandatory": true, "description": "Technical feasibility được chứng minh"},
        {"label": "Có đề cập scalability", "weight": 0.8, "mandatory": true, "description": "Khả năng mở rộng được xem xét"},
        {"label": "Có phân tích chi phí", "weight": 0.7, "mandatory": false, "description": "Cost analysis được đề cập"},
        {"label": "Timeline thực tế", "weight": 0.6, "mandatory": false, "description": "Kế hoạch thời gian hợp lý"}
      ]
    }'::jsonb
  ),
  
  -- Report
  (
    gen_random_uuid(), 
    'report', 
    'Report', 
    'Báo cáo phân tích hoặc nghiên cứu',
    '{
      "clarity": ["unclear_term", "undefined_technical_term", "ambiguous_reference", "vague_language"],
      "logic": ["contradiction", "unsupported_claim", "logic_gap"],
      "structure": ["off_topic"],
      "goal_alignment": ["missing_rubric_element", "weak_evidence"]
    }'::jsonb,
    '{
      "sections": [
        {"type": "intro", "label": "Executive Summary", "required": true, "guidelines": "Tóm tắt các phát hiện chính"},
        {"type": "body", "label": "Methodology", "required": false, "guidelines": "Phương pháp nghiên cứu và thu thập dữ liệu"},
        {"type": "body", "label": "Findings", "required": true, "guidelines": "Kết quả và phát hiện với dữ liệu cụ thể"},
        {"type": "body", "label": "Analysis", "required": true, "guidelines": "Phân tích dữ liệu có độ sâu"},
        {"type": "conclusion", "label": "Recommendations", "required": true, "guidelines": "Khuyến nghị dựa trên phân tích"}
      ],
      "suggested_criteria": [
        {"label": "Dữ liệu chính xác", "weight": 1.0, "mandatory": true, "description": "Dữ liệu được trích dẫn và xác minh"},
        {"label": "Phân tích có độ sâu", "weight": 0.9, "mandatory": true, "description": "Phân tích đi sâu vào insight"},
        {"label": "Kết luận có dẫn chứng", "weight": 0.8, "mandatory": true, "description": "Mỗi kết luận đều có data hỗ trợ"},
        {"label": "Có biểu đồ minh họa", "weight": 0.5, "mandatory": false, "description": "Data visualization phù hợp"}
      ]
    }'::jsonb
  ),
  
  -- Pitch
  (
    gen_random_uuid(), 
    'pitch', 
    'Pitch', 
    'Bài thuyết trình bán hàng hoặc gọi vốn',
    '{
      "clarity": ["unclear_term", "undefined_technical_term", "ambiguous_reference", "vague_language"],
      "logic": ["contradiction", "unsupported_claim", "logic_gap"],
      "structure": ["off_topic"],
      "goal_alignment": ["missing_rubric_element", "weak_evidence"]
    }'::jsonb,
    '{
      "sections": [
        {"type": "intro", "label": "Hook", "required": true, "guidelines": "Câu mở đầu thu hút và gây tò mò"},
        {"type": "body", "label": "Problem", "required": true, "guidelines": "Vấn đề thị trường rõ ràng"},
        {"type": "body", "label": "Solution", "required": true, "guidelines": "Giải pháp độc đáo của bạn"},
        {"type": "body", "label": "Market Opportunity", "required": true, "guidelines": "Quy mô thị trường và cơ hội"},
        {"type": "body", "label": "Competitive Advantage", "required": true, "guidelines": "Điểm khác biệt so với đối thủ"},
        {"type": "conclusion", "label": "Call to Action", "required": true, "guidelines": "Kêu gọi hành động rõ ràng"}
      ],
      "suggested_criteria": [
        {"label": "Value proposition rõ ràng", "weight": 1.0, "mandatory": true, "description": "Giá trị cốt lõi được truyền tải rõ"},
        {"label": "Có dữ liệu thị trường", "weight": 0.9, "mandatory": true, "description": "Market size và opportunity có số liệu"},
        {"label": "Điểm khác biệt cạnh tranh", "weight": 0.8, "mandatory": true, "description": "Competitive advantage được làm rõ"},
        {"label": "Câu chuyện hấp dẫn", "weight": 0.7, "mandatory": false, "description": "Narrative compelling và memorable"}
      ]
    }'::jsonb
  ),
  
  -- Blog Post
  (
    gen_random_uuid(), 
    'blog_post', 
    'Blog Post', 
    'Bài viết blog hoặc content marketing',
    '{
      "clarity": ["unclear_term", "vague_language"],
      "logic": ["unsupported_claim", "logic_gap"],
      "structure": ["off_topic"],
      "goal_alignment": ["missing_rubric_element"]
    }'::jsonb,
    '{
      "sections": [
        {"type": "intro", "label": "Introduction", "required": true, "guidelines": "Hook hấp dẫn, giới thiệu chủ đề"},
        {"type": "body", "label": "Main Content", "required": true, "guidelines": "Nội dung chính với ví dụ cụ thể"},
        {"type": "conclusion", "label": "Conclusion & CTA", "required": true, "guidelines": "Tóm tắt key takeaways và call-to-action"}
      ],
      "suggested_criteria": [
        {"label": "Tiêu đề hấp dẫn", "weight": 0.8, "mandatory": true, "description": "Title thu hút click"},
        {"label": "Nội dung dễ đọc", "weight": 0.9, "mandatory": true, "description": "Câu ngắn gọn, đoạn văn súc tích"},
        {"label": "Có ví dụ thực tế", "weight": 0.7, "mandatory": false, "description": "Examples và case studies cụ thể"},
        {"label": "Có CTA rõ ràng", "weight": 0.6, "mandatory": false, "description": "Call-to-action được đặt hợp lý"},
        {"label": "Giá trị cho reader", "weight": 0.8, "mandatory": true, "description": "Actionable insights cho độc giả"}
      ]
    }'::jsonb
  )
ON CONFLICT DO NOTHING;

-- USER test
-- Email: demo@logicguard.ai
-- Password: demo123
INSERT INTO "USER"(id, email, password_hash)
VALUES (gen_random_uuid(), 'demo@logicguard.ai', '$2b$12$kYjh7jy8XJeR9R/L3gfoA.xt2Bv8doVDOVx9heAy1DYJZR5TDXAem')
ON CONFLICT DO NOTHING;