
from typing import Any, Dict, List
import requests
import html2text

def sample_news_data_fetcher() -> List[Dict[str, Any]]:
    """
    从API获取新闻数据，并为每条新闻添加raw_content字段
    """
    api_url = "https://whyta.cn/api/tx/generalnews"
    api_key = "d8c6d4c75ba0"
    
    try:
        response = requests.get(f"{api_url}?key={api_key}")
        response.raise_for_status()
        data = response.json()
        
        # 获取新闻列表
        news_list = data["result"]["newslist"]
        
        # 使用html2text为每条新闻添加raw_content
        h = html2text.HTML2Text()
        h.ignore_links = False
        
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
    
print(sample_news_data_fetcher())