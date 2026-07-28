"""
Budget & Yield Analysis Agent for AgriPlan AI.
Estimates cultivation costs, input requirements, government subsidies, and projected profit.
Demonstrates Tool Use & Calculation Pattern.
"""

from agents.base_agent import BaseAgent

# Baseline Sri Lankan cost estimates per acre
CROP_COST_BENCHMARKS = {
    "rice": {
        "seed_cost_per_acre": 12000,
        "fertilizer_cost_per_acre": 35000,
        "labor_machinery_per_acre": 55000,
        "expected_yield_kg_per_acre": 2200,
        "market_price_per_kg": 110,
        "subsidy_per_acre": 10000
    },
    "maize": {
        "seed_cost_per_acre": 18000,
        "fertilizer_cost_per_acre": 40000,
        "labor_machinery_per_acre": 45000,
        "expected_yield_kg_per_acre": 2500,
        "market_price_per_kg": 135,
        "subsidy_per_acre": 0
    },
    "banana": {
        "seed_cost_per_acre": 105000, # 700 plants @ 150
        "fertilizer_cost_per_acre": 90000,
        "labor_machinery_per_acre": 180000,
        "expected_yield_kg_per_acre": 12000,
        "market_price_per_kg": 120,
        "subsidy_per_acre": 0
    }
}

class BudgetAgent(BaseAgent):
    def __init__(self, api_key: str = None):
        super().__init__(
            name="Budget & Yield Agent",
            role="Agribusiness Economist & Financial Planner",
            model_type="reasoning",
            api_key=api_key
        )

    def calculate_budget(self, crop: str, acres: float, budget_limit_lkr: float = 0) -> dict:
        """
        Tool Execution: Calculate detailed input costs, gross revenue, net profit, and ROI.
        """
        crop_key = crop.lower().strip()
        benchmark = CROP_COST_BENCHMARKS.get(crop_key, CROP_COST_BENCHMARKS["rice"])

        seeds = benchmark["seed_cost_per_acre"] * acres
        fertilizer = benchmark["fertilizer_cost_per_acre"] * acres
        labor = benchmark["labor_machinery_per_acre"] * acres
        total_cost = seeds + fertilizer + labor

        subsidy = benchmark["subsidy_per_acre"] * acres
        net_cost = max(0, total_cost - subsidy)

        est_yield_kg = benchmark["expected_yield_kg_per_acre"] * acres
        gross_revenue = est_yield_kg * benchmark["market_price_per_kg"]
        net_profit = gross_revenue - net_cost
        roi_percentage = (net_profit / net_cost * 100) if net_cost > 0 else 0

        # Run LLM reasoning over financial parameters
        prompt = f"""
Financial Breakdown for {acres} acre(s) of {crop.upper()}:
- Total Input & Labor Cost: LKR {total_cost:,.2f}
- Estimated Government Subsidy: LKR {subsidy:,.2f}
- Net Out-of-Pocket Cost: LKR {net_cost:,.2f}
- Projected Yield: {est_yield_kg:,.0f} kg
- Expected Gross Revenue: LKR {gross_revenue:,.2f}
- Estimated Net Profit: LKR {net_profit:,.2f} (ROI: {roi_percentage:.1f}%)
- User Stated Budget Limit: LKR {budget_limit_lkr:,.2f} (if 0, not specified)

Provide a brief, high-value financial recommendation for the farmer regarding cash flow management, risk mitigation, and optimization of fertilizer/seed purchase.
"""
        advice = self.execute(prompt)

        return {
            "agent": self.name,
            "financial_summary": {
                "crop": crop,
                "acres": acres,
                "total_cost_lkr": total_cost,
                "subsidy_lkr": subsidy,
                "net_cost_lkr": net_cost,
                "estimated_yield_kg": est_yield_kg,
                "gross_revenue_lkr": gross_revenue,
                "net_profit_lkr": net_profit,
                "roi_percentage": round(roi_percentage, 1),
                "is_within_budget": (budget_limit_lkr == 0) or (net_cost <= budget_limit_lkr)
            },
            "financial_advice": advice
        }
