#!/usr/bin/env python3
"""
AutoVideo - 自动化每日新闻视频生成工具
"""

import os
import sys
from typing import List, Dict, Any
from datetime import datetime
import html2text

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from autovideo.autovideo import AutoVideoGenerator
from autovideo.config import Config
import requests


def sample_news_data_fetcher(api_key: str = None) -> List[Dict[str, Any]]:
    """
    从API获取新闻数据，并为每条新闻添加raw_content字段
    """
    api_url = "https://whyta.cn/api/tx/generalnews"
    print(f"正在获取API数据: {api_key}")
    try:
        response = requests.get(f"{api_url}?key={api_key}")
        response.raise_for_status()
        data = response.json()
        
        # 获取新闻列表
        news_list = data["result"]["newslist"]
        # 使用html2text为每条新闻添加raw_content
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_emphasis = True
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            # 如有需要可添加 Cookie 字段
        }
        for news in news_list:
            if "url" in news:
                try:
                    response = requests.get(news["url"], headers=headers, timeout=10)
                    response.raise_for_status()
                    news["raw_content"] = h.handle(response.text)
                except Exception as e:
                    print(f"获取新闻内容失败: {news['url']} {e}")
                    news["raw_content"] = ""
        return news_list
    except Exception as e:
        print(f"获取API数据失败: {e}")
        return []  # 返回空列表而不是0，保持类型一致性
    
def main():
    """主函数"""
    print("=== AutoVideo - 自动化每日新闻视频生成工具 ===")
    
    # 创建配置
    config = Config.from_env()
    
    # 初始化视频生成器
    generator = AutoVideoGenerator(config)
    
    try:
        # 生成新闻视频
        print("正在生成新闻视频...")
        news_data = sample_news_data_fetcher(api_key=config.whyta_api_key)
        video_path = generator.generate_news_video(
            news_data_fetcher= lambda: news_data,  # 这里传递一个返回news_data的函数
            output_path=f"output/news_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        )
        
        print(f"✅ 新闻视频生成成功！")
        print(f"📹 视频路径: {video_path}")
        
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
