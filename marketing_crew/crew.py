from typing import List
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
    SerperDevTool,
    ScrapeWebsiteTool,
    DirectoryReadTool,
    FileWriterTool,
    FileReadTool
)
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

_ = load_dotenv()

llm = LLM(
    model="gemini/gemini-2.0-flash",
    temperature=0.7,          
    api_key=os.getenv("GOOGLE_API_KEY"),
    max_output_tokens=4096 ,
    top_p= 0.9
)

# print("API Key Used by Crew AI:", os.getenv("GOOGLE_API_KEY"))

class Content(BaseModel):
    content_type: str = Field(..., description="The type of content to be created (e.g., blog post, social media post, video)")
    topic: str = Field(..., description="The topic of the content")
    target_audience: str = Field(..., description="The target audience for the content")
    tags: List[str] = Field(..., description="Tags to be used for the content")
    content: str = Field(..., description="The content itself")


@CrewBase
class TheMarketingCrew():
    base_dir = os.path.dirname(__file__)  
    agents_config = os.path.join(base_dir, "config", "agents.yaml")
    tasks_config = os.path.join(base_dir, "config", "tasks.yaml")

    # Agents 
    @agent
    def head_of_marketing(self) -> Agent:
        return Agent(
            config=self.agents_config['head_of_marketing'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), DirectoryReadTool('resources/drafts'),
                   FileWriterTool(), FileReadTool()],
            reasoning=False,
            inject_date=False,
            llm=llm,
            allow_delegation=False,
            max_iter=1,
            max_rpm=5
        )

    @agent
    def content_creator_social_media(self) -> Agent:
        return Agent(
            config=self.agents_config['content_creator_social_media'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), DirectoryReadTool('resources/drafts'),
                   FileWriterTool(), FileReadTool()],
            reasoning=False,
            inject_date=False,
            llm=llm,
            allow_delegation=False,
            max_iter=1,
            max_rpm=5
        )

    @agent
    def content_writer_blogs(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer_blogs'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), DirectoryReadTool('resources/drafts/blogs'),
                   FileWriterTool(), FileReadTool()],
            reasoning=False,
            inject_date=False,
            llm=llm,
            allow_delegation=False,
            max_iter=1,
            max_rpm=5
        )

    @agent
    def seo_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['seo_specialist'],
            tools=[SerperDevTool(), ScrapeWebsiteTool(), DirectoryReadTool('resources/drafts'),
                   FileWriterTool(), FileReadTool()],
            reasoning=False,
            inject_date=False,
            llm=llm,
            allow_delegation=False,
            max_iter=1,
            max_rpm=5
        )

    @task
    def market_research(self) -> Task:
        return Task(config=self.tasks_config['market_research'], agent=self.head_of_marketing())

    @task
    def draft_blogs(self) -> Task:
        return Task(config=self.tasks_config['draft_blogs'], agent=self.content_writer_blogs(), output_json=Content)

    @task
    def seo_optimization(self) -> Task:
        return Task(config=self.tasks_config['seo_optimization'], agent=self.seo_specialist(), output_json=Content)

    @task
    def prepare_post_drafts(self) -> Task:
        return Task(config=self.tasks_config['prepare_post_drafts'], agent=self.content_creator_social_media(), output_json=Content)

    # Crew (all agents + tasks)
    @crew
    def marketingcrew(self) -> Crew:
        """Creates the Marketing crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
            planning=False,        
            max_rpm=5
        )

    @crew
    def market_research_crew(self) -> Crew:
        return Crew(
            agents=[self.head_of_marketing()],
            tasks=[self.market_research()],
            process=Process.sequential,
            verbose=False,
            planning=False,        
            max_rpm=5
        )
    @crew
    def blog_writer_crew(self) -> Crew:
        return Crew(
            agents=[self.content_writer_blogs()],
            tasks=[self.draft_blogs()],
            process=Process.sequential,
            verbose=False,
            planning=False,        
            max_rpm=5
        )
    @crew
    def seo_crew(self) -> Crew:
        return Crew(
            agents=[self.seo_specialist()],
            tasks=[self.seo_optimization()],
            process=Process.sequential,
            verbose=False,
            planning=False,        
            max_rpm=5
        )
    @crew
    def social_media_crew(self) -> Crew:
        return Crew(
            agents=[self.content_creator_social_media()],
            tasks=[self.prepare_post_drafts()],
            process=Process.sequential,
            verbose=False,
            planning=False,        
            max_rpm=5
        )
    
    @crew
    def market_research_crew(self) -> Crew:
        return Crew(
            agents=[self.head_of_marketing()],
            tasks=[self.market_research()],
            process=Process.sequential,
            verbose=False,
            planning=False,        
            max_rpm=5
        )