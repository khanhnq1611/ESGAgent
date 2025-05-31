from typing import Any, Dict, List
from classes.state import ESGState


class DataIngestionAgent:
    """Validates and preprocesses transaction data for ESG analysis"""
    
    def __init__(self):
        pass
    
    def process(self, state: ESGState) -> ESGState:
        """Process and validate the input transaction data"""
        try:
            # Get transaction ID for logging
            transaction_id = state["transaction_data"].get("transaction_id", "Unknown")
            print(f"Data ingestion completed successfully for transaction ID: {transaction_id}")
            
            # Initialize errors list if not present
            if "errors" not in state:
                state["errors"] = []
            
            # Validate required fields with correct field names
            if not state["sender_info"].get("sender_name"):  # Changed from "name" to "sender_name"
                state["errors"].append("Missing sender name")
            
            if not state["receiver_info"].get("receiver_name"):  # Changed from "name" to "receiver_name"
                state["errors"].append("Missing receiver name")
            
            # Initialize analysis_results if not present
            if "analysis_results" not in state:
                state["analysis_results"] = {}
                
            return state
            
        except Exception as e:
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append(f"DataIngestionAgent error: {str(e)}")
            return state






