from typing import TypedDict, NotRequired, Required, Dict, List, Any, Annotated
from operator import add

def merge_dicts(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """Custom reducer to merge dictionaries without conflicts"""
    if not left:
        return right
    if not right:
        return left
    merged = left.copy()
    merged.update(right)
    return merged

def add_floats(left: float, right: float) -> float:
    """Custom reducer for adding floats, handling the case where one might be the initial value"""
    return left + right

def take_last(left: Any, right: Any) -> Any:
    """Custom reducer that takes the last (most recent) value"""
    return right

# Define the input state
class ESGState(TypedDict, total=False):
    transaction_data: Annotated[Dict[str, Any], take_last]
    sender_info: Annotated[Dict[str, Any], take_last]
    receiver_info: Annotated[Dict[str, Any], take_last]
    total_esg_score: Annotated[float, take_last]
    analysis_results: Annotated[Dict[str, Any], merge_dicts]
    general_evaluation: NotRequired[Annotated[str, take_last]]
    advises: NotRequired[Annotated[List[str], add]]
    errors: Annotated[List[str], add]

