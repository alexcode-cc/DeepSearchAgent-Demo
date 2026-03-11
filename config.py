# Deep Search Agent 配置文件（向后兼容）
#
# *** 推荐使用 config.toml 管理配置 ***
# 复制 config-sample.toml 为 config.toml 并填入 API 密钥即可。
# 当 config.toml 存在时，本文件会被忽略。
#
# 如果仍需使用本文件，请在下方填入 API 密钥。

# API 密钥 — 请改用 config.toml 的 [secrets] 区段存放
DEEPSEEK_API_KEY = ""
OPENAI_API_KEY = ""
TAVILY_API_KEY = ""

# 配置参数
DEFAULT_LLM_PROVIDER = "deepseek"  # deepseek, openai 或 ollama
DEEPSEEK_MODEL = "deepseek-chat"
OPENAI_MODEL = "gpt-4o-mini"

# Ollama 配置（本地模型）
OLLAMA_MODEL = "llama3"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

MAX_REFLECTIONS = 2
SEARCH_RESULTS_PER_QUERY = 3
SEARCH_CONTENT_MAX_LENGTH = 20000
OUTPUT_DIR = "reports"
SAVE_INTERMEDIATE_STATES = True
