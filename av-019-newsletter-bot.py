#!/usr/bin/env python3
"""
AV-019 AI日报 Newsletter 自动化脚本
功能：抓取AI资讯 → AI生成内容 → 发送邮件
作者：可乐
日期：2026-05-07
"""

import os
import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import List, Dict

# ============ 配置 ============
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "sk-你的百炼API密钥")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "re_你的Resend密钥")

# 信息源列表
SOURCES = [
    {"name": "TechCrunch AI", "url": "https://techcrunch.com/category/artificial-intelligence/"},
    {"name": "The Verge AI", "url": "https://www.theverge.com/ai-artificial-intelligence"},
    {"name": "VentureBeat AI", "url": "https://venturebeat.com/ai/"},
    {"name": "Hacker News", "url": "https://news.ycombinator.com/"},
    {"name": "Product Hunt", "url": "https://www.producthunt.com/"},
]

# ============ 1. 抓取资讯 ============
def fetch_news() -> List[Dict]:
    """
    从多个源抓取AI资讯
    实际项目中可以使用RSS、API或爬虫
    """
    # 模拟抓取的数据（实际项目中替换为真实抓取）
    mock_news = [
        {
            "title": "OpenAI发布GPT-5，多模态能力大幅提升",
            "summary": "GPT-5支持视频理解、实时语音对话，API价格降低50%",
            "url": "https://openai.com/blog/gpt-5",
            "source": "OpenAI",
            "category": "重磅"
        },
        {
            "title": "Midjourney V7发布，图像生成质量再突破",
            "summary": "新增'风格迁移'功能，可一键将照片转换为任意艺术风格",
            "url": "https://midjourney.com/v7",
            "source": "Midjourney",
            "category": "工具"
        },
        {
            "title": "AI头像生成服务月入3万案例拆解",
            "summary": "95后设计师用Midjourney+小红书，单月变现3万",
            "url": "https://example.com/case",
            "source": "案例库",
            "category": "变现"
        },
        {
            "title": "2026年AI创业10大风口预测",
            "summary": "AI Agent、AI数字人、AI教育...资深投资人深度分析",
            "url": "https://example.com/trends",
            "source": "投资分析",
            "category": "趋势"
        },
        {
            "title": "Claude 4支持100万token上下文",
            "summary": "Anthropic发布Claude 4，可处理整本书籍内容",
            "url": "https://anthropic.com/claude-4",
            "source": "Anthropic",
            "category": "重磅"
        },
    ]
    return mock_news

# ============ 2. AI生成内容 ============
def generate_newsletter(news_list: List[Dict]) -> str:
    """
    使用百炼API生成Newsletter内容
    """
    # 构建prompt
    news_text = "\n\n".join([
        f"{i+1}. 【{n['category']}】{n['title']}\n   {n['summary']}"
        for i, n in enumerate(news_list)
    ])
    
    prompt = f"""请为以下AI资讯生成一份专业的中文Newsletter。

资讯列表：
{news_text}

要求：
1. 写一个吸引人的标题（包含emoji）
2. 每条资讯扩展为80-100字的中文解读
3. 添加实用价值点评（为什么重要/怎么用）
4. 最后加1条"💰 今日AI变现机会"（具体可操作）
5. 格式为HTML，适合邮件发送
6. 风格专业但不失亲和力

输出格式：
```html
<!-- Newsletter HTML -->
```
"""

    # 调用百炼API (使用标准库)
    url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    payload = {
        "model": "qwen-max",
        "input": {
            "messages": [
                {"role": "system", "content": "你是一位专业的AI资讯编辑，擅长将技术新闻转化为通俗易懂的中文内容。"},
                {"role": "user", "content": prompt}
            ]
        },
        "parameters": {
            "result_format": "message",
            "max_tokens": 4000,
            "temperature": 0.7
        }
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
                "Content-Type": "application/json"
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            
            # 提取HTML内容
            content = result["output"]["choices"][0]["message"]["content"]
            
            # 如果输出包含代码块，提取其中的HTML
            if "```html" in content:
                html_start = content.find("```html") + 7
                html_end = content.find("```", html_start)
                content = content[html_start:html_end].strip()
            
            return content
        
    except Exception as e:
        print(f"AI生成失败: {e}")
        # 返回默认模板
        return generate_fallback_html(news_list)

def generate_fallback_html(news_list: List[Dict]) -> str:
    """生成默认HTML模板"""
    today = datetime.now().strftime("%Y年%m月%d日")
    
    news_html = "\n".join([
        f"""
        <div style="margin-bottom: 25px; padding-bottom: 20px; border-bottom: 1px solid #eee;">
            <span style="display: inline-block; background: {get_tag_color(n['category'])}; color: white; padding: 3px 10px; border-radius: 10px; font-size: 12px; margin-bottom: 8px;">{n['category']}</span>
            <h3 style="margin: 0 0 8px 0; color: #333; font-size: 18px;">{n['title']}</h3>
            <p style="margin: 0; color: #666; line-height: 1.6;">{n['summary']}</p>
            <a href="{n['url']}" style="color: #667eea; text-decoration: none; font-size: 14px;">阅读全文 →</a>
        </div>
        """
        for n in news_list
    ])
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>AI日报 - {today}</title>
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f5f5f5;">
        <div style="background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #667eea;">
                <h1 style="color: #667eea; margin: 0;">🤖 AI日报</h1>
                <p style="color: #999; margin: 10px 0 0 0;">{today}</p>
            </div>
            
            {news_html}
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-top: 30px;">
                <h3 style="margin: 0 0 10px 0;">💰 今日AI变现机会</h3>
                <p style="margin: 0; opacity: 0.9;">用AI生成头像+小红书引流，单张售价¥29，日销10单=月入¥8700。工具：Midjourney + 小红书。</p>
            </div>
            
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                <p style="color: #999; font-size: 14px;">© 2026 AI日报 | <a href="#" style="color: #667eea;">取消订阅</a></p>
            </div>
        </div>
    </body>
    </html>
    """

def get_tag_color(category: str) -> str:
    """获取分类标签颜色"""
    colors = {
        "重磅": "#ff4757",
        "工具": "#2ed573",
        "变现": "#ffa502",
        "趋势": "#1e90ff"
    }
    return colors.get(category, "#747d8c")

# ============ 3. 发送邮件 ============
def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    使用Resend发送邮件 (使用标准库)
    """
    url = "https://api.resend.com/emails"
    
    payload = {
        "from": "AI日报 <daily@ai-daily.com>",
        "to": to_email,
        "subject": subject,
        "html": html_content,
        "tags": ["newsletter", "daily"]
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            method='POST'
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            print(f"✅ 邮件发送成功: {to_email}")
            return True
            
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False

def send_to_all_subscribers(html_content: str):
    """
    发送给所有订阅用户
    实际项目中从数据库读取订阅列表
    """
    # 模拟订阅列表
    subscribers = [
        "user1@example.com",
        "user2@example.com",
    ]
    
    today = datetime.now().strftime("%m月%d日")
    subject = f"🤖 AI日报 - {today} | 今日5条精选"
    
    for email in subscribers:
        send_email(email, subject, html_content)

# ============ 主流程 ============
def main():
    """
    主流程：抓取 → 生成 → 发送
    """
    print("🚀 开始生成AI日报...")
    print("-" * 50)
    
    # 1. 抓取资讯
    print("📡 正在抓取AI资讯...")
    news = fetch_news()
    print(f"✅ 抓取到 {len(news)} 条资讯")
    
    # 2. AI生成内容
    print("🤖 正在生成Newsletter内容...")
    newsletter_html = generate_newsletter(news)
    print("✅ 内容生成完成")
    
    # 3. 保存到本地（调试）
    today = datetime.now().strftime("%Y%m%d")
    output_file = f"/tmp/newsletter_{today}.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(newsletter_html)
    print(f"💾 已保存到: {output_file}")
    
    # 4. 发送邮件（取消注释以启用）
    # print("📧 正在发送邮件...")
    # send_to_all_subscribers(newsletter_html)
    
    print("-" * 50)
    print("🎉 AI日报生成完成！")
    print(f"📧 预览文件: {output_file}")

if __name__ == "__main__":
    main()
