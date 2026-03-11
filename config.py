# Deep Search Agent 配置文件
# 请在这里填入您的API密钥

# DeepSeek API Key
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"

# OpenAI API Key (可选)
OPENAI_API_KEY = "your_openai_api_key_here"

# Tavily搜索API Key
TAVILY_API_KEY = "your_tavily_api_key_here"

# 配置参数
DEFAULT_LLM_PROVIDER = "deepseek"  # deepseek, openai 或 ollama
DEEPSEEK_MODEL = "deepseek-chat"
OPENAI_MODEL = "gpt-4o-mini"

# Ollama配置（本地模型）
OLLAMA_MODEL = "llama3"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

MAX_REFLECTIONS = 2
SEARCH_RESULTS_PER_QUERY = 3
SEARCH_CONTENT_MAX_LENGTH = 20000
OUTPUT_DIR = "reports"
SAVE_INTERMEDIATE_STATES = True
