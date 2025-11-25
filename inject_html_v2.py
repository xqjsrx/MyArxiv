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

# ----------------- 样式定义 (Inline CSS) -----------------

# 1. 每一行的容器：Flex布局，底部虚线
STYLE_ROW = (
    "display: flex; "
    "align-items: baseline; "
    "padding: 8px 0; "
    "border-bottom: 1px dashed var(--nord04); " # 虚线分割
    "opacity: 0.95;"
)

# 2. 左侧 Label：固定宽度，右对齐，显得很整齐
STYLE_LABEL_COL = (
    "flex: 0 0 110px; "  # 固定宽度 110px
    "text-align: right; "
    "margin-right: 15px; "
)

# 3. 右侧 Content：占据剩余空间
STYLE_CONTENT_COL = (
    "flex: 1; "
    "line-height: 1.6; "
)

# 4. Label 本身的 Chip 样式 (保持原生风格)
STYLE_CHIP_LABEL = (
    "font-size: 0.85em; "
    "padding: 3px 8px; "
    "border-radius: 6px; "
    "font-weight: bold; "
    "background: var(--nord04); " # 稍微淡一点的背景，不抢眼
    "color: var(--nord01); "
    "display: inline-block;"
)

# 5. 分数勋章样式 (更醒目)
STYLE_SCORE_BADGE = (
    "background: var(--nord0B); " # 红色
    "color: white; "
    "font-size: 1.1em; "
    "font-weight: 800; "
    "padding: 4px 10px; "
    "border-radius: 8px; "
    "margin-right: 12px; "
    "box-shadow: 0 2px 4px rgba(0,0,0,0.2);"
)

# ----------------- 辅助函数 -----------------

def create_flex_row(soup, label_text, content_text):
    """创建左右对齐的 Flex 行"""
    if not content_text or content_text == "N/A":
        return None
        
    row_div = soup.new_tag('div', **{'style': STYLE_ROW})
    
    # Left Column (Label)
    left_col = soup.new_tag('div', **{'style': STYLE_LABEL_COL})
    label_span = soup.new_tag('span', **{'style': STYLE_CHIP_LABEL}) # 这里不再用 class=chip 避免样式冲突，直接内联
    label_span.string = label_text
    left_col.append(label_span)
    row_div.append(left_col)
    
    # Right Column (Content)
    right_col = soup.new_tag('div', **{'style': STYLE_CONTENT_COL})
    right_col.string = str(content_text)
    row_div.append(right_col)
    
    return row_div

# ----------------- 构建页面 -----------------

if scored_papers:
    # 外层容器
    top_section = soup.new_tag('section', **{'class': 'day-container', 'style': 'margin-top: 25px; border: 3px solid var(--nord08); border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);'})
    
    # 头部
    header_div = soup.new_tag('div', **{'class': 'date', 'style': 'padding: 15px; border-bottom: 2px solid var(--nord04); background: rgba(0,0,0,0.02);'})
    header_div.string = f"🏆 Weekly Top Picks ({len(scored_papers)} Papers)"
    top_section.append(header_div)

    for paper in scored_papers:
        # 单篇论文容器 (去掉原本的 dashed border，因为内部行已经有分割线了)
        article = soup.new_tag('article', **{'style': 'padding: 0 15px 25px 15px; margin-bottom: 10px; border-bottom: 4px solid var(--nord04);'})
        
        # 默认展开
        details = soup.new_tag('details', **{'class': 'article-expander', 'open': 'true', 'style': 'border: none;'})
        
        # === 标题行 (Summary) ===
        summary_tag = soup.new_tag('summary', **{'class': 'article-expander-title', 'style': 'padding: 15px 0 10px 0; display: flex; align-items: center; list-style: none;'})
        
        # 1. Score Badge
        score_span = soup.new_tag('span', **{'style': STYLE_SCORE_BADGE})
        score_span.string = str(paper['score'])
        summary_tag.append(score_span)
        
        # 2. Title Container
        title_div = soup.new_tag('div', **{'style': 'flex: 1;'})
        
        # Title Text
        title_text = soup.new_tag('div', **{'style': 'font-size: 1.25em; font-weight: 700; line-height: 1.3; color: var(--nord03);'})
        title_text.string = paper['title']
        title_div.append(title_text)
        
        # Publication Tag (if exists)
        if paper.get('publication') and paper['publication'] != "N/A":
            pub_span = soup.new_tag('span', **{'class': 'chip', 'style': 'margin-top: 6px; font-size: 0.8em; background: var(--nord0E); color: var(--nord01);'})
            pub_span.string = paper['publication']
            title_div.append(pub_span)
            
        summary_tag.append(title_div)
        details.append(summary_tag)

        # === 核心信息区 (Flex 布局) ===
        
        # 1. 作者与链接行 (这一行比较特殊，不需要Label，单独处理)
        meta_row = soup.new_tag('div', **{'style': "padding-bottom: 12px; margin-bottom: 5px; border-bottom: 1px solid var(--nord04); display: flex; align-items: center; font-size: 0.9em; color: var(--nord03);"})
        
        # Icons
        abs_link = paper['id']
        pdf_link = abs_link.replace('/abs/', '/pdf/')
        pdf_link = re.sub(r'v\d+$', '', pdf_link)
        
        link_a = soup.new_tag('a', href=abs_link, target="_blank", **{'style': 'margin-right: 12px; text-decoration: none; display: flex; align-items: center;'})
        link_i = soup.new_tag('i', **{'class': 'ri-links-line', 'style': 'margin-right: 4px;'}) 
        link_a.append(link_i)
        link_a.append("ABS")
        meta_row.append(link_a)

        pdf_a = soup.new_tag('a', href=pdf_link, target="_blank", **{'style': 'margin-right: 20px; text-decoration: none; display: flex; align-items: center; color: var(--nord0B);'})
        pdf_i = soup.new_tag('i', **{'class': 'ri-file-pdf-line', 'style': 'margin-right: 4px;'})
        pdf_a.append(pdf_i)
        pdf_a.append("PDF")
        meta_row.append(pdf_a)

        # Authors
        authors_text = soup.new_tag('span', **{'style': 'font-style: italic; opacity: 0.8;'})
        if isinstance(paper['authors'], list):
            authors_text.string = ", ".join(paper['authors'])
        else:
            authors_text.string = paper['authors']
        meta_row.append(authors_text)
        
        details.append(meta_row)

        # 2. 中文标题 (Title CN)
        if paper.get('title_zh'):
            row = create_flex_row(soup, "Title CN", paper['title_zh'])
            if row:
                row.find_all('div')[1]['style'] += "font-weight: bold; color: var(--nord02);"
                details.append(row)

        # 3. AI Keywords
        keywords = paper.get('keywords', [])
        if keywords:
            if isinstance(keywords, list):
                keywords_str = " · ".join(keywords)
            else:
                keywords_str = keywords
            row = create_flex_row(soup, "AI Keywords", keywords_str)
            if row: details.append(row)

        # 4. AI Summary
        row = create_flex_row(soup, "AI Summary", paper.get('summary', ''))
        if row: details.append(row)

        # 5. AI Reason
        row = create_flex_row(soup, "AI Reason", paper.get('reason', ''))
        if row: details.append(row)

        # 6. Original Abstract
        row = create_flex_row(soup, "Abstract", paper.get('abstract', ''))
        if row:
            # 摘要字体稍微小一点，颜色淡一点
            row.find_all('div')[1]['style'] += "font-size: 0.9em; opacity: 0.8;"
            details.append(row)

        # 7. Raw Comment
        row = create_flex_row(soup, "Comment", paper.get('comment', ''))
        if row: details.append(row)

        # 8. Categories
        row = create_flex_row(soup, "Categories", paper.get('category', ''))
        if row: details.append(row)

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

print("HTML injection complete: Fixed None appending error.")
