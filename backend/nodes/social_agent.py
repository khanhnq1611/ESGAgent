# agents/social_agent.py

import os
import json
from openai import OpenAI
import asyncio
from typing import Any, Dict

from classes.state import ESGState
import requests
OPENROUTER_API_KEY = ""

headers = {
  'Authorization': f'Bearer {OPENROUTER_API_KEY}',
  'Content-Type': 'application/json',
}


class SocialAgent:
    """
    Agent sử dụng LLM (OpenAI GPT) để đánh giá tiêu chí Xã hội (Social).
    System prompt chứa quy tắc chấm điểm S1, S2.
    """

    def __init__(self, model: str = "gpt-4.1-nano"):


        # System prompt chứa đầy đủ quy tắc chấm điểm S1, S2
        self.system_prompt = """
    Bạn là một trợ lý AI chuyên đánh giá tiêu chí Xã hội (Social) cho một giao dịch tài chính.
    Dưới đây là quy tắc chấm điểm minh họa tham khảo:

    S1. Loại hình tổ chức/doanh nghiệp (tối đa 2.0 điểm)
    - Nếu tổ chức nhận thuộc các loại sau, cộng điểm tương ứng:
      • Phi lợi nhuận: Tổ chức từ thiện, quỹ cứu trợ, hội chữ thập đỏ → +2.5 
      • Giáo dục - Y tế: Trường học, bệnh viện, phòng khám, trung tâm nghiên cứu → +1.5  
      • Doanh nghiệp xã hội: Hợp tác xã, doanh nghiệp có trách nhiệm xã hội cao → +1.0  
      • SME địa phương: Cửa hàng gia đình, thương hiệu địa phương nhỏ → +0.5  

    S2. Mục đích chuyển khoản (tối đa 1.5 điểm)
    - Nếu mô tả giao dịch chứa các từ khóa sau, cộng điểm tương ứng (lấy mức cao nhất):
      • Cứu trợ khẩn cấp: 'thiên tai', 'lũ lụt', 'động đất', 'cứu trợ' → +1.5  
      • Từ thiện: 'ủng hộ', 'từ thiện', 'quyên góp', 'giúp đỡ' → +1.0  
      • Giáo dục: 'học phí', 'học bổng', 'sách vở', 'đào tạo' → +0.75  
      • Y tế: 'chữa bệnh', 'phẫu thuật', 'thuốc men', 'khám chữa bệnh' → +0.75  
      • Hỗ trợ cộng đồng: 'người già', 'trẻ em', 'người khuyết tật', 'cộng đồng' → +0.5  

    S3. Tác động xã hội rộng (tối đa 0.5 điểm)
    - Nếu mô tả giao dịch thể hiện tác động sau, cộng điểm tương ứng:
      • Tạo việc làm: Thanh toán lương cho lao động địa phương, freelancer → +0.25
      • Hỗ trợ MSME: Giao dịch với doanh nghiệp siêu nhỏ, hộ kinh doanh → +0.25

    Yêu cầu với LLM:
    1. Dựa vào:
       - `receiver_info["business_type"]`
       - `transaction_data["transaction_description"]`
       - (Nếu cần) `receiver_info["company_size"]` hoặc thông tin KYC/AM‌L (nếu muốn mở rộng)
        
       Hãy tính điểm S1 và S2 theo quy tắc ở trên.
    2. Trả về kết quả ở định dạng JSON (chỉ có JSON thuần, không có bất kỳ phần text giải thích nào) như sau:
       {
         "s1_score": float,
         "s2_score": float,
         "total_s_score": float,   # = s1_score + s2_score, tối đa 4.0
         "breakdown": {
         "organization_type": <s1_score>,
         "purpose": <s2_score>,
         "explaination_message_s": "..."  short desbcription of the scores in genenral and in vietnamese language
    3. Nếu không tìm thấy tổ chức thuộc S1 hoặc từ khóa S2, trả 0.0 cho mục đó.
    4. Giới hạn `total_s_score` ở mức tối đa 4.0 
    LƯU Ý:
    - Chỉ trả JSON, KHÔNG trả thêm text thuyết minh.
    - Kết quả JSON phải parseable hoàn toàn.
    """

    def process(self, state: ESGState) -> ESGState:
        """
        Gửi request tới OpenAI ChatCompletion, parse kết quả JSON và lưu điểm vào state.
        """
        try:
            # Lấy thông tin cần thiết để gửi cho LLM
            business_type = state["receiver_info"].get("business_type", "")
            description = state["transaction_data"].get("transaction_description", "")

            # Tạo message cho LLM: system + user
            input_payload = {
                "business_type": business_type,
                "transaction_description": description
            }

            response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json={
                'model': 'meta-llama/llama-3.3-70b-instruct:nitro',
                'messages': [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(input_payload, ensure_ascii=False)
                }
                ],
                "response_format": {
                    "type": "json_object",
                }
            })
           
            content = response.json()['choices'][0]['message']['content']

            # Chuyển chuỗi JSON thành dict Python
            try:
                result = json.loads(content)
            except json.JSONDecodeError as e:
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append(f"Parsing JSON error (SocialAgent): {str(e)} | Raw response: {content}")
                # Nếu parsing lỗi, đặt điểm 0
                result = {
                    "s1_score": 0.0,
                    "s2_score": 0.0,
                    "total_s_score": 0.0,
                    "breakdown": {
                        "organization_type": 0.0,
                        "purpose": 0.0,
                        "explaination_message_s": "Không thể parse kết quả từ LLM."
                    }
                }

            # Gán điểm vào state
            s1 = float(result.get("s1_score", 0.0))
            s2 = float(result.get("s2_score", 0.0))
            total_s = float(result.get("total_s_score", 0.0))

            # Giới hạn tổng điểm (nếu bạn muốn giới hạn ở 4.0 hoặc 3.5)
            capped_total = round(min(total_s, 4.0), 2)

            # Extract explanation from breakdown or direct field
            explanation = result.get("breakdown", {}).get("explaination_message_s", 
                                   result.get("explaination_message_s", "Không có giải thích"))

            state["social_score"] = capped_total
            state["analysis_results"]["social"] = {
                "organization_type": round(s1, 2),
                "purpose": round(s2, 2),
                "total": capped_total,
                "explaination_message_s": explanation
            }

            # print(f"👥 [LLM] Social Score: {state['social_score']:.2f}")
            # print(f"👥 [LLM] Explanation s: {explanation}")
            return state

        except Exception as e:
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"SocialAgent LLM error: {str(e)}")
            
            # Set default values
            state["social_score"] = 0.0
            if "analysis_results" not in state:
                state["analysis_results"] = {}
            state["analysis_results"]["social"] = {
                "organization_type": 0.0,
                "purpose": 0.0,
                "total": 0.0,
                "explaination_message_s": "Lỗi xử lý"
            }
            return state
