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

# ----------------- 样式配置 -----------------

STYLE_ROW = "display: flex; align-items: flex-start; padding: 8px 0; border-bottom: 1px dashed var(--nord04);"
STYLE_CONTENT = "flex-grow: 1; line-height: 1.6; font-size: 0.95em;"

def create_styled_row(soup, label_text, content_text, is_last=False):
    """创建对齐的行"""
    if not content_text or content_text == "N/A":
        return None
        
    row_style = STYLE_ROW
    if is_last:
        row_style = row_style.replace("border-bottom: 1px dashed var(--nord04);", "")

    div = soup.new_tag('div', **{'style': row_style})
    
    # Label
    label = soup.new_tag('span', **{'class': 'chip', 'style': 'width: 130px; text-align: center; flex-shrink: 0; margin-right: 15px; display: block; height: fit-content;'})
    label.string = label_text
    div.append(label)
    
    # Content
    content = soup.new_tag('span', **{'style': STYLE_CONTENT})
    content.string = str(content_text)
    div.append(content)
    
    return div

# ----------------- 构建页面 -----------------

if scored_papers:
    top_section = soup.new_tag('section', **{'class': 'day-container', 'style': 'margin-top: 20px; border: 2px solid var(--nord08); padding: 20px;'})
    
    header_div = soup.new_tag('div', **{'class': 'date', 'style': 'padding-bottom: 15px; border-bottom: 2px solid var(--nord04); margin-bottom: 15px; font-size: 1.5em;'})
    header_div.string = f"🏆 Weekly Top Picks ({len(scored_papers)} Papers)"
    top_section.append(header_div)

    for paper in scored_papers:
        article = soup.new_tag('article', **{'style': 'margin-bottom: 30px; padding-bottom: 10px; border-bottom: 4px solid var(--nord04);'})
        details = soup.new_tag('details', **{'class': 'article-expander', 'open': 'true'})
        
        # === Title Area ===
        summary_tag = soup.new_tag('summary', **{'class': 'article-expander-title', 'style': 'display: flex; align-items: flex-start; padding-bottom: 10px; border-bottom: 1px solid var(--nord04); margin-bottom: 10px;'})
        
        # Score
        score_color = "var(--nord0B)" if paper['score'] >= 8 else "var(--nord0E)"
        score_div = soup.new_tag('div', **{'style': f'font-size: 2.2em; font-weight: 800; color: {score_color}; line-height: 1; margin-right: 20px; min-width: 40px; text-align: center;'})
        score_div.string = str(paper['score'])
        summary_tag.append(score_div)
        
        # Title Container
        title_container = soup.new_tag('div', **{'style': 'flex-grow: 1;'})
        
        # Title
        title_div = soup.new_tag('div', **{'style': 'font-size: 1.2em; font-weight: bold; line-height: 1.3; margin-bottom: 6px;'})
        title_div.string = paper['title']
        title_container.append(title_div)
        
        # Pub Chip
        if paper.get('publication') and paper['publication'] != "N/A":
            pub_span = soup.new_tag('span', **{'class': 'chip', 'style': 'font-size: 0.8em;'})
            pub_span.string = paper['publication']
            title_container.append(pub_span)
        
        summary_tag.append(title_container)
        details.append(summary_tag)

        # === Rows Area ===
        rows_container = soup.new_tag('div', **{'style': 'padding-left: 10px;'})

        # Row: Links & Authors
        meta_row = soup.new_tag('div', **{'style': STYLE_ROW})
        
        links_div = soup.new_tag('div', **{'style': 'width: 130px; flex-shrink: 0; margin-right: 15px; display: flex; justify-content: center; gap: 10px;'})
        abs_link = paper['id']
        pdf_link = abs_link.replace('/abs/', '/pdf/').replace('v1', '').replace('v2', '').replace('v3', '')
        pdf_link = re.sub(r'v\d+$', '', pdf_link)

        link_a = soup.new_tag('a', href=abs_link, target="_blank", **{'style': 'text-decoration: none; color: var(--nord08); font-weight: bold;'})
        link_a.append(soup.new_tag('i', **{'class': 'ri-links-line', 'style': 'font-size: 1.2em;'}))
        links_div.append(link_a)
        
        pdf_a = soup.new_tag('a', href=pdf_link, target="_blank", **{'style': 'text-decoration: none; color: var(--nord0B); font-weight: bold;'})
        pdf_a.append(soup.new_tag('i', **{'class': 'ri-file-pdf-line', 'style': 'font-size: 1.2em;'}))
        links_div.append(pdf_a)
        
        meta_row.append(links_div)

        authors_text = soup.new_tag('span', **{'style': 'font-style: italic; color: var(--nord03); font-size: 0.95em; align-self: center;'})
        if isinstance(paper['authors'], list):
            authors_text.string = ", ".join(paper['authors'])
        else:
            authors_text.string = paper['authors']
        meta_row.append(authors_text)
        
        rows_container.append(meta_row)

        # --- 修复部分：必须先检查返回值不为 None 再 append ---

        # Row: Title CN
        row = create_styled_row(soup, "Title CN", paper.get('title_zh', ''))
        if row: rows_container.append(row)

        # Row: AI Keywords
        keywords = paper.get('keywords', [])
        if keywords:
            kw_str = " · ".join(keywords) if isinstance(keywords, list) else keywords
            row = create_styled_row(soup, "AI Keywords", kw_str)
            if row: rows_container.append(row)

        # Row: AI Summary
        row = create_styled_row(soup, "AI Summary", paper.get('summary', ''))
        if row: rows_container.append(row)

        # Row: AI Reason
        row = create_styled_row(soup, "AI Reason", paper.get('reason', ''))
        if row: rows_container.append(row)

        # Row: Abstract
        row = create_styled_row(soup, "Abstract", paper.get('abstract', ''))
        if row: rows_container.append(row)

        # Row: Comment (这里之前报错)
        row = create_styled_row(soup, "Comment", paper.get('comment', ''))
        if row: rows_container.append(row)

        # Row: Categories (最后一行)
        row = create_styled_row(soup, "Categories", paper.get('category', ''), is_last=True)
        if row: rows_container.append(row)

        details.append(rows_container)
        article.append(details)
        top_section.append(article)

    # 插入到 Header 之后
    header_container = soup.find('section', class_='header-container')
    if header_container:
        header_container.insert_after(top_section)
    else:
        soup.body.insert(0, top_section)

# 写回
with open("target/index.html", 'w') as f:
    f.write(str(soup.prettify()))

print("HTML injection complete with safety checks.")
