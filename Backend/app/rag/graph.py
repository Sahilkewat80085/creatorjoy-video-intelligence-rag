from langgraph.graph import StateGraph, END
from app.rag.state import ChatState
from app.rag.nodes.retriever_node import retriever_node
from app.rag.nodes.prompt_node import prompt_node
from app.rag.nodes.generator_node import generator_node
from app.rag.nodes.memory_node import memory_node

# Define the graph
workflow = StateGraph(ChatState)

# Add nodes
workflow.add_node("memory", memory_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("prompt", prompt_node)
workflow.add_node("generator", generator_node)

# Set edges
workflow.set_entry_point("memory")
workflow.add_edge("memory", "retriever")
workflow.add_edge("retriever", "prompt")
workflow.add_edge("prompt", "generator")
workflow.add_edge("generator", END)

# Compile the standard graph
app = workflow.compile()

# Define the stream graph that stops at prompt
stream_workflow = StateGraph(ChatState)
stream_workflow.add_node("memory", memory_node)
stream_workflow.add_node("retriever", retriever_node)
stream_workflow.add_node("prompt", prompt_node)

stream_workflow.set_entry_point("memory")
stream_workflow.add_edge("memory", "retriever")
stream_workflow.add_edge("retriever", "prompt")
stream_workflow.add_edge("prompt", END)

# Compile the stream graph
stream_app = stream_workflow.compile()
