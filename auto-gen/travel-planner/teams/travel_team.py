from autogen_agentchat.teams import RoundRobinGroupChat

from agents.planner import planner_agent
from agents.researcher import researcher_agent
from config.settings import TERMINATION_WORD
from autogen_agentchat.conditions import TextMentionTermination
from utils.utils import get_termination_condition

team = RoundRobinGroupChat(
    participants=[planner_agent,researcher_agent],
    name="Travel Team",
    description="A team of agents that helps users plan their trips by providing information about destinations, itineraries and travel tips.",
    system_message="You are a travel planning team. Your task is to help users plan their trips by providing information about destination, " \
    "itineraries and travel tips.",
    termination_condition=get_termination_condition()
)