from haystack.components.generators import OpenAIGenerator
from haystack.utils import Secret

from app.config import app_config

llm_generator = OpenAIGenerator(
    api_key=Secret.from_token(str(app_config.OPENAI_API_KEY.get_secret_value())),
    api_base_url=app_config.OPENAI_API_BASE_URL,
    model=app_config.PIPELINE_CONFIG.LLM_MODEL,
    system_prompt=app_config.PIPELINE_CONFIG.LLM_SYSTEM_PROMPT,
    generation_kwargs={
        "temperature": 0,
    },
)