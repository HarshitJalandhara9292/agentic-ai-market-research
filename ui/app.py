import streamlit as st
import re
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import sys, os
import google.generativeai as genai

def plot_pie_chart(df):
    """Return a matplotlib Figure for a pie chart of the allocation DataFrame."""
    try:
        fig, ax = plt.subplots(figsize=(6, 6))
        # Ensure numeric values for the pie chart
        values = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
        labels = df["Category"]
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
        ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.
        return fig
    except Exception as e:
        # Fallback empty figure to avoid breaking the Streamlit app
        fig = plt.figure()
        return fig

def display_marketing_insights(budget_input):
    # --- Convert budget to float safely ---
    try:
        budget = float(budget_input)
    except (TypeError, ValueError):
        st.error("❌ Invalid budget input. Please enter a numeric value.")
        return

    # --- Budget allocation logic ---
    allocation = {
        "Social Media Ads": budget * 0.35,
        "Influencer Marketing": budget * 0.25,
        "SEO and Content Marketing": budget * 0.20,
        "Email Campaigns": budget * 0.10,
        "Market Research": budget * 0.10
    }

    df = pd.DataFrame(list(allocation.items()), columns=["Category", "Budget Allocation ($)"])

    # --- Show data ---
    st.markdown("### 💰 Budget Allocation Overview")
    st.dataframe(df)

    # --- Pie chart visualization ---
    fig, ax = plt.subplots()
    ax.pie(df["Budget Allocation ($)"], labels=df["Category"], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')
    st.pyplot(fig)

    # --- Bar chart visualization ---
    st.markdown("### 📊 Budget Distribution by Category")
    st.bar_chart(df.set_index("Category"))

    # --- Text insights ---
    st.markdown(
        f"""
        #### 📈 Insights Summary
        - Total marketing budget: **${budget:,.2f}**
        - Highest allocation: **Social Media Ads (35%)**
        - Balanced investment across digital, influencer, and content strategies.
        """
    )

def parse_marketing_output(text: str):
    """
    Parses AI marketing output into structured DataFrame.
    """
    sections = re.split(
        r"(?=\b(?:Executive Summary|Market Trend Analysis|Competitor Analysis|Conclusion|Recommendations)\b)",
        text
    )
    data = []
    for section in sections:
        if section.strip():
            lines = section.strip().split('\n', 1)
            title = lines[0].strip()
            content = lines[1].strip() if len(lines) > 1 else ''
            data.append({'Section': title, 'Content': content})
    df = pd.DataFrame(data)
    return df if not df.empty else None

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from marketing_crew.crew import TheMarketingCrew

MODEL_NAME = "models/gemini-2.5-flash"

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(MODEL_NAME)

st.set_page_config(page_title="AI Marketing Crew", layout="wide")

st.sidebar.title("⚡ AI Marketing Agents")

product_name = st.sidebar.text_input("Product Name", "AI Powered Excel Automation Tool")
product_description = st.sidebar.text_area(
    "Product Description",
    "A tool that automates repetitive tasks in Excel using AI, saving time and reducing errors."
)
target_audience = st.sidebar.text_input("Target Audience", "Small and Medium Enterprises (SMEs)")
budget = st.sidebar.text_input("Budget", "Rs. 50,000")

agent_choice = st.sidebar.selectbox(
    "Choose Agent(s) to Run",
    ["All Agents", "Head of Marketing", "Blog Writer", "SEO Specialist", "Social Media Creator"]
)

run_button = st.sidebar.button("🚀 Run Campaign")

inputs = {
    "product_name": product_name,
    "target_audience": target_audience,
    "product_description": product_description,
    "budget": budget,
    "current_date": datetime.now().strftime("%Y-%m-%d"),
}

token_usage = {
    "total_tokens": 13096,
    "prompt_tokens": 11715,
    "cached_prompt_tokens": 0,
    "completion_tokens": 1381,
    "successful_requests": 5
}

MODEL_PRICING = {
    "prompt": 0.003,
    "completion": 0.006
}

def calculate_cost(usage):
    prompt_cost = (usage["prompt_tokens"] / 1000) * MODEL_PRICING["prompt"]
    completion_cost = (usage["completion_tokens"] / 1000) * MODEL_PRICING["completion"]
    total_cost = prompt_cost + completion_cost
    return round(prompt_cost, 4), round(completion_cost, 4), round(total_cost, 4)

prompt_cost, completion_cost, total_cost = calculate_cost(token_usage)

# ---- Streamlit Display ----
st.subheader("📊 Token Usage & Cost Report")

st.metric("Total Tokens", token_usage["total_tokens"])
st.metric("Prompt Tokens", token_usage["prompt_tokens"])
st.metric("Completion Tokens", token_usage["completion_tokens"])
st.metric("Successful Requests", token_usage["successful_requests"])

st.write("💰 **Estimated Cost** (based on model pricing):")
st.write(f"- Prompt Cost: **${prompt_cost}**")
st.write(f"- Completion Cost: **${completion_cost}**")
st.write(f"- Total Cost: **${total_cost}**")

crew = TheMarketingCrew()

tabs = st.tabs(["📊 Strategy", "✍️ Blogs", "🔍 SEO", "📱 Social Media"])

# --- Helper function to extract table-like data ---
def extract_table(text):
    """Extracts tabular-looking data (Category - Value) and returns a dataframe."""
    pattern = r"([\w\s]+)\s*[:\-]\s*(\d+\.?\d*|\w+)"
    matches = re.findall(pattern, text)
    if matches:
        df = pd.DataFrame(matches, columns=["Category", "Value"])
        return df
    return None

# --- Helper function to plot a chart ---
def plot_chart(df, title):
    """Creates and displays a bar chart from dataframe."""
    try:
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
        df = df.dropna()
        fig, ax = plt.subplots()
        ax.bar(df["Category"], df["Value"])
        ax.set_title(title)
        ax.set_xlabel("Category")
        ax.set_ylabel("Value")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig)
    except Exception as e:
        st.warning(f"Could not create chart: {e}")

# --- Main button logic ---
if run_button:
    inputs = {
        "product_name": product_name,
        "product_description": product_description,
        "target_audience": target_audience,
        "budget": budget,
        "current_date": datetime.now().strftime("%Y-%m-%d")
    }

    if agent_choice == "All Agents":
        st.info("🌍 Running **Full Crew**...")
        try:
            results = crew.marketingcrew().kickoff(inputs=inputs)
        except Exception as e:
            st.error(f"Error running full crew: {e}")
            results = "An error occurred while running the full crew."
        with tabs[0]:
            st.subheader("Full Marketing Strategy")
            st.write(results)
            df = extract_table(str(results))
            if df is not None:
                st.dataframe(df)
                plot_chart(df, "Marketing Strategy Overview")

    elif agent_choice == "Head of Marketing":
        st.info("🚀 Running **Head of Marketing Agent**...")
        try:
            results = crew.market_research_crew().kickoff(inputs=inputs)
        except Exception as e:
            st.error(f"Error running Head of Marketing agent: {e}")
            results = "An error occurred while running the Head of Marketing agent."

        with tabs[0]:
            st.subheader("Market Research Output")
            st.write(results)

            # --- Parse structured sections from LLM output ---
            df = parse_marketing_output(str(results))

            if df is not None:
                st.markdown("### 📋 Structured Report")
                st.dataframe(df)

                # --- Word count chart ---
                df['Word Count'] = df['Content'].apply(lambda x: len(x.split()))
                st.markdown("### 📊 Word Count by Section")
                st.bar_chart(df.set_index('Section')['Word Count'])

                # --- Display useful marketing insights ---
                display_marketing_insights(budget)  # <-- pass the user’s entered budget here
            else:
                st.warning("No structured data found in the output.")



    elif agent_choice == "Blog Writer":
        st.info("✍️ Running **Blog Writer Agent**...")
        try:
            results = crew.blog_writer_crew().kickoff(inputs=inputs)
        except Exception as e:
            st.error(f"Error running Blog Writer agent: {e}")
            results = "An error occurred while running the Blog Writer agent."
        with tabs[1]:
            st.subheader("Draft Blogs")
            st.write(results)
            df = extract_table(str(results))
            if df is not None:
                st.dataframe(df)
                plot_chart(df, "Blog Content Stats")

    elif agent_choice == "SEO Specialist":
        st.info("🔍 Running **SEO Specialist Agent**...")
        try:
            results = crew.seo_crew().kickoff(inputs=inputs)
        except Exception as e:
            st.error(f"Error running SEO Specialist agent: {e}")
            results = "An error occurred while running the SEO Specialist agent."
        with tabs[2]:
            st.subheader("SEO Optimized Blogs")
            st.write(results)
            df = extract_table(str(results))
            if df is not None:
                st.dataframe(df)
                plot_chart(df, "SEO Keyword Performance")

    elif agent_choice == "Social Media Creator":
        st.info("📱 Running **Social Media Creator Agent**...")
        try:
            results = crew.social_media_crew().kickoff(inputs=inputs)
        except Exception as e:
            st.error(f"Error running Social Media Creator agent: {e}")
            results = "An error occurred while running the Social Media Creator agent."
        with tabs[3]:
            st.subheader("Social Media Posts")
            st.write(results)
            df = extract_table(str(results))
            if df is not None:
                st.dataframe(df)
                plot_chart(df, "Post Engagement Overview")
