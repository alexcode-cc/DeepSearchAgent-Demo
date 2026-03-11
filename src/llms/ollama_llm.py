"""
Ollama LLM实现
支持通过Ollama运行本地模型，使用OpenAI兼容API
"""

import os
from typing import Optional, Dict, Any
from openai import OpenAI
from .base import BaseLLM


class OllamaLLM(BaseLLM):
    """Ollama LLM实现类，用于连接本地或远程Ollama服务"""

    def __init__(
        self,
        model_name: Optional[str] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        初始化Ollama客户端

        Args:
            model_name: 模型名称（如 llama3, qwen2, mistral 等），
                        如果不提供则从环境变量 OLLAMA_MODEL 读取，
                        仍无则使用默认值
            base_url: Ollama服务地址，默认 http://localhost:11434/v1，
                      也可通过环境变量 OLLAMA_BASE_URL 设置
            api_key: API密钥，Ollama本地服务不需要，传入占位值即可
        """
        # Ollama 本地服务不需要真实 API key，但 OpenAI SDK 要求非空
        resolved_key = api_key or os.getenv("OLLAMA_API_KEY", "ollama")
        super().__init__(resolved_key, model_name)

        self.base_url = (
            base_url
            or os.getenv("OLLAMA_BASE_URL")
            or "http://localhost:11434/v1"
        )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
        )

        self.default_model = model_name or os.getenv("OLLAMA_MODEL") or self.get_default_model()

    def get_default_model(self) -> str:
        """获取默认模型名称"""
        return "llama3"

    def invoke(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        """
        调用Ollama API生成回复

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户输入
            **kwargs: 其他参数，如temperature、max_tokens等

        Returns:
            模型生成的回复文本
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            params = {
                "model": self.default_model,
                "messages": messages,
                "temperature": kwargs.get("temperature", 0.7),
                "stream": False,
            }

            # Ollama 部分模型不支持 max_tokens，改用 num_predict（通过 options）
            # 但 OpenAI 兼容端点支持 max_tokens，所以仍然传入
            max_tokens = kwargs.get("max_tokens")
            if max_tokens is not None:
                params["max_tokens"] = max_tokens

            response = self.client.chat.completions.create(**params)

            if response.choices and response.choices[0].message:
                content = response.choices[0].message.content
                return self.validate_response(content)
            else:
                return ""

        except Exception as e:
            print(f"Ollama API调用错误: {str(e)}")
            raise e

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取当前模型信息

        Returns:
            模型信息字典
        """
        return {
            "provider": "Ollama",
            "model": self.default_model,
            "api_base": self.base_url,
        }
