"""
Planner / Orchestrator Agent for AgriPlan AI.
Demonstrates:
- Pattern 1: Planning & Task Decomposition
- Pattern 2: Tool Use & ReAct
- Pattern 3: Orchestrator-Worker / Router Pattern
Communicates with KnowledgeAgent and BudgetAgent.
"""

from agents.base_agent import BaseAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.budget_agent import BudgetAgent

class PlannerAgent(BaseAgent):
    def __init__(self, api_key: str = None):
        # Fast model for intent parsing & routing
        super().__init__(
            name="Planner & Orchestrator Agent",
            role="Chief Agricultural Planner & Multi-Agent Orchestrator",
            model_type="fast",
            api_key=api_key
        )
        self.knowledge_agent = KnowledgeAgent(api_key=api_key)
        self.budget_agent = BudgetAgent(api_key=api_key)

    def plan_and_execute(self, crop: str, acres: float, location: str = "Dry Zone", budget_limit: float = 0, custom_question: str = "") -> dict:
        """
        Orchestration Flow:
        1. Formulate sub-tasks (Planning pattern).
        2. Worker 1 (KnowledgeAgent) executes RAG search.
        3. Worker 2 (BudgetAgent) computes financial breakdown.
        4. Synthesizer weaves worker outputs into final comprehensive plan.
        """
        # Step 1: Sub-task formulation
        rag_query = f"{crop} cultivation best practices seed variety fertilizer {location} Sri Lanka {custom_question}".strip()
        
        # Step 2: Communicate with Worker Agents (Agent Communication requirement)
        knowledge_res = self.knowledge_agent.query_knowledge_base(rag_query)
        budget_res = self.budget_agent.calculate_budget(crop, acres, budget_limit)

        # Step 3: Synthesis using reasoning model
        synthesis_prompt = f"""
USER CULTIVATION PLAN REQUEST:
- Crop: {crop.title()}
- Land Area: {acres} Acre(s)
- Location / Zone: {location}
- Stated Budget Limit: LKR {budget_limit:,.2f}
- Specific Question: {custom_question or 'Provide full cultivation guidance'}

WORKER 1 (RAG KNOWLEDGE AGENT) REPORT:
{knowledge_res['answer']}
Sources: {', '.join(knowledge_res['sources'])}

WORKER 2 (BUDGET & YIELD AGENT) REPORT:
- Net Cost: LKR {budget_res['financial_summary']['net_cost_lkr']:,.2f}
- Projected Yield: {budget_res['financial_summary']['estimated_yield_kg']:,.0f} kg
- Net Profit: LKR {budget_res['financial_summary']['net_profit_lkr']:,.2f} (ROI: {budget_res['financial_summary']['roi_percentage']}%)
Financial Advice: {budget_res['financial_advice']}

Task: As Chief AgriPlan Strategist, combine these findings into a clear, professional, multi-section Cultivation Plan for the farmer.
Include:
1. Executive Summary & Suitability Analysis
2. Recommended Varieties & Planting Timeline
3. Step-by-Step Fertilizer & Irrigation Schedule
4. Financial Forecast & Budget Feasibility
5. Key Risk Management (Pests & Water)
"""
        final_plan = self.execute(synthesis_prompt)

        return {
            "crop": crop,
            "acres": acres,
            "location": location,
            "planner_agent": self.name,
            "knowledge_agent_output": knowledge_res,
            "budget_agent_output": budget_res,
            "final_cultivation_plan": final_plan
        }
