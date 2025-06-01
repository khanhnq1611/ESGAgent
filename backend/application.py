from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
import json
import os
from main import esg_workflow
from classes.state import ESGState

app = Flask(__name__)

# Configure CORS more specifically
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"], 
     methods=["GET", "POST", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])

# Redirect root to Next.js frontend or serve a simple info page
@app.route("/")
def index():
    return jsonify({
        "message": "ESG Agent Backend API",
        "version": "1.0.0",
        "endpoints": {
            "esg_analysis": "/api/esg (POST)",
            "health": "/health (GET)"
        },
        "frontend_url": "http://localhost:3000"
    })

# Health check endpoint
@app.route("/health")
def health():
    return jsonify({"status": "OK", "service": "ESG Agent Backend"})

@app.route("/api/esg", methods=["POST", "OPTIONS"])
def process_esg():
    # Handle preflight OPTIONS request
    if request.method == "OPTIONS":
        return jsonify({"status": "OK"}), 200
        
    try:
        # Check if request has JSON content type
        if not request.is_json:
            return jsonify({
                "success": False, 
                "error": "Content-Type must be application/json"
            }), 400
            
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False, 
                "error": "No JSON data received"
            }), 400
            
        # Validate required fields
        required_sections = ['transaction_data', 'sender_info', 'receiver_info']
        for section in required_sections:
            if section not in data:
                return jsonify({
                    "success": False,
                    "error": f"Missing required section: {section}"
                }), 400
        
        print("===== Payload đã nhận từ frontend =====")
        print(json.dumps(data, ensure_ascii=False, indent=2))
        print("====================================")
        
       
        # Uncomment this when esg_workflow is working properly
        work_flow = esg_workflow()
        initial_state: ESGState = data
        finally_state = work_flow.invoke(initial_state)
        
        if "advises" not in finally_state or "analysis_results" not in finally_state:
            print("ERROR: Missing required fields in final state")
            print("Final state keys:", list(finally_state.keys()))
            return jsonify({
                "success": False,
                "error": "Analysis incomplete - missing required data"
            }), 500
        
        result_data = {
            "advises": finally_state.get("advises", []),
            "analysis_results": finally_state.get("analysis_results", {}),
            "general_evaluation": finally_state.get("general_evaluation", ""),
        }

        print("===== Kết quả phân tích ESG =====")
        print(json.dumps(result_data, ensure_ascii=False, indent=2))
        print("====================================")

        return jsonify({
            "success": True,
            "data": result_data
        }), 200
    
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


if __name__ == "__main__":
    # For local network access (everyone on same WiFi can access)
    app.run(debug=True, host='0.0.0.0', port=5000)
    
    # For production deployment, use:
    # app.run(debug=False, host='0.0.0.0', port=5000)
