import json
import re

def remove_newlines(text):
    if text:
        return re.sub(r'\s+', ' ', text).strip()
    return ""

def get_base_id(url):
    """
    从URL中提取不带版本号的基础ID。
    例如: http://arxiv.org/abs/2301.12345v1 -> http://arxiv.org/abs/2301.12345
    这样可以防止同一篇论文的v1和v2版本被当作两篇处理。
    """
    return re.sub(r'v\d+$', '', url)

def process_cache_file(cache_file, output_file):
    with open(cache_file, 'r') as f:
        cache_data = json.load(f)

    # 使用字典进行去重：Key是基础ID，Value是论文数据
    unique_papers = {}

    # 1. 获取所有日期并降序排序 (最新的日期排在前面)
    all_dates = sorted(cache_data.keys(), reverse=True)
    
    # 2. 只取最近的 7 天
    target_dates = all_dates[:7]
    print(f"Processing papers from the last {len(target_dates)} days: {target_dates}")

    # 3. 遍历这 7 天的数据
    for date in target_dates:
        categories = cache_data[date]
        for category, papers in categories.items():
            for paper in papers:
                # 清理数据
                paper['title'] = remove_newlines(paper['title'])
                if 'comment' in paper and paper['comment'] is not None:
                    paper['comment'] = remove_newlines(paper['comment'])
                
                # 处理摘要字段
                if 'summary' in paper:
                    paper['abstract'] = remove_newlines(paper['summary'])
                    del paper['summary']
                
                # 获取基础ID用于去重
                paper_id = paper['id']
                base_id = get_base_id(paper_id)

                # 去重与合并逻辑
                if base_id not in unique_papers:
                    # 如果是新论文，直接存入，并初始化 category 为列表方便追加
                    paper['category'] = [category] 
                    unique_papers[base_id] = paper
                else:
                    # 如果论文已存在
                    existing_paper = unique_papers[base_id]
                    
                    # 合并 Category (去重)
                    if category not in existing_paper['category']:
                        existing_paper['category'].append(category)
                    
                    # 版本检查：如果当前遍历到的 paper ID 字典序更大 (v2 > v1)，则更新内容
                    if paper_id > existing_paper['id']:
                         # 保留已有的分类列表
                        cats = existing_paper['category']
                        # 更新内容
                        unique_papers[base_id] = paper
                        unique_papers[base_id]['category'] = cats

    # 将处理后的字典转回列表
    merged_data = list(unique_papers.values())
    
    # 把 category 列表转回字符串，如 "cs.CV, cs.AI"
    for paper in merged_data:
        if isinstance(paper['category'], list):
            paper['category'] = ", ".join(paper['category'])

    print(f"Total papers after deduplication: {len(merged_data)}")

    # # ================= DEBUG LIMIT =================
    # # 限制为前 20 篇，用于快速测试 (正式运行时请注释掉)
    # merged_data = merged_data[:20]
    # print(f"DEBUG MODE: Only processing top {len(merged_data)} papers.")
    # # ===============================================

    # 写入输出文件
    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    process_cache_file("target/cache.json", "target/latest_papers.json")
