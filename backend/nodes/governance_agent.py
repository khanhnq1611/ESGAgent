import os
import json
from openai import OpenAI
from classes.state import ESGState
import requests
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

headers = {
  'Authorization': f'Bearer {OPENROUTER_API_KEY}',
  'Content-Type': 'application/json',
}

class GovernanceAgent:
    """Analyzes the governance aspects of ESG transactions"""

    def __init__(self, model: str = "gpt-4.1-nano"):
        # Check for API key during initialization


        # System prompt chứa quy tắc chấm điểm G1, G2
        self.system_prompt = """
Bạn là một trợ lý AI chuyên đánh giá tiêu chí Quản trị (Governance) cho một giao dịch tài chính.
Dưới đây là quy tắc chấm điểm minh họa tham khảo:

G1. Độ tin cậy và minh bạch (tối đa 1.0 điểm)
- Nếu trang thái KYC thuộc nhóm sau, cộng điểm tương ứng:
  • Cao: KYC đầy đủ + eKYC + sinh trắc học → +1.0
  • Trung bình: KYC cơ bản + OTP + xác thực 2 lớp → +0.75
  • Cơ bản: Chỉ có thông tin tài khoản cơ bản → +0.25
  • Nếu không có thông tin rõ ràng, hoặc thiếu dữ liệu → +0.0

G2. Tuân thủ pháp luật và quy định (tối đa 1.0 điểm)
- Dựa vào thông tin pháp lý của tổ chức nhận (receiver_info):
  • Tuân thủ cao: Có giấy phép kinh doanh, đăng ký thuế, báo cáo minh bạch → +1.0
  • Tuân thủ cơ bản: Có thông tin pháp lý cơ bản, không vi phạm → +0.5
  • Có nghi vấn: Thiếu thông tin, có dấu hiệu bất thường → +0.0

Yêu cầu với LLM:
1. Dựa vào các trường:
   - `sender_info["kyc_status"]`
   - `receiver_info["kyc_status"]`
   - `receiver_info["business_license"]`
   - `receiver_info["tax_code"]`
   - (Nếu có) `transaction_data["aml_flag"]` để bổ trợ đánh giá.
2. Tính điểm G1 và G2 theo quy tắc ở trên.
3. Trả về kết quả ở định dạng JSON (chỉ có JSON thuần, không kèm bất kỳ văn bản nào khác) như sau:
   {
     "g1_score": float,
     "g2_score": float,
     "total_g_score": float,   # = g1_score + g2_score, tối đa 2.0
     "breakdown": {
        "kyc_reliability": <g1_score>,
        "legal_compliance": <g2_score>
     },
     "explanation_message_g": "..." # short desbcription of the scores in genenral and in vietnamese language
   }
4. Nếu không tìm thấy dữ liệu phù hợp, cho điểm 0.0 cho mục đó.
5. Giới hạn `total_g_score` tối đa là 2.0.

LƯU Ý:
- Chỉ trả JSON, KHÔNG trả thêm phần text nao khac.
- Kết quả JSON phải dễ dàng parse bằng json.loads.
"""

    def process(self, state: ESGState) -> ESGState:  # Remove async
        """
        Gửi request tới OpenAI ChatCompletion, parse kết quả JSON và lưu điểm vào state.
        """
        try:
            # Ensure errors key exists
            if "errors" not in state:
                state["errors"] = []

            # Trích xuất dữ liệu cần thiết từ state
            sender_kyc = state["sender_info"].get("kyc_status", "")
            receiver_kyc = state["receiver_info"].get("kyc_status", "")
            business_license = state["receiver_info"].get("business_license", "")
            tax_code = state["receiver_info"].get("tax_code", "")
            aml_flag = state["transaction_data"].get("aml_flag", "")

            # Tạo payload JSON cho LLM
            input_payload = {
                "sender_kyc": sender_kyc,
                "receiver_kyc": receiver_kyc,
                "business_license": business_license,
                "tax_code": tax_code,
                "aml_flag": aml_flag
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

            # Add proper response validation
            if response.status_code != 200:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")
            
            response_data = response.json()
            
            # Check if response has the expected structure
            if 'choices' not in response_data:
                raise Exception(f"Invalid API response structure: {response_data}")
            
            if not response_data['choices'] or 'message' not in response_data['choices'][0]:
                raise Exception(f"Invalid choices structure: {response_data}")
            
            content = response_data['choices'][0]['message']['content']

            # Chuyển chuỗi JSON từ LLM thành dict Python
            try:
                result = json.loads(content)
            except json.JSONDecodeError as e:
                state["errors"].append(
                    f"Parsing JSON error (GovernanceAgent): {str(e)} | Raw response: {content}"
                )
                # Nếu parse lỗi, gán mặc định 0
                result = {
                    "g1_score": 0.0,
                    "g2_score": 0.0,
                    "total_g_score": 0.0,
                    "breakdown": {
                        "kyc_reliability": 0.0,
                        "legal_compliance": 0.0
                    },
                    "explanation_message_g": "Không thể parse kết quả từ LLM."
                }

            # Trích kết quả từ JSON trả về
            g1 = float(result.get("g1_score", 0.0))
            g2 = float(result.get("g2_score", 0.0))
            total_g = float(result.get("total_g_score", 0.0))

            # Giới hạn tổng điểm ở 2.0
            capped_total = round(min(total_g, 2.0), 2)

            # Cập nhật state
            state["governance_score"] = capped_total
            state["analysis_results"]["governance"] = {
                "kyc_reliability": round(g1, 2),
                "legal_compliance": round(g2, 2),
                "total": capped_total,
                "explanation_message_g": result.get("explanation_message_g", "Không có giải thích")
            }

            # print(f"⚖️ [LLM] Governance Score: {state['governance_score']:.2f}")
            return state

        except Exception as e:
            state["errors"].append(f"GovernanceAgent LLM error: {str(e)}")
            state["governance_score"] = 0.0
            if "analysis_results" not in state:
                state["analysis_results"] = {}
            state["analysis_results"]["governance"] = {
                "error": str(e),
                "total_governance_score": 0.0
            }
            return state
