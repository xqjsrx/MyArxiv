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
papers_dict = {paper['id']: paper for paper in evaluated_papers if all(key in paper for key in ['id', 'score', 'reason', 'summary'])}

# 查找所有文章的详细信息部分
articles = soup.find_all('details', class_='article-expander')

for article in articles:
    # 获取论文的链接
    link = article.find('a')['href']
    
    # 根据链接查找对应的论文信息
    if link in papers_dict:
        paper_info = papers_dict[link]
        score = paper_info.get('score', 'N/A')
        reason = paper_info.get('reason', 'N/A')
        summary = paper_info.get('summary', 'N/A')
        
        # 更新标题，将评分放在最前面
        title_summary = article.find('summary', class_='article-expander-title')
        if title_summary:
            title_summary.string = f'Score: {score} {title_summary.text.strip()}'
        
        # 创建新的理由和摘要元素
        reason_span = soup.new_tag('span', **{'class': 'chip'})
        reason_span.string = 'reason'
        reason_text = soup.new_tag('span')
        reason_text.string = reason
        
        summary_span = soup.new_tag('span', **{'class': 'chip'})
        summary_span.string = 'summary'
        summary_text = soup.new_tag('span')
        summary_text.string = summary
        
        # 创建一个新的 div 元素来包含理由和摘要
        summary_box_inner = soup.new_tag('div', **{'class': 'article-summary-box-inner'})
        summary_box_inner.append(reason_span)
        summary_box_inner.append(reason_text)
        summary_box_inner.append(soup.new_tag('br'))
        summary_box_inner.append(summary_span)
        summary_box_inner.append(summary_text)
        
        # 将新的 div 元素插入到文章的详细信息部分
        article.append(summary_box_inner)

# 将修改后的 HTML 内容写回文件
with open("target/index.html", 'w') as f:
    f.write(str(soup.prettify()))

print("HTML 文件已更新，评分、理由和摘要已插入。")
