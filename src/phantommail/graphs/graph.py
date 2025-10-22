from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from phantommail.graphs.nodes import GraphNodes
from phantommail.graphs.state import FakeEmailState

# Load environment variables before initializing nodes
load_dotenv()


class ConfigSchema(TypedDict):
    sender: str


graph_nodes = GraphNodes()
graph = StateGraph(FakeEmailState, config_schema=ConfigSchema)

graph.add_node("generate_declaration", graph_nodes.generate_declaration)
graph.add_node("generate_order", graph_nodes.generate_order)
graph.add_node("generate_question", graph_nodes.generate_question)
graph.add_node("generate_complaint", graph_nodes.generate_complaint)
graph.add_node("generate_price_request", graph_nodes.generate_price_request)
graph.add_node("generate_waiting_costs", graph_nodes.generate_waiting_costs)
graph.add_node("generate_update_order", graph_nodes.generate_update_order)
graph.add_node("generate_random", graph_nodes.generate_random)
graph.add_node("send_email", graph_nodes.send_email)

graph.add_conditional_edges(
    START,
    graph_nodes.email_types,
    {
        "order": "generate_order",
        "declaration": "generate_declaration",
        "question": "generate_question",
        "complaint": "generate_complaint",
        "price_request": "generate_price_request",
        "waiting_costs": "generate_waiting_costs",
        "update_order": "generate_update_order",
        "random": "generate_random",
    },
)

graph.add_edge("generate_order", "send_email")
graph.add_edge("generate_declaration", "send_email")
graph.add_edge("generate_question", "send_email")
graph.add_edge("generate_complaint", "send_email")
graph.add_edge("generate_price_request", "send_email")
graph.add_edge("generate_waiting_costs", "send_email")
graph.add_edge("generate_update_order", "send_email")
graph.add_edge("generate_random", "send_email")
graph.add_edge("send_email", END)


graph = graph.compile()


__all__ = ["graph"]
