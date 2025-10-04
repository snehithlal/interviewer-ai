import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configuration settings for the interview agent"""

    # API Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    # Model settings (you can use either OpenAI or Anthropic)
    MODEL_PROVIDER = os.getenv("MODEL_PROVIDER", "openai")  # "openai" or "anthropic"
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4-turbo-preview")

    # Interview settings
    MAX_QUESTIONS = 10
    MAX_CONSECUTIVE_WRONG = 3  # End interview if 3 wrong in a row
    MIN_QUESTIONS = 3  # Ask at least 3 questions before ending

    # Output settings
    REPORTS_DIR = "outputs/reports"

    @classmethod
    def get_llm(cls):
        """Get the configured LLM instance"""
        if cls.MODEL_PROVIDER == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=cls.MODEL_NAME or "claude-3-5-sonnet-20241022",
                anthropic_api_key=cls.ANTHROPIC_API_KEY,
                temperature=0.7
            )
        else:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=cls.MODEL_NAME or "gpt-4-turbo-preview",
                openai_api_key=cls.OPENAI_API_KEY,
                temperature=0.7
            )


settings = Settings()