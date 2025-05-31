from classes.state import ESGState
import json
from openai import OpenAI
import os
import requests
OPENROUTER_API_KEY = "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"

headers = {
  'Authorization': f'Bearer {OPENROUTER_API_KEY}',
  'Content-Type': 'application/json',
}
class ScoringAgent:
    """
    Agent tính tổng điểm ESG (E + S + G), phân loại, cập nhật va viet bao cao ve diem ESG cua giao dich do vào state.
    """

    def __init__(self, model: str = "gpt-4.1-nano"):
        # Phân loại tổng điểm ESG
        # Lưu ý: khoảng điểm là [min, max], bao gồm cả min và max
        self.classifications = {
            (8.0, 10.0): "Xuất sắc",
            (6.0, 7.9):  "Tốt",
            (4.0, 5.9):  "Trung bình",
            (2.0, 3.9):  "Thấp",
            (0.0, 1.9):  "Rất thấp"
        }
        
        self.system_prompt = """
Bạn là một chuyên gia phân tích ESG (Environmental, Social, Governance) chuyên nghiệp. 
Nhiệm vụ của bạn là tạo báo cáo tổng hợp và đưa ra lời khuyên dựa trên kết quả đánh giá ESG của một giao dịch tài chính.

Yêu cầu:
1. Viết một báo cáo tổng hợp (report) ngắn gọn, chuyên nghiệp về điểm ESG
2. Đưa ra 3-5 lời khuyên cụ thể (advises) để cải thiện điểm ESG trong tương lai

Trả về kết quả ở định dạng JSON như sau:
{
  "report": "Báo cáo tổng hợp ngắn gọn về điểm ESG của giao dịch này...",
  "advises": [
    "Lời khuyên 1 để cải thiện điểm Environment...",
    "Lời khuyên 2 để cải thiện điểm Social...",
    "Lời khuyên 3 để cải thiện điểm Governance...",
    "Lời khuyên 4 tổng quát..."
  ]
}

LƯU Ý:
- Chỉ trả về JSON thuần, không có văn bản giải thích thêm
- Báo cáo nên ngắn gọn, súc tích (khoảng 100 từ)
- Lời khuyên phải cụ thể và có thể thực hiện được
- Sử dụng tiếng Việt tự nhiên, chuyên nghiệp
"""
        
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def process(self, state: ESGState) -> ESGState:
        try:
            # 1. Lấy từng sub‐score
            e = state["analysis_results"]["environment"].get("total", 0.0)
            s = state["analysis_results"]["social"].get("total", 0.0)
            g = state["analysis_results"]["governance"].get("total", 0.0)
            explaination_e = state["analysis_results"]["environment"].get("explaination_message_e", "")
            explaination_s = state["analysis_results"]["social"].get("explaination_message_s", "")
            explaination_g = state["analysis_results"]["governance"].get("explaination_message_g", "")
            
            # 2. Tính tổng và làm tròn 2 chữ số thập phân
            total_esg = round(e + s + g, 2)
            state["total_esg_score"] = total_esg

            # 3. Phân loại
            classification = "Rất thấp"
            for (min_score, max_score), label in self.classifications.items():
                if min_score <= total_esg <= max_score:
                    classification = label
                    break

            # 4. Ensure breakdown structure exists
            if "breakdown" not in state["analysis_results"]:
                state["analysis_results"]["breakdown"] = {}
            
            # 5. Cập nhật breakdown vào analysis_results
            state["analysis_results"]["classification"] = classification
            state["analysis_results"]["breakdown"]["total"] = total_esg

            # 6. Generate report and advises using LLM
            self._generate_report_and_advises(state, e, s, g, total_esg, classification, 
                                            explaination_e, explaination_s, explaination_g)
            
            return state

        except Exception as ex:
            # Nếu có lỗi, thêm vào errors
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"ScoringAgent error: {str(ex)}")
            return state

    def _generate_report_and_advises(self, state: ESGState, e: float, s: float, g: float, 
                                   total_esg: float, classification: str, 
                                   explaination_e: str, explaination_s: str, explaination_g: str):
        """Sử dụng LLM để tạo báo cáo và lời khuyên"""
        try:
            # Chuẩn bị dữ liệu đầu vào cho LLM
            input_data = {
                "transaction_description": state["transaction_data"].get("transaction_description", ""),
                "sender_name": state["sender_info"].get("sender_name", ""),
                "receiver_name": state["receiver_info"].get("receiver_name", ""),
                "scores": {
                    "environment": e,
                    "social": s,
                    "governance": g,
                    "total": total_esg
                },
                "classification": classification,
                "explanations": {
                    "environment": explaination_e,
                    "social": explaination_s,
                    "governance": explaination_g
                }
            }

            # Tạo message cho LLM
           
            response = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json={
                'model': 'meta-llama/llama-3.3-70b-instruct:nitro',
                'messages': [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(input_data, ensure_ascii=False)
                }
                ],
                "response_format": {
                    "type": "json_object",
                }
            })
         
            content = response.json()['choices'][0]['message']['content']

            # Parse JSON response
            try:
                result = json.loads(content)
                state["report"] = result.get("report", "Không thể tạo báo cáo")
                state["advises"] = result.get("advises", ["Không thể tạo lời khuyên"])
            except json.JSONDecodeError as e:
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append(f"Parsing JSON error in report generation: {str(e)}")
                # Fallback values
                state["report"] = f"Giao dịch này đạt điểm ESG {total_esg:.2f}/10.0, được đánh giá {classification}. Cần cải thiện các tiêu chí để đạt hiệu quả bền vững tốt hơn."
                state["advises"] = [
                    "Tìm hiểu các chứng chỉ môi trường để cải thiện điểm E",
                    "Ưu tiên giao dịch với các tổ chức có tác động xã hội tích cực",
                    "Đảm bảo tuân thủ đầy đủ các quy định pháp luật",
                    "Sử dụng các phương thức thanh toán số để giảm tác động môi trường"
                ]

        except Exception as e:
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"LLM report generation error: {str(e)}")
            # Set default values
            state["report"] = f"Giao dịch đạt điểm ESG {total_esg:.2f}/10.0"
            state["advises"] = ["Cải thiện các tiêu chí ESG để đạt hiệu quả bền vững tốt hơn"]

