# Ollama 支援設定指南

本指南說明如何使用 Ollama 在本機（或遠端伺服器）執行自架模型，並將其整合至 Deep Search Agent。

---

## 目錄

1. [Ollama 簡介](#1-ollama-簡介)
2. [安裝 Ollama](#2-安裝-ollama)
3. [下載與管理模型](#3-下載與管理模型)
4. [設定 Deep Search Agent 使用 Ollama](#4-設定-deep-search-agent-使用-ollama)
5. [在 Ollama 與 OpenAI 之間切換](#5-在-ollama-與-openai-之間切換)
6. [Streamlit Web 介面操作](#6-streamlit-web-介面操作)
7. [程式碼方式動態切換](#7-程式碼方式動態切換)
8. [架構隔離說明](#8-架構隔離說明)
9. [進階設定](#9-進階設定)
10. [常見問題排除](#10-常見問題排除)

---

## 1. Ollama 簡介

[Ollama](https://ollama.com/) 是一個開源的本地 LLM 執行工具，讓你能在自己的機器上運行 Llama 3、Qwen 2、Mistral、Gemma 等開源模型，**完全免費、資料不離開本機**。

Ollama 提供 OpenAI 相容的 REST API（`/v1/chat/completions`），因此本專案可直接使用 `openai` Python SDK 與其通訊，無需額外依賴。

### 使用 Ollama 的優勢

- **隱私**：所有資料在本機處理，不經過任何第三方服務
- **免費**：無 API 呼叫費用，僅需本機硬體資源
- **離線可用**：模型下載後可完全離線運行（搜尋功能仍需網路）
- **靈活**：可隨時切換不同開源模型

---

## 2. 安裝 Ollama

### Windows

從官網下載安裝程式：

```bash
# 或使用 winget
winget install Ollama.Ollama
```

### macOS

```bash
brew install ollama
```

### Linux

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 驗證安裝

安裝完成後啟動 Ollama 服務：

```bash
ollama serve
```

確認服務運行中（預設監聽 `http://localhost:11434`）：

```bash
curl http://localhost:11434/v1/models
```

> **注意**：Windows 安裝後 Ollama 通常會自動以背景服務啟動，無需手動執行 `ollama serve`。

---

## 3. 下載與管理模型

### 下載模型

```bash
# 推薦的模型（依硬體能力選擇）
ollama pull llama3          # Meta Llama 3 8B（建議至少 8GB RAM）
ollama pull llama3:70b      # Meta Llama 3 70B（建議至少 48GB RAM）
ollama pull qwen2           # 阿里 Qwen 2 7B（中文能力優秀）
ollama pull qwen2:72b       # 阿里 Qwen 2 72B
ollama pull mistral         # Mistral 7B
ollama pull gemma2          # Google Gemma 2 9B
ollama pull deepseek-r1     # DeepSeek R1（推理能力強）
```

### 確認已下載的模型

```bash
ollama list
```

輸出範例：

```
NAME              ID            SIZE     MODIFIED
llama3:latest     a6990ed6be41  4.7 GB   2 hours ago
qwen2:latest      e0d4e1163c58  4.4 GB   1 hour ago
```

### 快速測試模型

```bash
ollama run llama3 "你好，請用繁體中文回答"
```

### 模型選擇建議

| 模型 | 參數量 | 最低 RAM | 中文能力 | 推薦用途 |
|------|--------|---------|---------|---------|
| `qwen2` | 7B | 8GB | 優秀 | **中文研究報告首選** |
| `qwen2:72b` | 72B | 48GB | 極佳 | 高品質中文報告 |
| `llama3` | 8B | 8GB | 普通 | 英文研究、通用任務 |
| `llama3:70b` | 70B | 48GB | 良好 | 高品質英文報告 |
| `mistral` | 7B | 8GB | 普通 | 輕量快速 |
| `deepseek-r1` | 7B | 8GB | 優秀 | 需要推理能力的研究 |

> **提示**：本專案的 Prompt 以中文撰寫，建議優先選擇中文能力較強的模型（如 `qwen2` 系列）。

---

## 4. 設定 Deep Search Agent 使用 Ollama

### 方式一：修改 config.py（推薦）

編輯專案根目錄的 `config.py`：

```python
# === 切換至 Ollama ===
DEFAULT_LLM_PROVIDER = "ollama"

# Ollama 設定
OLLAMA_MODEL = "qwen2"                          # 使用已下載的模型名稱
OLLAMA_BASE_URL = "http://localhost:11434/v1"    # Ollama 服務位址

# Tavily 搜尋仍需要 API Key（搜尋功能與 LLM 無關）
TAVILY_API_KEY = "your_tavily_api_key_here"

# 以下設定在使用 Ollama 時不會用到，但保留不影響
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
OPENAI_API_KEY = "your_openai_api_key_here"
DEEPSEEK_MODEL = "deepseek-chat"
OPENAI_MODEL = "gpt-4o-mini"
```

然後直接執行：

```bash
python examples/basic_usage.py
```

### 方式二：環境變數

```bash
export OLLAMA_MODEL="qwen2"
export OLLAMA_BASE_URL="http://localhost:11434/v1"
```

### 方式三：程式碼內建立 Config

```python
from src import DeepSearchAgent, Config

config = Config(
    default_llm_provider="ollama",
    ollama_model="qwen2",
    ollama_base_url="http://localhost:11434/v1",
    tavily_api_key="your_tavily_key",
)

agent = DeepSearchAgent(config)
report = agent.research("2025年人工智慧發展趨勢")
```

---

## 5. 在 Ollama 與 OpenAI 之間切換

切換 LLM 後端**只需修改 `DEFAULT_LLM_PROVIDER` 一個欄位**，其餘設定互不干擾。

### config.py 切換範例

所有 provider 的設定可以**同時保留**在 config.py 中，系統只會讀取當前 provider 對應的欄位：

```python
# ===== 切換開關（只需修改這一行）=====
DEFAULT_LLM_PROVIDER = "ollama"    # "deepseek" | "openai" | "ollama"

# ----- DeepSeek 設定（provider="deepseek" 時使用）-----
DEEPSEEK_API_KEY = "sk-xxxxxxxxxxxxxxxx"
DEEPSEEK_MODEL = "deepseek-chat"

# ----- OpenAI 設定（provider="openai" 時使用）-----
OPENAI_API_KEY = "sk-xxxxxxxxxxxxxxxx"
OPENAI_MODEL = "gpt-4o-mini"

# ----- Ollama 設定（provider="ollama" 時使用）-----
OLLAMA_MODEL = "qwen2"
OLLAMA_BASE_URL = "http://localhost:11434/v1"

# ----- 共用設定（所有 provider 都會使用）-----
TAVILY_API_KEY = "tvly-xxxxxxxxxxxxxxxx"
MAX_REFLECTIONS = 2
SEARCH_RESULTS_PER_QUERY = 3
SEARCH_CONTENT_MAX_LENGTH = 20000
OUTPUT_DIR = "reports"
SAVE_INTERMEDIATE_STATES = True
```

**切換方式**：只需將 `DEFAULT_LLM_PROVIDER` 改為 `"openai"` 或 `"deepseek"` 即可，無需修改或刪除任何其他設定。

### 切換對照表

| 動作 | 修改內容 |
|------|---------|
| Ollama → OpenAI | `DEFAULT_LLM_PROVIDER = "openai"` |
| OpenAI → Ollama | `DEFAULT_LLM_PROVIDER = "ollama"` |
| Ollama → DeepSeek | `DEFAULT_LLM_PROVIDER = "deepseek"` |
| 換 Ollama 模型 | 修改 `OLLAMA_MODEL`（如 `"llama3"` → `"qwen2"`） |
| 連遠端 Ollama | 修改 `OLLAMA_BASE_URL`（如 `"http://192.168.1.100:11434/v1"`） |

---

## 6. Streamlit Web 介面操作

啟動 Web 介面：

```bash
streamlit run examples/streamlit_app.py
```

### 使用 Ollama

1. 在左側欄「LLM提供商」下拉選單中選擇 **ollama**
2. 填入「Ollama模型名称」（如 `qwen2`）
3. 確認「Ollama服务地址」（預設 `http://localhost:11434/v1`）
4. 填入「Tavily API Key」
5. **不需要**填寫 DeepSeek / OpenAI API Key
6. 輸入研究查詢，點擊「開始研究」

### 切換回 OpenAI

1. 將「LLM提供商」改為 **openai**
2. 填入「OpenAI API Key」
3. 選擇 OpenAI 模型
4. 其他設定不變，直接使用

> 介面中各 provider 的設定欄位會**動態顯示/隱藏**，不會互相影響。

---

## 7. 程式碼方式動態切換

在同一程式中建立不同 provider 的 Agent，可用於比較輸出品質：

```python
from src import DeepSearchAgent, Config

# 共用設定
common = dict(
    tavily_api_key="your_tavily_key",
    max_reflections=2,
    max_search_results=3,
)

# Ollama Agent
ollama_config = Config(
    default_llm_provider="ollama",
    ollama_model="qwen2",
    **common,
)
ollama_agent = DeepSearchAgent(ollama_config)

# OpenAI Agent
openai_config = Config(
    default_llm_provider="openai",
    openai_api_key="sk-xxxxxxxx",
    openai_model="gpt-4o-mini",
    **common,
)
openai_agent = DeepSearchAgent(openai_config)

# 同一查詢，不同模型
query = "量子計算的最新進展"
ollama_report = ollama_agent.research(query)
openai_report = openai_agent.research(query)
```

兩個 Agent 實例**完全獨立**，各自持有自己的 LLM 客戶端與狀態物件。

---

## 8. 架構隔離說明

以下說明為何 Ollama 與 OpenAI 的設定不會互相衝突。

### 組態層隔離

`Config` dataclass 中，各 provider 的欄位完全分離：

```
Config
├── deepseek_api_key / deepseek_model          ← DeepSeek 專用
├── openai_api_key / openai_model              ← OpenAI 專用
├── ollama_model / ollama_base_url             ← Ollama 專用
├── default_llm_provider                        ← 切換開關
└── tavily_api_key / max_reflections / ...      ← 所有 provider 共用
```

### 初始化隔離

`DeepSearchAgent._initialize_llm()` 使用 `if/elif` 分支，每個分支只讀取對應欄位：

```python
if provider == "deepseek":
    return DeepSeekLLM(api_key=config.deepseek_api_key, ...)   # 不碰 ollama_*
elif provider == "openai":
    return OpenAILLM(api_key=config.openai_api_key, ...)       # 不碰 ollama_*
elif provider == "ollama":
    return OllamaLLM(model_name=config.ollama_model, ...)      # 不碰 openai_*
```

### SDK 實例隔離

雖然 `OllamaLLM` 和 `OpenAILLM` 都使用 `openai.OpenAI` SDK，但各自建立**獨立的 client 實例**：

| 類別 | `api_key` | `base_url` |
|------|-----------|-----------|
| `OpenAILLM` | 用戶的 OpenAI API Key | `https://api.openai.com`（SDK 預設） |
| `OllamaLLM` | `"ollama"`（佔位值） | `http://localhost:11434/v1` |

兩個 client 不共享任何狀態，呼叫完全獨立。

### 驗證邏輯隔離

`Config.validate()` 依 provider 決定需要哪些金鑰：

- `provider="openai"` → 要求 `openai_api_key` 非空
- `provider="ollama"` → **跳過** LLM 金鑰驗證（本地服務不需要）
- 所有 provider → 都要求 `tavily_api_key`（搜尋功能與 LLM 無關）

---

## 9. 進階設定

### 連接遠端 Ollama 伺服器

若 Ollama 執行在另一台機器上：

```python
OLLAMA_BASE_URL = "http://192.168.1.100:11434/v1"
```

需確保遠端 Ollama 設定了 `OLLAMA_HOST=0.0.0.0`：

```bash
# 在遠端機器上
OLLAMA_HOST=0.0.0.0 ollama serve
```

### 調整生成參數

在程式碼中可透過 `kwargs` 傳遞參數給 Ollama：

```python
# 在自訂節點中呼叫時可調整
response = llm_client.invoke(
    system_prompt="...",
    user_prompt="...",
    temperature=0.3,     # 降低隨機性，提高一致性
    max_tokens=8000,     # 增加輸出長度上限
)
```

### 搭配 GPU 加速

Ollama 自動偵測 NVIDIA GPU。確認 GPU 是否被使用：

```bash
ollama ps
```

若要強制使用 CPU：

```bash
CUDA_VISIBLE_DEVICES="" ollama serve
```

### 多模型同時使用

Ollama 支援同時載入多個模型。可在不同研究任務中使用不同模型：

```python
# 用 qwen2 做結構規劃（中文能力強）
structure_config = Config(
    default_llm_provider="ollama",
    ollama_model="qwen2",
    tavily_api_key="...",
)

# 用 deepseek-r1 做深度分析（推理能力強）
analysis_config = Config(
    default_llm_provider="ollama",
    ollama_model="deepseek-r1",
    tavily_api_key="...",
)
```

---

## 10. 常見問題排除

### Q: 出現 "Connection refused" 錯誤

**原因**：Ollama 服務未啟動。

**解法**：
```bash
# 啟動服務
ollama serve

# 確認是否正在運行
curl http://localhost:11434/v1/models
```

Windows 用戶：檢查系統匣是否有 Ollama 圖示，或在「服務」中確認 Ollama 服務已啟動。

### Q: 出現 "model not found" 錯誤

**原因**：指定的模型尚未下載。

**解法**：
```bash
# 查看已下載的模型
ollama list

# 下載缺少的模型
ollama pull qwen2
```

### Q: 回應品質不如 OpenAI

**建議**：

1. 換用較大的模型（如 `qwen2:72b`）
2. 降低 `temperature`（如 0.3）以提高輸出穩定性
3. 增加 `max_reflections` 以補償模型能力差距
4. 若硬體允許，使用 `deepseek-r1` 獲得更好的推理品質

### Q: 生成速度很慢

**建議**：

1. 確認 GPU 是否被正確使用（`ollama ps` 查看）
2. 改用較小的模型（如 7B 而非 70B）
3. 減少 `max_reflections`（如從 2 降至 1）
4. 減少 `max_search_results`（減少需要處理的文字量）

### Q: JSON 解析頻繁失敗

**原因**：部分小型模型遵循 JSON 格式指令的能力較弱。

**建議**：

1. 換用較大或指令微調過的模型
2. 系統已有多層 JSON 容錯機制（正則提取、預設值回退），多數情況下不會中斷流程
3. 若仍有問題，可在 `src/prompts/prompts.py` 中為 Prompt 加上更明確的格式範例

### Q: 切換回 OpenAI 後出現錯誤

**確認事項**：

1. `DEFAULT_LLM_PROVIDER` 是否已改為 `"openai"`
2. `OPENAI_API_KEY` 是否填入有效金鑰
3. Ollama 相關設定**不需要刪除**，放著不會影響 OpenAI 運作

### Q: 可以同時保留所有 provider 的設定嗎？

**可以。** config.py 中可以同時填寫 DeepSeek、OpenAI、Ollama 的所有設定。系統只會根據 `DEFAULT_LLM_PROVIDER` 的值使用對應的欄位，其餘欄位會被忽略。這是刻意的設計，方便用戶隨時切換。
