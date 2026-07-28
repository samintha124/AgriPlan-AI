"""
Knowledge (RAG) Agent for AgriPlan AI.
Searches agricultural domain knowledge base and extracts grounded advice.
Demonstrates Tool Use & ReAct Pattern.
"""

from agents.base_agent import BaseAgent
from rag.retriever import KnowledgeRetriever

class KnowledgeAgent(BaseAgent):
    def __init__(self, api_key: str = None):
        super().__init__(
            name="Knowledge RAG Agent",
            role="Sri Lankan Agricultural Research & Department of Agriculture Specialist",
            model_type="reasoning",
            api_key=api_key
        )
        self.retriever = KnowledgeRetriever()

    def query_knowledge_base(self, query: str) -> dict:
        """
        Tool Execution: Retrieve top matching chunks and generate grounded explanation.
        """
        # Step 1: Tool Call - Vector Retrieval
        retrieved_chunks = self.retriever.retrieve(query, top_k=3)
        context_str = self.retriever.format_context(retrieved_chunks)

        # Step 2: Generation grounded in context
        prompt = f"""
Query: {query}

{context_str}

Instruction: Answer the user query using ONLY the verified facts from the retrieved knowledge base above.
If specific details (like varieties, fertilizer stages, or costs) are present, highlight them clearly.
Include citations to the source file names.
"""
        response = self.execute(prompt)

        return {
            "agent": self.name,
            "answer": response,
            "sources": [c["source"] for c in retrieved_chunks],
            "retrieved_chunks": retrieved_chunks
        }
