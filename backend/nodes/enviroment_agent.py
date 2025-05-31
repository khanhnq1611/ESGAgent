# agents/environment_agent.py

import os
import json
from openai import OpenAI
from classes.state import ESGState
import requests
OPENROUTER_API_KEY = "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"

headers = {
  'Authorization': f'Bearer {OPENROUTER_API_KEY}',
  'Content-Type': 'application/json',
}


class EnvironmentAgent:
    """
    Agent sử dụng LLM (OpenAI GPT) để đánh giá tiêu chí Môi trường (E).
    System prompt chứa quy tắc chấm điểm E1, E2, E3.
    """

    def __init__(self, model: str = "gpt-4.1-nano"):
        # Check for API key during initialization
        # if "OPENAI_API_KEY" not in os.environ:
        #     raise RuntimeError("Bạn cần đặt biến môi trường OPENAI_API_KEY trước khi chạy.")
        
        # # Initialize OpenAI client
        # self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        # self.model = model

        # System prompt chứa đầy đủ quy tắc chấm điểm
        self.system_prompt = """
Bạn là một trợ lý AI chuyên đánh giá tiêu chí Môi trường (Environmental) cho một giao dịch tài chính.
Dưới đây là quy tắc chấm điểm minh họa tham khảo:

E1. Chứng chỉ & Tiêu chuẩn môi trường (tối đa 1.5 điểm)
- Nếu tổ chức nhận có các chứng chỉ sau, cộng điểm tương ứng:
  • 'LEED Platinum', 'Carbon Neutral', 'B-Corp Environmental' → +1.5 điểm  
  • 'LEED Gold', 'LEED Silver', 'ISO 14001', 'BREEAM'             → +1.0 điểm  
  • 'Energy Star', 'Green Building', 'chứng chỉ hữu cơ địa phương' → +0.5 điểm  

E2. Nội dung giao dịch thân thiện môi trường (tối đa 1.5 điểm)
- Nếu mô tả giao dịch chứa các từ khóa sau, cộng điểm tương ứng (lấy mức cao nhất):
  • Năng lượng sạch: 'năng lượng tái tạo', 'pin mặt trời', 'điện gió', 'biogas' → +1.5  
  • Giao thông xanh: 'xe điện', 'xe hybrid', 'vé tàu', 'xe buýt', 'xe đạp điện' → +1.0  
  • Sản phẩm xanh: 'organic', 'sinh học', 'tái chế', 'thân thiện môi trường'     → +0.75  
  • Dịch vụ xanh: 'làm sạch không hóa chất', 'in 3D tái chế', 'sửa chữa tái sử dụng' → +0.5  

E3. Phương thức giao dịch số hóa (tối đa 1.0 điểm)
- Nếu phương thức thanh toán thuộc nhóm sau, cộng điểm tương ứng:
  • Hoàn toàn số: 'QR', 'NFC', 'ví điện tử', 'blockchain'    → +1.0  
  • Chủ yếu số: 'mobile banking', 'e-invoice', 'hóa đơn điện tử' → +0.5
  • Một phần số: 'ATM', 'thẻ chip', 'SMS banking'          → +0.25  

Yêu cầu với LLM:
1. Dựa vào dữ liệu `transaction_description`, `payment_method` và `receiver_info['environmental_certificates']`, 
   hãy tính lần lượt E1, E2, E3 theo quy tắc trên.
2. Trả về kết quả ở định dạng JSON như sau:
   {
     "e1_score": float,
     "e2_score": float,
     "e3_score": float,
     "total_e_score": float,   # = e1_score + e2_score + e3_score, tối đa 4.0
     "breakdown": {
        "certificates": <e1_score>,
        "keywords": <e2_score>,
        "digital_payment": <e3_score>
     },
     "explaination_message_e": "..." # short desbcription of the scores in genenral and in vietnamese language
   }
3. KHÔNG trả lời bất kỳ văn bản nào ngoài JSON thuần. Nếu không tìm thấy chứng chỉ hoặc từ khóa, trả 0.0 cho mục đó.
"""

    def process(self, state: ESGState) -> ESGState:
        """
        Gửi request tới OpenAI ChatCompletion, parse kết quả JSON và lưu điểm vào state.
        """
        try:
            # Ensure errors key exists
            if "errors" not in state:
                state["errors"] = []

            # Chuẩn bị thông tin đầu vào cho LLM
            transaction_desc = state["transaction_data"].get("transaction_description", "")
            payment_method = state["transaction_data"].get("payment_method", "")
            certificates = state["receiver_info"].get("environmental_certificates", [])

            # Tạo message cho LLM: system + user
            
            # Update OpenAI API call to use new format
            response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json={
                'model': 'meta-llama/llama-3.3-70b-instruct:nitro',
                'messages': [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": json.dumps({
                        "transaction_description": transaction_desc,
                        "payment_method": payment_method,
                        "environmental_certificates": certificates
                    }, ensure_ascii=False)
                }
                ],
                "response_format": {
                    "type": "json_object",
                }
            })
            analysis_result = response.json()['choices'][0]['message']['content']

            # Chuyển chuỗi JSON thành dict Python
            try:
                result = json.loads(analysis_result)
            except json.JSONDecodeError as e:
                state["errors"].append(f"Parsing JSON error: {str(e)} | Raw response: {analysis_result}")
                # Nếu parsing lỗi, đặt điểm 0
                result = {
                    "e1_score": 0.0,
                    "e2_score": 0.0,
                    "e3_score": 0.0,
                    "total_e_score": 0.0,
                    "breakdown": {
                        "certificates": 0.0,
                        "keywords": 0.0,
                        "digital_payment": 0.0
                    },
                    "explaination_message_e": "Parsing error"
                }

            # Gán điểm vào state
            e1 = float(result.get("e1_score", 0.0))
            e2 = float(result.get("e2_score", 0.0))
            e3 = float(result.get("e3_score", 0.0))
            total_e = float(result.get("total_e_score", 0.0))

            state["environment_score"] = round(min(total_e, 4.0), 2)
            state["analysis_results"]["environment"] = {
                "certificates": round(e1, 2),
                "keywords": round(e2, 2),
                "digital_payment": round(e3, 2),
                "total": round(min(total_e, 4.0), 2),
                "explaination_message_e": result.get("explaination_message_e", "")
            }

            # print(f"🌱 [LLM] Environment Score: {state['environment_score']:.2f}")
            # print(f"🌱 Explanation for E: {state['analysis_results']['environment']['explaination_message_e']}")
            return state

        except Exception as e:
            # Ensure errors key exists before appending
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"EnvironmentAgent LLM error: {str(e)}")
            
            # Set default values
            state["environment_score"] = 0.0
            if "analysis_results" not in state:
                state["analysis_results"] = {}
            state["analysis_results"]["environment"] = {
                "certificates": 0.0,
                "keywords": 0.0,
                "digital_payment": 0.0,
                "total": 0.0,
                "explaination_message_e": "Lỗi xử lý"
            }
        
        return state
