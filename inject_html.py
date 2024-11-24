import json
from bs4 import BeautifulSoup

# 读取 evaluated_papers.json 文件
with open("target/evaluated_papers.json", 'r') as f:
    evaluated_papers = json.load(f)

# 读取 HTML 文件
with open("target/index.html", 'r') as f:
    html_content = f.read()

# 使用 BeautifulSoup 解析 HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 创建一个字典，用于快速查找论文的评分、理由和摘要
papers_dict = {paper['id']: paper for paper in evaluated_papers}

# 查找所有文章的详细信息部分
articles = soup.find_all('details', class_='article-expander')

for article in articles:
    # 获取论文的链接
    link = article.find('a')['href']
    
    # 根据链接查找对应的论文信息
    if link in papers_dict:
        paper_info = papers_dict[link]
        score = paper_info['score']
        reason = paper_info['reason']
        summary = paper_info['summary']
        
        # 创建新的评分、理由和摘要元素
        score_element = soup.new_tag('div', **{'class': 'article-score'})
        score_element.string = f'Score: {score}'

        reason_element = soup.new_tag('div', **{'class': 'article-reason'})
        reason_element.string = f'Reason: {reason}'

        summary_element = soup.new_tag('div', **{'class': 'article-summary'})
        summary_element.string = f'Summary: {summary}'
        
        # 将新元素插入到文章的详细信息部分
        article.append(score_element)
        article.append(reason_element)
        article.append(summary_element)

# 将修改后的 HTML 内容写回文件
with open("target/index.html", 'w') as f:
    f.write(str(soup.prettify()))

print("HTML 文件已更新，评分、理由和摘要已插入。")
