import json
import re
from datetime import datetime, timedelta
import os
import toml

# 保留原有配置读取逻辑
def load_config():
    with open("config.toml", "r", encoding="utf-8") as f:
        return toml.load(f)

def parse_arxiv_id(link):
    """解析论文基础ID和版本号（新增核心函数）"""
    match = re.search(r'arxiv\.org/abs/(\d+\.\d+)(v\d+)?', link)
    if not match:
        return None, 1  # 无效链接默认版本1
    base_id = match.group(1)
    version = match.group(2) or 'v1'
    return base_id, int(version[1:])

def get_week_dates():
    """获取过去7天的日期字符串（YYYY-MM-DD）"""
    today = datetime.now().date()
    return [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

def extract_weekly_papers():
    config = load_config()
    cache_path = config["site"]["cache_url"]
    output_path = "target/weekly_unique_papers.json"
    
    # 确保输出目录存在
    os.makedirs("target", exist_ok=True)
    
    # 读取缓存文件（原有逻辑）
    with open(cache_path, "r", encoding="utf-8") as f:
        cache_data = json.load(f)
    
    # 筛选本周论文（新增）
    week_dates = get_week_dates()
    weekly_papers = []
    for date, categories in cache_data.items():
        if date not in week_dates:
            continue
        for category, papers in categories.items():
            for paper in papers:
                # 补充日期和分类信息
                paper["date"] = date
                paper["category"] = category
                # 统一字段名（保留原有处理）
                paper["title"] = paper.get("title", "").replace("\n", " ")
                paper["abstract"] = paper.get("summary", "").replace("\n", " ")
                if "summary" in paper:
                    del paper["summary"]
                weekly_papers.append(paper)
    
    # 去重：按基础ID分组，保留最新版本（新增核心逻辑）
    paper_groups = {}
    for paper in weekly_papers:
        base_id, version = parse_arxiv_id(paper["link"])
        if not base_id:
            weekly_papers.append(paper)
            continue
        # 保留最新版本
        if base_id not in paper_groups or version > paper_groups[base_id]["version"]:
            paper_groups[base_id] = {
                "paper": paper,
                "version": version
            }
    
    # 提取去重后的论文
    unique_papers = [g["paper"] for g in paper_groups.values()]
    print(f"去重前：{len(weekly_papers)} 篇，去重后：{len(unique_papers)} 篇")
    
    # 保存结果
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unique_papers, f, indent=2, ensure_ascii=False)
    print(f"本周去重论文已保存至：{output_path}")

if __name__ == "__main__":
    extract_weekly_papers()
