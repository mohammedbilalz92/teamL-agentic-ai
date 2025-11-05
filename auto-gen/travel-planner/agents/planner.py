from autogen_agentchat.agents import AssistantAgent
from config.settings import OPENAI_API_KEY,MAX_TURN,TERMINATION_WORD
from autogen_ext.models.openai import OpenAIChatCompletionClient
from models.apenAi import OpenAIModel

planner_agent = AssistantAgent(
    name="Travel Planner",
    description="A travel planner agent that helps users plan their trips.",
    model=OpenAIModel,
    system_message="You are a travel planner agent. Your task is to help users plan trips",
    max_turns=5,
    termination_word="END"
)

