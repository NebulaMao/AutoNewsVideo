"""
AutoVideo - 自动化每日新闻视频生成工具

主要功能：
- 支持自定义LLM（通过OpenAI标准接口）
- 从新闻数据生成JSON格式化数据
- 通过HTML模板生成图片
- TTS语音合成
- FFMPEG视频生成

使用方法：
1. 安装依赖：pip install -e .
2. 配置环境变量或修改配置文件
3. 运行：python main.py
"""

from .autovideo import AutoVideoGenerator
from .config import Config

__version__ = "0.1.0"
__all__ = ["AutoVideoGenerator", "Config"]