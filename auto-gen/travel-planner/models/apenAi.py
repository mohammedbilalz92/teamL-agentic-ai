from config.settings import OPENAI_API_KEY,MAX_TURN,TERMINATION_WORD
from autogen_ext.models.openai import OpenAIChatCompletionClient

model_client = OpenAIChatCompletionClient(
    model='MODEL',
    openai_api_key=OPENAI_API_KEY
)