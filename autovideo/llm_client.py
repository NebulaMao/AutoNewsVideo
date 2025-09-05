from openai import OpenAI
from typing import Dict, Any, Optional, List
import json
import logging
from .config import LLMConfig

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
    
    def generate_news_json(self, news_data: Dict[str, Any], prompt_template: str = None) -> Dict[str, Any]:
        """
        Generate formatted news JSON data using LLM
        """
        if prompt_template is None:
            prompt_template = """
请将以下新闻数据格式化为JSON格式，包含以下字段：
- title: 新闻标题
- summary: 新闻摘要
- category: 新闻类别
- importance: 重要程度 (1-5)
- keywords: 关键词列表
- created_at: 创建时间

新闻数据：{news_data}

请以JSON格式返回，不要包含其他解释。
"""
        
        prompt = prompt_template.format(news_data=json.dumps(news_data, ensure_ascii=False))
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是一个新闻格式化助手，专门将新闻数据格式化为标准JSON格式。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info("Successfully generated news JSON")
            return result
            
        except Exception as e:
            logger.error(f"Error generating news JSON: {str(e)}")
            raise
    
    def generate_summary(self, news_items: List[Dict[str, Any]]) -> str:
        """
        Generate overview summary for news items
        """
        prompt = f"""
请根据以下新闻条目生成一个简短的概览介绍，用于快速介绍今日新闻要点：

新闻条目：
{json.dumps(news_items, ensure_ascii=False, indent=2)}

请生成一段50-100字的概览介绍。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是一个新闻摘要助手，擅长生成简洁有力的新闻概览。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=200
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info("Successfully generated news summary")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            raise
    
    def generate_item_introduction(self, news_item: Dict[str, Any]) -> str:
        """
        Generate introduction text for individual news item
        """
        prompt = f"""
请根据以下新闻条目生成一个简短的介绍语，用于TTS语音合成：

新闻条目：
{json.dumps(news_item, ensure_ascii=False, indent=2)}

请生成一段30-60字的介绍语。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是一个新闻介绍助手，擅长生成简洁明了的新闻介绍。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=150
            )
            
            introduction = response.choices[0].message.content.strip()
            logger.info("Successfully generated news item introduction")
            return introduction
            
        except Exception as e:
            logger.error(f"Error generating item introduction: {str(e)}")
            raise