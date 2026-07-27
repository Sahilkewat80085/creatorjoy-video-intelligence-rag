import logging
from langgraph.graph import StateGraph, END
from app.rag.state import ChatState
from app.rag.nodes.retriever_node import retriever_node
from app.rag.nodes.prompt_node import prompt_node
from app.rag.nodes.generator_node import generator_node
from app.rag.nodes.memory_node import memory_node

logger = logging.getLogger(__name__)

logger.info("Initializing StateGraph workflows for the RAG pipeline...")

try:
    # -------------------------------------------------------------
    # 1. Main RAG Pipeline Workflow
    # -------------------------------------------------------------
    # Define the graph structure with ChatState schema
    workflow = StateGraph(ChatState)

    # Register execution nodes
    workflow.add_node("memory", memory_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("prompt", prompt_node)
    workflow.add_node("generator", generator_node)

    # Establish flow edges
    workflow.set_entry_point("memory")
    workflow.add_edge("memory", "retriever")
    workflow.add_edge("retriever", "prompt")
    workflow.add_edge("prompt", "generator")
    workflow.add_edge("generator", END)

    # Compile the full RAG execution graph
    app = workflow.compile()
    logger.info("Successfully compiled the main RAG workflow StateGraph.")

except Exception as e:
    logger.exception("Failed to build or compile the main RAG workflow.")
    raise e

try:
    # -------------------------------------------------------------
    # 2. Streaming RAG Pipeline Workflow (Stops after prompt node)
    # -------------------------------------------------------------
    # Define structure for streaming queries that handles generation on demand
    stream_workflow = StateGraph(ChatState)
    stream_workflow.add_node("memory", memory_node)
    stream_workflow.add_node("retriever", retriever_node)
    stream_workflow.add_node("prompt", prompt_node)

    # Establish flow edges
    stream_workflow.set_entry_point("memory")
    stream_workflow.add_edge("memory", "retriever")
    stream_workflow.add_edge("retriever", "prompt")
    stream_workflow.add_edge("prompt", END)

    # Compile the stream RAG execution graph
    stream_app = stream_workflow.compile()
    logger.info("Successfully compiled the streaming RAG workflow StateGraph.")

except Exception as e:
    logger.exception("Failed to build or compile the streaming RAG workflow.")
    raise e

