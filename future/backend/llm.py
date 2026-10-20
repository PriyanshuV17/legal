from langchain_community.llms import Ollama
import logging

logger = logging.getLogger(__name__)

def get_llm():
    try:
        return Ollama(
            model="phi3",
            base_url="http://localhost:11434",
            timeout=5.0
        )
    except Exception as e:
        logger.warning(f"Failed to initialize Ollama: {e}")
        return None