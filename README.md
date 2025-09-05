# AutoVideo - 自动视频生成器

AutoVideo 是一个自动生成新闻视频的工具，支持从新闻源自动生成视频内容。

## 主要特性

- **自动新闻获取**: 通过 WYTA API 获取新闻内容
- **智能字幕生成**: 自动生成语音字幕
- **高质量语音**: 使用 TTS 技术生成自然语音
- **多模型支持**: 支持 LLM 和 TTS 多种模型
- **易于使用**: 简单的配置和使用流程

## 快速开始

### 系统要求

- Python 3.13+
- 查看 `pyproject.toml` 依赖

### 安装

1. 克隆项目:
```bash
git clone <repository-url>
cd autovideo
```

2. 安装依赖:
```bash
uv sync
```

3. 配置环境:
```bash
cp .env.example .env
# 编辑 .env 文件设置相关 API 密钥
```

### 运行项目

```bash
python main.py
```

工作流程:
1. 通过 WYTA API 获取新闻
2. 使用 LLM 生成字幕
3. 将文字转换为语音
4. 生成图片素材
5. 合成最终视频

## 环境配置

### 必需配置

(在 `.env` 文件中配置以下参数):

```env
# LLM配置
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=https://api.siliconflow.cn/v1  # 使用的 LLM 服务
LLM_MODEL=deepseek-ai/DeepSeek-V3
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000

# 语音合成配置
TTS_PROVIDER=siliconflow  # 可选: edge_tts, siliconflow
TTS_VOICE=FunAudioLLM/CosyVoice2-0.5B:alex
TTS_RATE=+0%
TTS_VOLUME=+0%

# 新闻 API 配置
WHYTA_API_KEY=your_whyta_api_key

# SiliconFlow TTS 配置 (当 TTS_PROVIDER=siliconflow 时需要)
TTS_API_KEY=your_tts_api_key
TTS_BASE_URL=https://api.siliconflow.cn/v1
TTS_MODEL=FunAudioLLM/CosyVoice2-0.5B
```

### 支持服务

#### 语言模型 (LLM)
- OpenAI GPT 系列
- DeepSeek
- 其他兼容 OpenAI API 的服务

#### 语音合成 (TTS)
- **Edge TTS**: 免费在线语音服务
- **SiliconFlow**: 高质量商业语音服务

#### 新闻源
- **WYTA API**: 免费新闻聚合 API

## 项目结构

```
autovideo/
├── autovideo/
│   ├── __init__.py
│   ├── autovideo.py         # 主要视频生成类
│   ├── config.py            # 配置管理
│   ├── llm_client.py        # LLM 客户端
│   ├── tts_generator.py     # TTS 生成器
│   ├── html_to_image.py     # HTML 转图片
│   └── video_generator.py   # 视频生成器
├── main.py                  # 主程序入口
├── .env.example            # 环境变量模板
├── pyproject.toml          # 项目配置
├── requirements.txt        # 依赖列表
└── templates/              # HTML 模板文件
```

## 使用示例

### 自定义新闻源

```python
from autovideo.autovideo import AutoVideoGenerator
from autovideo.config import Config

def custom_news_fetcher():
    # 自定义新闻获取逻辑
    return [{"title": "新闻标题", "content": "新闻内容", ...}]

config = Config.from_env()
generator = AutoVideoGenerator(config)

video_path = generator.generate_news_video(
    news_data_fetcher=custom_news_fetcher,
    output_path="custom_video.mp4"
)
```

### 直接生成新闻视频

```python
news_items = [
    {
        "title": "新闻标题",
        "content": "新闻内容",
        "source": "新闻来源",
        "created_at": "2024-01-01 12:00:00"
    }
]

video_path = generator.generate_from_news_list(
    news_items=news_items,
    output_path="formatted_video.mp4"
)
```

## 配置参数

### 视频参数
- `width`: 视频宽度，默认 1920
- `height`: 视频高度，默认 1080
- `fps`: 帧率，默认 30
- `image_duration`: 图片显示时长，默认 5秒
- `transition_duration`: 转场时长，默认 0.5秒

### LLM 参数
- `temperature`: 生成温度，范围 0.0-1.0
- `max_tokens`: 最大生成令牌数

### TTS 参数
- `voice`: 语音选择
- `rate`: 语速，如 "+10%"
- `volume`: 音量，如 "+0%"

## 日志输出

### 日志级别

默认使用 Python logging 模块，级别为 INFO:
```python
import logging
logging.basicConfig(level=logging.INFO)
```

### 输出文件

生成的视频文件位于 `output/` 目录下:
- 新闻视频: `news_video_YYYYMMDD_HHMMSS.mp4`
- 其他文件: (根据具体功能)

## 常见问题

1. **API密钥问题**:
   - 检查 `.env` 文件中的 API 密钥是否正确
   - 确认账户余额和 API 调用权限

2. **网络问题**:
   - 确保网络连接稳定
   - 检查防火墙和代理设置

3. **生成问题**:
   - 检查输入数据格式是否正确
   - 视频: MP4 格式，兼容主流播放器

## 贡献指南

欢迎通过 Issues 和 Pull Requests 贡献代码

## 项目许可

本项目采用 MIT 许可证

## 更新日志

### 版本历史

1. **API 密钥配置**:
   - 在 `.env` 文件中配置 API 密钥和参数
   - 支持多种 API 服务

2. **功能完善**:
   - 完善新闻获取逻辑
   - 增加错误处理和日志记录

3. **依赖更新**:
   - 使用 `uv sync` 安装依赖
   - 更新 Python 版本要求

4. **性能优化**:
   - 优化图片生成速度
   - 改进视频合成质量

### 未来计划

后续计划包括:
1. 增加更多新闻源
2. 优化配置参数
3. 增加 Web 界面