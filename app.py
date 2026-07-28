import streamlit as st
import os
import pandas as pd
from utils.config import get_api_key
from agents.planner_agent import PlannerAgent
from agents.knowledge_agent import KnowledgeAgent
from agents.budget_agent import BudgetAgent
from rag.retriever import KnowledgeRetriever

# Page configuration
st.set_page_config(
    page_title="AgriPlan AI - Agentic Farming Assistant",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS
def load_css():
    css_path = os.path.join("assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Header Banner
st.markdown("""
<div class="main-header">
    <h1>🌾 AgriPlan AI</h1>
    <p>An Agentic AI Multi-Agent Assistant for Sri Lankan Farmers & Agribusiness Planning</p>
</div>
""", unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.image("https://img.icons8.com/color/96/sprout.png", width=80)
st.sidebar.title("⚙️ System Control & Keys")

# Secure API Key loading
groq_key = get_api_key("GROQ_API_KEY")
openrouter_key = get_api_key("OPENROUTER_API_KEY")

api_key_input = st.sidebar.text_input(
    "🔑 Groq / OpenRouter API Key",
    value=groq_key or openrouter_key or "",
    type="password",
    help="Provided via .env or Streamlit secrets. You can also paste key here."
)

active_key = api_key_input.strip()

if not active_key:
    st.sidebar.warning("⚠️ No API Key detected! Please enter a key above or add GROQ_API_KEY to your .env file.")
else:
    st.sidebar.success("✅ API Key configured successfully!")

st.sidebar.markdown("---")
st.sidebar.subheader("🤖 Active AI Agents")
st.sidebar.markdown("""
- **🧠 Planner Agent**: ReAct / Planning
- **📚 Knowledge Agent**: RAG Vector Search
- **📊 Budget Agent**: Financial Calculator
""")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Selected AI Models")
st.sidebar.info("""
- **Fast Model**: `llama-3.1-8b-instant` (Routing & Intent)
- **Reasoning Model**: `llama-3.3-70b-versatile` (Planning & Synthesis)
""")

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🌾 Cultivation Planner (Multi-Agent)",
    "📚 Knowledge Assistant (RAG QA)",
    "📊 Financial & Cost Estimator",
    "ℹ️ Architecture & Rubric Specs"
])

# ---------------------------------------------------------
# TAB 1: Cultivation Planner (Multi-Agent System)
# ---------------------------------------------------------
with tab1:
    st.subheader("🌾 Automated Cultivation Master Plan")
    st.caption("Inputs are analyzed collaboratively by the Planner Agent, RAG Knowledge Agent, and Budget Agent.")

    col1, col2, col3 = st.columns(3)
    with col1:
        crop = st.selectbox("Select Crop", ["Rice (Paddy)", "Maize (Corn)", "Banana (Plantain)"])
    with col2:
        acres = st.number_input("Land Size (Acres)", min_value=0.25, max_value=50.0, value=2.0, step=0.25)
    with col3:
        location = st.selectbox("Agro-Ecological Zone", ["Dry Zone (Anuradhapura/Polonnaruwa)", "Intermediate Zone (Kurunegala)", "Wet Zone (Low Country)"])

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        budget_limit = st.number_input("Budget Limit (LKR, 0 for unlimited)", min_value=0, value=250000, step=10000)
    with col_b2:
        custom_question = st.text_input("Specific Question / Requirement", placeholder="e.g. Which fertilizer schedule should I follow for Maha season?")

    if st.button("🚀 Generate Cultivation Plan", type="primary", use_container_width=True):
        if not active_key:
            st.error("Please enter a valid Groq or OpenRouter API key in the sidebar to run the multi-agent system.")
        else:
            with st.spinner("🤖 Multi-agent system collaborating (Planner ➔ RAG Search ➔ Financial Calculator)..."):
                try:
                    planner = PlannerAgent(api_key=active_key)
                    crop_clean = crop.split(" ")[0].lower()
                    result = planner.plan_and_execute(
                        crop=crop_clean,
                        acres=acres,
                        location=location,
                        budget_limit=budget_limit,
                        custom_question=custom_question
                    )

                    st.success("✅ Multi-Agent Orchestration Completed Successfully!")

                    # Financial Metric Cards
                    fin = result["budget_agent_output"]["financial_summary"]
                    m1, m2, m3, m4 = st.columns(4)
                    with m1:
                        st.markdown(f"""<div class="metric-card"><h3>LKR {fin['net_cost_lkr']:,.0f}</h3><p>Net Out-of-Pocket Cost</p></div>""", unsafe_allow_html=True)
                    with m2:
                        st.markdown(f"""<div class="metric-card"><h3>{fin['estimated_yield_kg']:,.0f} kg</h3><p>Projected Yield</p></div>""", unsafe_allow_html=True)
                    with m3:
                        st.markdown(f"""<div class="metric-card"><h3>LKR {fin['net_profit_lkr']:,.0f}</h3><p>Estimated Net Profit</p></div>""", unsafe_allow_html=True)
                    with m4:
                        st.markdown(f"""<div class="metric-card"><h3>{fin['roi_percentage']}%</h3><p>Return on Investment (ROI)</p></div>""", unsafe_allow_html=True)

                    st.markdown("### 📋 Final Synthesized Cultivation Plan")
                    st.markdown(result["final_cultivation_plan"])

                    # Agent Workflows Expander
                    with st.expander("🔍 View Raw Agent Communication & RAG Retrieval Trace"):
                        st.markdown("#### 📚 RAG Knowledge Agent Trace")
                        st.write("**Retrieved Sources:**", result["knowledge_agent_output"]["sources"])
                        st.text_area("RAG Grounded Response", result["knowledge_agent_output"]["answer"], height=150)

                        st.markdown("#### 📊 Budget Agent Trace")
                        st.json(result["budget_agent_output"]["financial_summary"])
                        st.write("**Financial Recommendation:**", result["budget_agent_output"]["financial_advice"])
                except Exception as e:
                    st.error(f"Error during agent execution: {str(e)}")

# ---------------------------------------------------------
# TAB 2: Knowledge Assistant (RAG QA)
# ---------------------------------------------------------
with tab2:
    st.subheader("📚 RAG Knowledge Base Assistant")
    st.caption("Ask questions directly against our 20+ document knowledge base (Department of Agriculture guides, fertilizers, subsidies).")

    user_query = st.text_input("Ask any agricultural question:", placeholder="e.g. What is the recommended seeding rate for paddy in Sri Lanka?")
    
    col_q1, col_q2 = st.columns([1, 4])
    with col_q1:
        search_btn = st.button("🔎 Search Knowledge Base")

    if user_query and (search_btn or user_query):
        if not active_key:
            st.error("Please enter an API Key in the sidebar.")
        else:
            with st.spinner("Searching vector index & synthesizing grounded response..."):
                knowledge_agent = KnowledgeAgent(api_key=active_key)
                res = knowledge_agent.query_knowledge_base(user_query)

                st.markdown("### 📝 Grounded Answer")
                st.markdown(res["answer"])

                st.markdown("### 📄 Retrieved Context Snippets (RAG Sources)")
                for chunk in res["retrieved_chunks"]:
                    st.info(f"**Source:** `{chunk['source']}` (Chunk #{chunk['chunk_id']})\n\n{chunk['content']}")

# ---------------------------------------------------------
# TAB 3: Financial & Cost Estimator
# ---------------------------------------------------------
with tab3:
    st.subheader("📊 Agribusiness Budget & Yield Estimator")
    st.caption("Interactive financial calculator based on verified Sri Lankan agricultural benchmark costs.")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        f_crop = st.selectbox("Crop Type", ["Rice", "Maize", "Banana"])
        f_acres = st.slider("Cultivation Area (Acres)", 0.5, 20.0, 2.0, 0.5)
    with col_f2:
        f_budget = st.number_input("Farmer Budget Limit (LKR)", value=300000, step=25000)

    if st.button("🧮 Compute Financials"):
        agent = BudgetAgent(api_key=active_key if active_key else "dummy")
        data = agent.calculate_budget(f_crop, f_acres, f_budget)["financial_summary"]

        df = pd.DataFrame({
            "Financial Metric": ["Total Cost", "Estimated Subsidy", "Net Cost", "Gross Revenue", "Net Profit", "ROI (%)"],
            "Amount (LKR / Value)": [
                f"LKR {data['total_cost_lkr']:,.2f}",
                f"LKR {data['subsidy_lkr']:,.2f}",
                f"LKR {data['net_cost_lkr']:,.2f}",
                f"LKR {data['gross_revenue_lkr']:,.2f}",
                f"LKR {data['net_profit_lkr']:,.2f}",
                f"{data['roi_percentage']}%"
            ]
        })
        st.table(df)

        if data["is_within_budget"]:
            st.success("✅ Projected net cost is within your specified budget limit!")
        else:
            st.warning("⚠️ Projected net cost exceeds your specified budget limit. Consider applying for micro-irrigation subsidies or scaling down acreage.")

# ---------------------------------------------------------
# TAB 4: Architecture & Rubric Specs
# ---------------------------------------------------------
with tab4:
    st.subheader("ℹ️ Coursework Technical Specs & Architecture (IT41043)")

    st.markdown("### 1. Agentic AI Patterns Implemented (15 Marks)")
    st.markdown("""
    - **Pattern 1: Planning & Task Decomposition**: `PlannerAgent` decomposes complex user queries into sub-tasks (RAG lookup + Financial calculations).
    - **Pattern 2: Tool Use & ReAct**: Agents dynamically invoke the `KnowledgeRetriever` vector search tool and `calculate_budget` calculation engine.
    - **Pattern 3: Orchestrator-Worker / Router Pattern**: `PlannerAgent` routes tasks to specialized worker agents (`KnowledgeAgent` & `BudgetAgent`) and synthesizes final outputs.
    """)

    st.markdown("### 2. Multi-Model Strategy (15 Marks)")
    model_df = pd.DataFrame({
        "Model": ["Groq Llama 3.1 8B Instant", "Groq Llama 3.3 70B Versatile / OpenRouter"],
        "Role": ["Fast Router & Intent Parser", "Deep Reasoning & Cultivation Synthesizer"],
        "Latency": ["~150 ms (Ultra Fast)", "~600 ms (Fast)"],
        "Context Window": ["128k Tokens", "128k Tokens"],
        "Justification": ["Low cost/latency for high-speed routing & sub-task planning.", "High reasoning capacity for complex agricultural planning and RAG synthesis."]
    })
    st.table(model_df)

    st.markdown("### 3. Agent Communication Flow")
    st.code("""
User Prompt ➔ [Planner Agent (Router)]
                     ├──➔ [Knowledge Agent] ➔ (ChromaDB RAG Tool) ──┐
                     └──➔ [Budget Agent]    ➔ (Financial Calculator) ─┴─➔ [Synthesizer] ➔ Final Cultivation Plan
    """, language="text")
