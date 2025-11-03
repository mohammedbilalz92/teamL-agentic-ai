from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination
import os
from dotenv import load_dotenv
from autogen_agentchat.ui import Console
from autogen_agentchat.base import TaskResult
load_dotenv()

async def team_Config(job_position="Software Engineer"):

    # define Model
    model_client = OpenAIChatCompletionClient(model="gpt-4.1-mini", api_key=os.getenv("OPENAI_API_KEY"))

    # Defining our Agent
    # 1. Interviewer Agent
    # 2. Interviewee Agent
    # 3. Career coach Agent

    job_position = "Software Engineer"

    interviewer = AssistantAgent (
        name="interviewer",
        model_client=model_client,
        description=f"An AI Agent that conducts interviews for a {job_position} position.",
        system_message=f'''
            You are a professional interviewer for a {job_position} position.
            Ask one question at a time and Wait for user to respond.
            Ask 3 questions in total covering technical skills and experience, problem-solving abilities, and cultural fit.
            After asking 3 questions, say 'TERMINATE' at the end of the interview.
            '''
        )

    candidate = UserProxyAgent(
        name="candidate",
        description=f"An agent that simulates a candidate for a {job_position} position.",
        input_func=input
    )

    career_coach = AssistantAgent(
        name='career_coach',
        model_client=model_client,
        description=f"An AI agent that provides feedback and advice to a candidates for a {job_position} position.",
        system_message=f'''
        You are a career coach specializing in preparing candidates for {job_position} interviews.
        provide constructive feedback on the candidate's responses and suggest improvements.
        After the interview, summarize the candidate's performance and provide actionable advice.
        '''
    )

    # A Team is a group of agents that work together to achieve a common goal.

    #RoundRobinGroupChat - a team where participants take a turn in a round robin fashion.
    team = RoundRobinGroupChat(
        participants=[interviewer,candidate,career_coach],
        termination_condition=TextMentionTermination(text="TERMINATE"),
        max_turns=20
    )
    return team

async def  interview(team):
    # run the interview
    async for message in team.run_stream(task="Start the interview with the first question?"):
        if isinstance(message,TaskResult):
            msg= f'Interview completed with result: {message.stop_reason}'
            yield msg
        else:
            msg= f'{message.source}: {message.content}'
            yield msg