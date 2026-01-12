from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from nodes.contractor import contractor_node
from nodes.coder import coder_node
from nodes.supervisor import supervisor_node
from nodes.reviewer import reviewer_node
from nodes.publisher import publisher_node
from nodes.tdd import tdd_node


# 1. Update State
class AgentState(TypedDict):
    task: Optional[str]
    ticket_id: Optional[str]
    contract_path: Optional[str]
    coder_mode: str
    status: str
    error: Optional[str]
    test_files: Optional[list[str]]


# 2. Define the Wrappers
def run_backend(state):
    print("🔄 Switching Coder to BACKEND mode...")
    state["coder_mode"] = "backend"
    return coder_node(state)


def run_frontend(state):
    print("🔄 Switching Coder to FRONTEND mode...")
    state["coder_mode"] = "frontend"
    return coder_node(state)


def route_supervisor(state):
    if state.get("task"):
        return "tdd"
    return END


def route_reviewer(state):
    """
    If approved -> Publisher
    If failed -> Send back to Backend Coder (simplification) to fix.
    """
    if state.get("status") == "approved":
        print("✅ Reviewer Approved -> Publisher")
        return "publisher"

    print("↩️  Routing back to Coder for fixes...")
    return "backend_coder"


# 3. Build the Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("contractor", contractor_node)
workflow.add_node("backend_coder", run_backend)
workflow.add_node("frontend_coder", run_frontend)
workflow.add_node("reviewer", reviewer_node)
workflow.add_node("publisher", publisher_node)
workflow.add_node("tdd", tdd_node)

# 4. Connect the Edges
workflow.set_entry_point("supervisor")

# Conditional Edge from Supervisor
workflow.add_conditional_edges("supervisor", route_supervisor, {"tdd": "tdd", END: END})

workflow.add_edge("tdd", "contractor")
workflow.add_edge("contractor", "backend_coder")
workflow.add_edge("backend_coder", "frontend_coder")
workflow.add_edge("frontend_coder", "reviewer")

# Conditional Edge from Reviewer (The Gauntlet Loop)
workflow.add_conditional_edges(
    "reviewer",
    route_reviewer,
    {"publisher": "publisher", "backend_coder": "backend_coder"},
)

workflow.add_edge("publisher", END)

# 5. Compile
app = workflow.compile()
