# API 參考

## `src.DeepSearchAgent`

主要的代理類別，提供完整的深度搜尋研究功能。

### 建構式

```python
DeepSearchAgent(config: Optional[Config] = None)
```

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `config` | `Config \| None` | `None` | 組態物件。若為 `None` 則自動呼叫 `load_config()` |

### 公開方法

#### `research(query, save_report=True) -> str`

執行完整的深度研究流程。

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `query` | `str` | — | 研究查詢 |
| `save_report` | `bool` | `True` | 是否儲存報告至檔案 |

**回傳**：最終 Markdown 報告字串。

**例外**：研究過程中的任何錯誤會被捕獲後重新拋出。

#### `get_progress_summary() -> Dict[str, Any]`

回傳研究進度摘要。

```python
{
    "total_paragraphs": int,
    "completed_paragraphs": int,
    "progress_percentage": float,  # 0.0 ~ 100.0
    "is_completed": bool,
    "created_at": str,   # ISO 格式
    "updated_at": str
}
```

#### `load_state(filepath: str) -> None`

從 JSON 檔案載入先前儲存的研究狀態。

#### `save_state(filepath: str) -> None`

將目前研究狀態儲存為 JSON 檔案。

### 公開屬性

| 屬性 | 型別 | 說明 |
|------|------|------|
| `config` | `Config` | 組態物件 |
| `llm_client` | `BaseLLM` | LLM 客戶端實例 |
| `state` | `State` | 目前研究狀態 |

---

## `src.Config`

組態管理類別。

### 建構式

```python
Config(
    deepseek_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    tavily_api_key: Optional[str] = None,
    default_llm_provider: str = "deepseek",
    deepseek_model: str = "deepseek-chat",
    openai_model: str = "gpt-4o-mini",
    max_search_results: int = 3,
    search_timeout: int = 240,
    max_content_length: int = 20000,
    max_reflections: int = 2,
    max_paragraphs: int = 5,
    output_dir: str = "reports",
    save_intermediate_states: bool = True
)
```

### 方法

#### `validate() -> bool`
驗證必要的 API 金鑰是否已設定。

#### `Config.from_file(config_file: str) -> Config`（類別方法）
從 `.py` 或 `.env` 格式的組態檔建立 Config。

### 參數說明

| 參數 | 說明 | 建議範圍 |
|------|------|---------|
| `max_reflections` | 每個段落的反思迴圈次數 | 1~5，越大品質越好但越慢 |
| `max_search_results` | 每次搜尋回傳的結果數 | 1~10，建議 3~5 |
| `max_content_length` | 搜尋結果內容截斷長度 | 5000~50000 |
| `max_paragraphs` | 報告最大段落數 | 由 Prompt 控制（目前為 5） |
| `search_timeout` | 搜尋超時秒數 | 60~600 |

---

## `src.load_config`

```python
load_config(config_file: Optional[str] = None) -> Config
```

載入組態。自動搜尋 `config.py` → `config.env` → `.env`，並執行 `validate()`。

---

## `src.create_agent`

```python
create_agent(config_file: Optional[str] = None) -> DeepSearchAgent
```

便捷函式，等同於 `DeepSearchAgent(load_config(config_file))`。

---

## LLM 類別

### `src.llms.BaseLLM`（抽象類別）

| 方法 | 說明 |
|------|------|
| `invoke(system_prompt, user_prompt, **kwargs) -> str` | 呼叫 LLM [抽象] |
| `get_default_model() -> str` | 取得預設模型名稱 [抽象] |
| `validate_response(response) -> str` | 清理回應（去空白） |

### `src.llms.DeepSeekLLM`

| 參數 / 方法 | 說明 |
|-------------|------|
| `__init__(api_key=None, model_name=None)` | 回退至 `DEEPSEEK_API_KEY` 環境變數 |
| `invoke(system_prompt, user_prompt, **kwargs)` | `temperature`=0.7, `max_tokens`=4000 |
| `get_model_info() -> Dict` | 回傳 `{provider, model, api_base}` |

### `src.llms.OpenAILLM`

介面同上，回退至 `OPENAI_API_KEY` 環境變數。

---

## 狀態類別

### `src.state.State`

| 方法 | 說明 |
|------|------|
| `add_paragraph(title, content) -> int` | 新增段落，回傳索引 |
| `get_paragraph(index) -> Paragraph \| None` | 取得段落 |
| `get_progress_summary() -> Dict` | 進度摘要 |
| `mark_completed()` | 標記完成 |
| `to_dict() / from_dict(data)` | 序列化 |
| `to_json(indent=2) / from_json(json_str)` | JSON 序列化 |
| `save_to_file(filepath) / load_from_file(filepath)` | 檔案讀寫 |

### `src.state.Paragraph`

| 屬性 / 方法 | 說明 |
|-------------|------|
| `title: str` | 段落標題 |
| `content: str` | 預期內容描述 |
| `research: Research` | 研究進度 |
| `order: int` | 排序 |
| `is_completed() -> bool` | 是否完成 |
| `get_final_content() -> str` | 取得最終內容 |

### `src.state.Research`

| 屬性 / 方法 | 說明 |
|-------------|------|
| `search_history: List[Search]` | 搜尋紀錄 |
| `latest_summary: str` | 當前摘要 |
| `reflection_iteration: int` | 反思次數 |
| `is_completed: bool` | 是否完成 |
| `add_search_results(query, results)` | 批次新增 |
| `increment_reflection()` | 反思計數 +1 |
| `mark_completed()` | 標記完成 |

### `src.state.Search`

| 屬性 | 型別 | 說明 |
|------|------|------|
| `query` | `str` | 搜尋查詢 |
| `url` | `str` | 結果連結 |
| `title` | `str` | 結果標題 |
| `content` | `str` | 結果內容 |
| `score` | `float \| None` | 相關度評分 |
| `timestamp` | `str` | 時間戳 |

---

## 搜尋工具

### `src.tools.tavily_search`

```python
tavily_search(
    query: str,
    max_results: int = 5,
    include_raw_content: bool = True,
    timeout: int = 240,
    api_key: Optional[str] = None
) -> List[Dict[str, Any]]
```

回傳格式：`[{"title": str, "url": str, "content": str, "score": float|None}]`

---

## 文字處理工具

### `src.utils.text_processing`

| 函式 | 簽名 | 說明 |
|------|------|------|
| `clean_json_tags` | `(text: str) -> str` | 移除 ```json 標記 |
| `clean_markdown_tags` | `(text: str) -> str` | 移除 ```markdown 標記 |
| `remove_reasoning_from_output` | `(text: str) -> str` | 移除 LLM 推理文字 |
| `extract_clean_response` | `(text: str) -> Dict` | 多策略提取 JSON |
| `format_search_results_for_prompt` | `(results, max_length) -> List[str]` | 格式化搜尋結果 |
| `truncate_content` | `(content, max_length=20000) -> str` | 截斷文字 |
