import json
from bs4 import BeautifulSoup

# 读取 HTML 文件
with open("target/index.html", 'r') as f:
    html_content = f.read()

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 查找最新一天的日期容器
latest_day_container = soup.find('section', class_='day-container')
if latest_day_container:
    date_div = latest_day_container.find('div', class_='date')
    if date_div:
        print(f"Processing papers for date: {date_div.text.strip()}")

    # 查找所有类别
    categories = latest_day_container.find_all('summary')
    for category in categories:
        # 查找该类别下的所有论文
        articles = category.find_next_siblings('article')
        if articles:
            # 提取评分并排序
            scored_articles = []
            for article in articles:
                score_span = article.find('span', class_='chip')
                if score_span and score_span.text.isdigit():
                    score = int(score_span.text)
                    scored_articles.append((score, article))
            
            # 按评分从高到低排序
            scored_articles.sort(key=lambda x: x[0], reverse=True)
            
            # 将排序后的论文重新插入到类别下
            for score, article in scored_articles:
                category.insert_after(article)

# 将修改后的 HTML 内容写回文件
with open("target/index.html", 'w') as f:
    f.write(str(soup.prettify()))

print("HTML 文件已更新，最新一天的论文已按评分排序。")
