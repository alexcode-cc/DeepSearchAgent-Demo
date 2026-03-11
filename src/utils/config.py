"""
配置管理模块
处理 TOML / Python / .env 配置文件和环境变量
"""

import os
import sys
from dataclasses import dataclass
from typing import Optional

# Python 3.11+ 内建 tomllib，旧版本使用 tomli
try:
    import tomllib
except ModuleNotFoundError:
    try:
        import tomli as tomllib
    except ModuleNotFoundError:
        tomllib = None


@dataclass
class Config:
    """配置类"""
    # API密钥
    deepseek_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None

    # 模型配置
    default_llm_provider: str = "deepseek"  # deepseek, openai 或 ollama
    deepseek_model: str = "deepseek-chat"
    openai_model: str = "gpt-4o-mini"
    ollama_model: str = "llama3"
    ollama_base_url: str = "http://localhost:11434/v1"

    # 搜索配置
    max_search_results: int = 3
    search_timeout: int = 240
    max_content_length: int = 20000

    # Agent配置
    max_reflections: int = 2
    max_paragraphs: int = 5

    # 输出配置
    output_dir: str = "reports"
    save_intermediate_states: bool = True

    def validate(self) -> bool:
        """验证配置"""
        if self.default_llm_provider == "deepseek" and not self.deepseek_api_key:
            print("错误: DeepSeek API Key未设置")
            return False

        if self.default_llm_provider == "openai" and not self.openai_api_key:
            print("错误: OpenAI API Key未设置")
            return False

        # Ollama 本地服务不需要 LLM API Key

        if not self.tavily_api_key:
            print("错误: Tavily API Key未设置")
            return False

        return True

    # ------------------------------------------------------------------
    # 从 TOML 文件加载
    # ------------------------------------------------------------------
    @classmethod
    def from_toml(cls, config_file: str) -> "Config":
        """从 TOML 配置文件创建配置"""
        if tomllib is None:
            raise ImportError(
                "需要 tomli 库来读取 TOML 文件。"
                "请执行: pip install tomli"
            )

        with open(config_file, "rb") as f:
            data = tomllib.load(f)

        secrets = data.get("secrets", {})
        llm = data.get("llm", {})
        search = data.get("search", {})
        agent = data.get("agent", {})
        output = data.get("output", {})

        # 过滤占位符值
        def _real_key(val: Optional[str]) -> Optional[str]:
            if val and not val.startswith("your_") and val not in ("", "None"):
                return val
            return None

        return cls(
            deepseek_api_key=_real_key(secrets.get("deepseek_api_key")),
            openai_api_key=_real_key(secrets.get("openai_api_key")),
            tavily_api_key=_real_key(secrets.get("tavily_api_key")),
            default_llm_provider=llm.get("default_provider", "deepseek"),
            deepseek_model=llm.get("deepseek", {}).get("model", "deepseek-chat"),
            openai_model=llm.get("openai", {}).get("model", "gpt-4o-mini"),
            ollama_model=llm.get("ollama", {}).get("model", "llama3"),
            ollama_base_url=llm.get("ollama", {}).get("base_url", "http://localhost:11434/v1"),
            max_search_results=search.get("max_results", 3),
            search_timeout=search.get("timeout", 240),
            max_content_length=search.get("max_content_length", 20000),
            max_reflections=agent.get("max_reflections", 2),
            max_paragraphs=agent.get("max_paragraphs", 5),
            output_dir=output.get("dir", "reports"),
            save_intermediate_states=output.get("save_intermediate_states", True),
        )

    # ------------------------------------------------------------------
    # 从 Python 或 .env 文件加载（向后兼容）
    # ------------------------------------------------------------------
    @classmethod
    def from_file(cls, config_file: str) -> "Config":
        """从配置文件创建配置（自动识别格式）"""
        if config_file.endswith('.toml'):
            return cls.from_toml(config_file)

        if config_file.endswith('.py'):
            # Python配置文件
            import importlib.util

            spec = importlib.util.spec_from_file_location("config", config_file)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)

            return cls(
                deepseek_api_key=getattr(config_module, "DEEPSEEK_API_KEY", None),
                openai_api_key=getattr(config_module, "OPENAI_API_KEY", None),
                tavily_api_key=getattr(config_module, "TAVILY_API_KEY", None),
                default_llm_provider=getattr(config_module, "DEFAULT_LLM_PROVIDER", "deepseek"),
                deepseek_model=getattr(config_module, "DEEPSEEK_MODEL", "deepseek-chat"),
                openai_model=getattr(config_module, "OPENAI_MODEL", "gpt-4o-mini"),
                ollama_model=getattr(config_module, "OLLAMA_MODEL", "llama3"),
                ollama_base_url=getattr(config_module, "OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                max_search_results=getattr(config_module, "SEARCH_RESULTS_PER_QUERY", 3),
                search_timeout=getattr(config_module, "SEARCH_TIMEOUT", 240),
                max_content_length=getattr(config_module, "SEARCH_CONTENT_MAX_LENGTH", 20000),
                max_reflections=getattr(config_module, "MAX_REFLECTIONS", 2),
                max_paragraphs=getattr(config_module, "MAX_PARAGRAPHS", 5),
                output_dir=getattr(config_module, "OUTPUT_DIR", "reports"),
                save_intermediate_states=getattr(config_module, "SAVE_INTERMEDIATE_STATES", True)
            )
        else:
            # .env格式配置文件
            config_dict = {}

            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config_dict[key.strip()] = value.strip()

            return cls(
                deepseek_api_key=config_dict.get("DEEPSEEK_API_KEY"),
                openai_api_key=config_dict.get("OPENAI_API_KEY"),
                tavily_api_key=config_dict.get("TAVILY_API_KEY"),
                default_llm_provider=config_dict.get("DEFAULT_LLM_PROVIDER", "deepseek"),
                deepseek_model=config_dict.get("DEEPSEEK_MODEL", "deepseek-chat"),
                openai_model=config_dict.get("OPENAI_MODEL", "gpt-4o-mini"),
                ollama_model=config_dict.get("OLLAMA_MODEL", "llama3"),
                ollama_base_url=config_dict.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                max_search_results=int(config_dict.get("SEARCH_RESULTS_PER_QUERY", "3")),
                search_timeout=int(config_dict.get("SEARCH_TIMEOUT", "240")),
                max_content_length=int(config_dict.get("SEARCH_CONTENT_MAX_LENGTH", "20000")),
                max_reflections=int(config_dict.get("MAX_REFLECTIONS", "2")),
                max_paragraphs=int(config_dict.get("MAX_PARAGRAPHS", "5")),
                output_dir=config_dict.get("OUTPUT_DIR", "reports"),
                save_intermediate_states=config_dict.get("SAVE_INTERMEDIATE_STATES", "true").lower() == "true"
            )


def load_config(config_file: Optional[str] = None) -> Config:
    """
    加载配置

    优先级: 指定路径 > config.toml > config.py > config.env > .env

    Args:
        config_file: 配置文件路径，如果不指定则按优先级自动搜索

    Returns:
        配置对象
    """
    if config_file:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        file_to_load = config_file
    else:
        # 按优先级搜索配置文件
        for config_path in ["config.toml", "config.py", "config.env", ".env"]:
            if os.path.exists(config_path):
                file_to_load = config_path
                print(f"已找到配置文件: {config_path}")
                break
        else:
            raise FileNotFoundError(
                "未找到配置文件，请复制 config-sample.toml 为 config.toml 并填入 API 密钥"
            )

    config = Config.from_file(file_to_load)

    if not config.validate():
        raise ValueError("配置验证失败，请检查配置文件中的API密钥")

    return config


def print_config(config: Config):
    """打印配置信息（隐藏敏感信息）"""
    print("\n=== 当前配置 ===")
    print(f"LLM提供商: {config.default_llm_provider}")
    print(f"DeepSeek模型: {config.deepseek_model}")
    print(f"OpenAI模型: {config.openai_model}")
    print(f"Ollama模型: {config.ollama_model}")
    print(f"Ollama服务地址: {config.ollama_base_url}")
    print(f"最大搜索结果数: {config.max_search_results}")
    print(f"搜索超时: {config.search_timeout}秒")
    print(f"最大内容长度: {config.max_content_length}")
    print(f"最大反思次数: {config.max_reflections}")
    print(f"最大段落数: {config.max_paragraphs}")
    print(f"输出目录: {config.output_dir}")
    print(f"保存中间状态: {config.save_intermediate_states}")

    # 显示API密钥状态（不显示实际密钥）
    print(f"DeepSeek API Key: {'已设置' if config.deepseek_api_key else '未设置'}")
    print(f"OpenAI API Key: {'已设置' if config.openai_api_key else '未设置'}")
    print(f"Tavily API Key: {'已设置' if config.tavily_api_key else '未设置'}")
    print("==================\n")
