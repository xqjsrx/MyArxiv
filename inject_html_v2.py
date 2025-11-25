import json
import re
from bs4 import BeautifulSoup

# 读取文件
with open("target/evaluated_papers.json", 'r') as f:
    evaluated_papers = json.load(f)

with open("target/index.html", 'r') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

# 过滤与排序
scored_papers = [p for p in evaluated_papers if 'score' in p and isinstance(p['score'], int)]
scored_papers.sort(key=lambda x: x['score'], reverse=True)

def create_row_with_label(soup, label_text, content_text):
    """
    创建 'Label + Content' 行
    使用 class="chip" 保持与主题一致的配色
    """
    if not content_text or content_text == "N/A":
        return None
        
    div = soup.new_tag('div', **{'class': 'article-summary-box-inner', 'style': 'margin-top: 6px;'})
    
    # Label (使用原生 chip 样式)
    label = soup.new_tag('span', **{'class': 'chip'})
    label.string = label_text
    div.append(label)
    
    # Content (不设置颜色，继承 body 颜色，只加一个左边距)
    content = soup.new_tag('span', **{'style': 'margin-left: 8px;'})
    content.string = str(content_text)
    div.append(content)
    
    return div

if scored_papers:
    # 外层容器
    top_section = soup.new_tag('section', **{'class': 'day-container', 'style': 'margin-top: 20px; border: 2px solid var(--nord08);'})
    
    # 顶部标题
    header_div = soup.new_tag('div', **{'class': 'date', 'style': 'color: var(--nord08); padding-bottom: 15px; border-bottom: 1px solid var(--nord04); margin-bottom: 15px;'})
    header_div.string = f"🏆 Weekly Top Picks ({len(scored_papers)} Papers)"
    top_section.append(header_div)

    for paper in scored_papers:
        article = soup.new_tag('article', **{'style': 'margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px dashed var(--nord03);'})
        details = soup.new_tag('details', **{'class': 'article-expander', 'open': 'true'})
        
        # === 第1行：分数 | 英文标题 | 中文标题 | 发表信息 ===
        summary_tag = soup.new_tag('summary', **{'class': 'article-expander-title', 'style': 'display: block; line-height: 1.6;'})
        
        # 1. Score Label
        score_span = soup.new_tag('span', **{'class': 'chip'})
        score_span.string = str(paper['score'])
        summary_tag.append(score_span)
        
        # 2. English Title
        title_span = soup.new_tag('span', **{'style': 'font-size: 1.1em; margin: 0 8px; font-weight: bold;'})
        title_span.string = paper['title']
        summary_tag.append(title_span)

        # 3. Chinese Title (Label + Text)
        if paper.get('title_zh'):
            zh_label = soup.new_tag('span', **{'class': 'chip'})
            zh_label.string = "中文标题"
            summary_tag.append(zh_label)
            
            zh_text = soup.new_tag('span', **{'style': 'margin: 0 8px; font-weight: normal; font-size: 0.95em;'})
            zh_text.string = paper['title_zh']
            summary_tag.append(zh_text)

        # 4. Publication (如果有)
        if paper.get('publication') and paper['publication'] != "N/A":
            pub_span = soup.new_tag('span', **{'class': 'chip'})
            pub_span.string = paper['publication']
            summary_tag.append(pub_span)
            
        details.append(summary_tag)

        # === 第2行：Links (ABS/PDF) ===
        # 使用 class="article-authors" 保持间距习惯，但里面放 chip
        link_div = soup.new_tag('div', **{'class': 'article-authors', 'style': 'margin-top: 5px;'})
        
        # 构造 PDF 链接
        abs_link = paper['id']
        pdf_link = abs_link.replace('/abs/', '/pdf/')
        pdf_link = re.sub(r'v\d+$', '', pdf_link)

        # ABS Chip
        abs_a = soup.new_tag('a', href=abs_link, target="_blank", **{'class': 'chip', 'style': 'text-decoration: none; margin-right: 10px;'})
        abs_a.string = "ABS"
        link_div.append(abs_a)
        
        # PDF Chip
        pdf_a = soup.new_tag('a', href=pdf_link, target="_blank", **{'class': 'chip', 'style': 'text-decoration: none;'})
        pdf_a.string = "PDF" 
        link_div.append(pdf_a)
        
        details.append(link_div)

        # === 第3行：Authors ===
        # 作者也用 chip 样式包裹 Label 吗？不，通常作者列表直接显示。
        # 你说“作者也用原来的颜色”，原来的作者是直接显示的文本。
        authors_div = soup.new_tag('div', **{'class': 'article-authors', 'style': 'margin-bottom: 5px;'})
        authors_icon = soup.new_tag('i', **{'class': 'ri-user-3-line', 'style': 'margin-right: 5px;'}) # 加个小图标美化
        authors_div.append(authors_icon)
        
        authors_text = soup.new_tag('span') # 不加 style，继承默认颜色
        if isinstance(paper['authors'], list):
            authors_text.string = ", ".join(paper['authors'])
        else:
            authors_text.string = paper['authors']
        authors_div.append(authors_text)
        details.append(authors_div)

        # === 第4行：AI Keywords ===
        keywords = paper.get('keywords', [])
        if keywords:
            if isinstance(keywords, list):
                keywords_str = " · ".join(keywords)
            else:
                keywords_str = keywords
            kw_row = create_row_with_label(soup, "AI Keywords", keywords_str)
            if kw_row: details.append(kw_row)

        # === 第5行：AI Summary ===
        sum_row = create_row_with_label(soup, "AI Summary", paper.get('summary', ''))
        if sum_row: details.append(sum_row)

        # === 第6行：AI Reason ===
        reason_row = create_row_with_label(soup, "AI Reason", paper.get('reason', ''))
        if reason_row: details.append(reason_row)

        # === 第7行：Original Abstract ===
        abs_row = create_row_with_label(soup, "Original Abstract", paper.get('abstract', ''))
        if abs_row: details.append(abs_row)

        # === 第8行：Comment (Raw) ===
        if paper.get('comment'):
            com_row = create_row_with_label(soup, "Comment", paper['comment'])
            if com_row: details.append(com_row)

        # === 第9行：Categories ===
        cat_row = create_row_with_label(soup, "Categories", paper.get('category', ''))
        if cat_row: details.append(cat_row)

        article.append(details)
        top_section.append(article)

    # 插入 Header
    header_container = soup.find('section', class_='header-container')
    if header_container:
        header_container.insert_after(top_section)
    else:
        soup.body.insert(0, top_section)

# 写回
with open("target/index.html", 'w') as f:
    f.write(str(soup.prettify()))

print("HTML injection complete: Original Theme Colors & New Layout.")
