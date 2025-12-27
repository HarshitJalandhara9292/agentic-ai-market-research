# api/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import os, sys
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware

# Add parent directory to path to access marketing_crew
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from marketing_crew.crew import TheMarketingCrew

app = FastAPI(title="AI Marketing Crew API")

# Configure Gemini model
MODEL_NAME = "models/gemini-2.5-flash"
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173", "http://localhost:5174"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InputData(BaseModel):
    product_name: str
    product_description: str
    target_audience: str
    budget: str
    agent_choice: str

@app.get("/")
def home():
    return {"message": "🚀 Marketing Crew API is running"}

@app.post("/run")
async def run_crew():
    crew = TheMarketingCrew().crew()
    result = crew.kickoff()
    return {"result": result}


@app.post("/run_agent")
async def run_agent(data: InputData):
    """Runs selected AI agent or full crew."""
    crew = TheMarketingCrew()

    # ✅ Convert budget safely to number
    try:
        budget_value = float(data.budget)
    except ValueError:
        budget_value = 0.0

    inputs = {
        "product_name": data.product_name,
        "product_description": data.product_description,
        "target_audience": data.target_audience,
        "budget": budget_value,
        "current_date": datetime.now().strftime("%Y-%m-%d")
    }


    try:
        # ✅ Run the correct agent based on selection
        if data.agent_choice == "All Agents":
            results = crew.marketingcrew().kickoff(inputs=inputs)
        elif data.agent_choice == "Head of Marketing":
            results = crew.market_research_crew().kickoff(inputs=inputs)
        elif data.agent_choice == "Blog Writer":
            results = crew.blog_writer_crew().kickoff(inputs=inputs)
        elif data.agent_choice == "SEO Specialist":
            results = crew.seo_crew().kickoff(inputs={
                "product_name": data.product_name,
                "product_description": data.product_description,
                "target_audience": data.target_audience,
                "budget": float(data.budget)
            })
        elif data.agent_choice == "Social Media Creator":
            results = crew.social_media_crew().kickoff(inputs=inputs)
        else:
            results = "Invalid agent choice."
        
        print("Agent results:", results)


        # ✅ Make results readable (paragraph summary)
        if isinstance(results, dict):
            summary_text = "\n".join([f"{k}: {v}" for k, v in results.items()])
        elif isinstance(results, list):
            summary_text = "\n".join(results)
        else:
            summary_text = str(results)

        # ✅ If user selected Head of Marketing → prepare chart data
        if data.agent_choice == "Head of Marketing" and budget_value > 0:
            allocation = {
                "Social Media Ads": budget_value * 0.35,
                "Influencer Marketing": budget_value * 0.25,
                "SEO and Content": budget_value * 0.20,
                "Email Campaigns": budget_value * 0.10,
                "Market Research": budget_value * 0.10
            }
            chart_data = [{"category": k, "value": v} for k, v in allocation.items()]
        else:
            chart_data = []

        # ✅ Send everything back to frontend
        return {
            "status": "success",
            "inputs": inputs,
            "agent": data.agent_choice,
            "summary": summary_text,
            "results": results,
            "chart_data": chart_data
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

    