from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from main import esg_workflow
from classes.state import ESGState

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "message": "ESG Analysis API is running"})

@app.route('/analyze-esg', methods=['POST'])
def analyze_esg():
    """
    Main endpoint to analyze ESG score for a transaction
    Expects JSON payload with transaction_data, sender_info, and receiver_info
    """
    try:
        # Get JSON data from request
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        required_fields = ['transaction_data', 'sender_info', 'receiver_info']
        for field in required_fields:
            if field not in request_data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create initial state from request data
        initial_state: ESGState = {
            "transaction_data": request_data['transaction_data'],
            "sender_info": request_data['sender_info'],
            "receiver_info": request_data['receiver_info'],
            "total_esg_score": 0.0,
            "analysis_results": {},
            "errors": []
        }
        
        # Initialize and run the ESG workflow
        workflow = esg_workflow()
        final_state = workflow.invoke(initial_state)
        
        # Return the analysis results
        return jsonify({
            "success": True,
            "data": final_state
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "An error occurred during ESG analysis"
        }), 500

@app.route('/analyze-esg/sample', methods=['GET'])
def get_sample_request():
    """
    Returns a sample request format for the analyze-esg endpoint
    """
    sample_data = {
        "transaction_data": {
            "transaction_id": "TXN_001",
            "transaction_description": "sample transaction",
            "payment_method": "mobile banking",
            "amount": 1000000,
            "aml_flag": "clean"
        },
        "receiver_info": {
            "receiver_name": "Sample Company",
            "business_type": "technology",
            "kyc_status": "verified",
            "environmental_certificates": [],
            "business_license": "1234567890",
            "tax_code": "0987654321",
            "company_size": "medium"
        },
        "sender_info": {
            "sender_name": "John Doe",
            "kyc_status": "verified"
        }
    }
    
    return jsonify({
        "message": "Sample request format for ESG analysis",
        "sample_request": sample_data,
        "endpoint": "/analyze-esg",
        "method": "POST"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
