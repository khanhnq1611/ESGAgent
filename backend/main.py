import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from classes.state import ESGState
from nodes import data_ingestion, enviroment_agent, social_agent, governance_agent, scoring_agent
from langgraph.graph import StateGraph, END

def esg_workflow():
    """Creates and returns the compiled ESG workflow"""
    # Initialize workflow
    data_agent = data_ingestion.DataIngestionAgent()
    env_agent = enviroment_agent.EnvironmentAgent()
    soc_agent = social_agent.SocialAgent()
    gov_agent = governance_agent.GovernanceAgent()
    score_agent = scoring_agent.ScoringAgent()

    # Create the workflow
    workflow = StateGraph(ESGState) 

    # add nodes to the workflow
    workflow.add_node("data_ingestion", data_agent.process)
    workflow.add_node("environment_agent", env_agent.process)
    workflow.add_node("social_agent", soc_agent.process)
    workflow.add_node("governance_agent", gov_agent.process)
    workflow.add_node("scoring_agent", score_agent.process)
    
    # Define the workflow structure - run in parallel now that concurrent updates are handled
    workflow.add_edge("data_ingestion", "environment_agent")
    workflow.add_edge("data_ingestion", "social_agent")
    workflow.add_edge("data_ingestion", "governance_agent")
    workflow.add_edge("environment_agent", "scoring_agent")
    workflow.add_edge("social_agent", "scoring_agent")
    workflow.add_edge("governance_agent", "scoring_agent")
    workflow.add_edge("scoring_agent", END)
    
    # Set the entry point
    workflow.set_entry_point("data_ingestion")
    
    return workflow.compile()


def main():
    # Initialize the ESG workflow
    workflow = esg_workflow()

    # Create an initial state with dummy data
    initial_state: ESGState = {
        "transaction_data": {
        "transaction_id": "TXN_004",
        "transaction_description": "quyên góp hỗ trợ phẫu thuật cho trẻ em khuyết tật",
        "payment_method": "mobile banking",
        "amount": 1500000,
        "aml_flag": "clean"
        },
        "receiver_info": {
            "receiver_name": "Quỹ Phẫu Thuật Nụ Cười Việt Nam",
            "business_type": "nonprofit healthcare",
            "kyc_status": "verified",
            "environmental_certificates": [],
            "business_license": "9988776655",
            "tax_code": "1122334455",
            "company_size": "medium"
        },
        "sender_info": {
            "sender_name": "Tran Van D",
            "kyc_status": "verified"
        },
        "total_esg_score": 0.0,
        "analysis_results": {},
        "errors": []
    }

    # Run the workflow
    final_state = workflow.invoke(initial_state)
    print(json.dumps(final_state, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()