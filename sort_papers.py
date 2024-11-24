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
        category_name = category.text.strip()
        print(f"Processing category: {category_name}")
        
        # 查找该类别下的所有论文
        articles = category.find_next_siblings('article')
        if articles:
            scored_articles = []
            for article in articles:
                score_span = article.find('span', class_='chip')
                if score_span and score_span.text.isdigit():
                    score = int(score_span.text)
                else:
                    score = 0  # 如果没有评分，默认为0分
                    print(f"No score found for article: {article.find('summary').text.strip()}, setting score to 0")
                
                scored_articles.append((score, article))
                print(f"Added article with score {score}: {article.find('summary').text.strip()}")
            
            # 按评分从高到低排序
            scored_articles.sort(key=lambda x: x[0], reverse=True)
            print(f"Sorted articles for category {category_name}: {[article.find('summary').text.strip() for _, article in scored_articles]}")
            
            # 将排序后的论文重新插入到类别下
            for score, article in scored_articles:
                category.insert_after(article)
                print(f"Inserted article with score {score}: {article.find('summary').text.strip()}")

# 将修改后的 HTML 内容写回文件
with open("target/index.html", 'w') as f:
    f.write(str(soup.prettify()))

print("HTML 文件已更新，最新一天的论文已按评分排序。")
