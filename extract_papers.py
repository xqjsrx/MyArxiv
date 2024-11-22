import json
import re

def remove_newlines(text):
    # 去除字符串中的所有换行符
    return re.sub(r'\s+', ' ', text).strip()

def process_cache_file(cache_file, output_file):
    with open(cache_file, 'r') as f:
        cache_data = json.load(f)

    # 获取最新的日期
    latest_date = sorted(cache_data.keys(), reverse=True)[0]
    latest_data = cache_data[latest_date]

    # 合并所有大类的数据，并添加大类属性
    merged_data = []
    for category, papers in latest_data.items():
        for paper in papers:
            paper['category'] = category
            paper['title'] = remove_newlines(paper['title'])  # 去除 title 中的换行符
            paper['comment'] = remove_newlines(paper['comment'])
            paper['abstract'] = remove_newlines(paper['summary'])
            del paper['summary']  # 删除原来的 summary 字段
            merged_data.append(paper)

    # 写入输出文件
    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    process_cache_file("target/cache.json", "target/latest_papers.json")
