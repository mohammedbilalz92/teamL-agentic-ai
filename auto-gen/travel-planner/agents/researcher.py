from autogen_agentchat.agents import AssistantAgent
from config.settings import OPENAI_API_KEY,MAX_TURN,TERMINATION_WORD
from autogen_ext.models.openai import OpenAIChatCompletionClient
from models.apenAi import OpenAIModel

researcher_agent = AssistantAgent(
    name="Researcher",
    description="A researcher agent that helps users find information and answer questions.",
    model=OpenAIModel,
    system_message="you are a researcher agent that helps users find information and answer questions.",
    max_turns=5,
    termination_word="END"
)

