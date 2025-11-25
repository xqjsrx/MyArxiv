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

    # 遍历缓存中的每一天 (cache_data 是以日期为 Key 的字典)
    for date, categories in cache_data.items():
        for category, papers in categories.items():
            for paper in papers:
                # 清理数据
                paper['title'] = remove_newlines(paper['title'])
                if 'comment' in paper and paper['comment'] is not None:
                    paper['comment'] = remove_newlines(paper['comment'])
                
                # 处理摘要字段 (原项目中是 summary)
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
                    
                    # 1. 合并 Category (去重)
                    if category not in existing_paper['category']:
                        existing_paper['category'].append(category)
                    
                    # 2. 版本检查：如果当前遍历到的 paper 更新时间更晚，则更新内容
                    # 注意：这里假设 arxiv api 返回的 updated 字符串是可以比较的，或者我们简单地假设后遍历到的是新的
                    # 为了简单起见，通常 ID 带 v2 的会比 v1 晚。
                    # 如果现有的是 v1，新来的是 v2，我们要更新除了 category 以外的信息
                    if paper_id > existing_paper['id']: # 字符串比较 v2 > v1
                         # 保留已有的分类列表
                        cats = existing_paper['category']
                        # 更新内容
                        unique_papers[base_id] = paper
                        unique_papers[base_id]['category'] = cats

    # 将处理后的字典转回列表
    merged_data = list(unique_papers.values())
    
    # 把 category 列表转回字符串，如 "cs.CV, cs.AI"
    for paper in merged_data:
        paper['category'] = ", ".join(paper['category'])

    print(f"Total papers after deduplication: {len(merged_data)}")

    # 写入输出文件
    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    process_cache_file("target/cache.json", "target/latest_papers.json")
