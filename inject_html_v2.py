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

# ----------------- 样式常量定义 -----------------

# 1. 每一行的容器
STYLE_ROW_DIV = (
    "display: flex; "
    "align-items: baseline; "
    "padding: 6px 0; "
    "border-bottom: 1px dashed var(--nord04); "
    "font-size: 0.75em; " 
)

# 2. 标签样式
STYLE_LABEL_FIXED = (
    "width: 80px; "       
    "justify-content: center; " 
    "flex-shrink: 0; "     
    "margin-right: 15px; " 
)

# 3. 分数样式
STYLE_SCORE = (
    "background: var(--nord0B); "
    "color: white; "
    "font-weight: bold; "
    "font-size: 1.2em; "
    "padding: 3px 10px; " 
    "margin-right: 10px;"
    "border-radius: 4px;"
)

# 4. [新增] 链接胶囊样式 (放在标题行的胶囊)
STYLE_LINKS_CAPSULE = (
    "display: inline-flex; "
    "align-items: center; "
    "margin-right: 10px; "
    "padding: 2px 8px; "
    "background: var(--nord08); " # [修改] 灰色 -> 青色
    "color: white; "      # 深色图标
    "border-radius: 4px;"
)


# ----------------- 辅助函数 -----------------

def create_row_with_label(soup, label_text, content_text):
    if not content_text or content_text == "N/A":
        return None
        
    div = soup.new_tag('div', **{'style': STYLE_ROW_DIV})
    
    # Label
    label = soup.new_tag('span', **{'class': 'chip', 'style': STYLE_LABEL_FIXED})
    label.string = label_text
    div.append(label)
    
    # Content
    content = soup.new_tag('span', **{'style': 'flex-grow: 1;'})
    content.string = str(content_text)
    div.append(content)
    
    return div

# ----------------- 构建页面 -----------------

if scored_papers:
    top_section = soup.new_tag('section', **{'class': 'day-container', 'style': 'margin-top: 20px; border: 2px solid var(--nord08);'})
    
    header_div = soup.new_tag('div', **{'class': 'date', 'style': 'padding-bottom: 15px; border-bottom: 1px solid var(--nord04); margin-bottom: 15px;'})
    header_div.string = f"🏆 Weekly Top Picks ({len(scored_papers)} Papers)"
    top_section.append(header_div)

    for paper in scored_papers:
        # Article 容器
        # [修改] margin-bottom 缩小到 15px
        article = soup.new_tag('article', **{'style': 'margin-bottom: 15px;'})
        details = soup.new_tag('details', **{'class': 'article-expander', 'open': 'true'})
        
        # === Row 1: Header (Score | Links | Title | Publication) ===
        summary_tag = soup.new_tag('summary', **{'class': 'article-expander-title', 'style': 'display: flex; align-items: center; padding-bottom: 10px; border-bottom: 1px solid var(--nord04);'})
        
        # 1. Score
        score_span = soup.new_tag('span', **{'class': 'chip', 'style': STYLE_SCORE})
        score_span.string = str(paper['score'])
        summary_tag.append(score_span)

        # 2. [新增] Links Capsule (Wrap with label style)
        links_span = soup.new_tag('span', **{'style': STYLE_LINKS_CAPSULE})
        
        # Link Logic
        abs_link = paper['id']
        pdf_link = abs_link.replace('/abs/', '/pdf/')
        pdf_link = re.sub(r'v\d+$', '', pdf_link)

        # ABS Icon
        link_a = soup.new_tag('a', href=abs_link, target="_blank", **{'style': 'margin-right: 8px; text-decoration: none; display: flex; align-items: center;'})
        link_i = soup.new_tag('i', **{'class': 'ri-links-line', 'style': 'font-size: 1.1em;'}) 
        link_a.append(link_i)
        links_span.append(link_a)
        
        # PDF Icon
        pdf_a = soup.new_tag('a', href=pdf_link, target="_blank", **{'style': 'text-decoration: none; display: flex; align-items: center;'})
        pdf_i = soup.new_tag('i', **{'class': 'ri-file-pdf-line', 'style': 'font-size: 1.1em;'}) 
        pdf_a.append(pdf_i)
        links_span.append(pdf_a)

        summary_tag.append(links_span)
        
        # 3. Title Container
        title_container = soup.new_tag('div', **{'style': 'flex-grow: 1; display: flex; align-items: baseline; flex-wrap: wrap;'})
        
        # Title
        title_span = soup.new_tag('span', **{'style': 'margin-right: 10px; font-weight: bold;'})
        title_span.string = paper['title']
        title_container.append(title_span)
        
        # Publication
        if paper.get('publication') and paper['publication'] != "N/A":
            pub_span = soup.new_tag('span', **{'class': 'chip'})
            pub_span.string = paper['publication']
            title_container.append(pub_span)
            
        summary_tag.append(title_container)
        details.append(summary_tag)

        # === Row 2: Title CN ===
        if paper.get('title_zh'):
            trans_row = create_row_with_label(soup, "Title CN", paper['title_zh'])
            if trans_row: details.append(trans_row)

        # === Row 3: Keywords ===
        keywords = paper.get('keywords', [])
        if keywords:
            if isinstance(keywords, list):
                keywords_str = " · ".join(keywords)
            else:
                keywords_str = keywords
            kw_row = create_row_with_label(soup, "Keywords", keywords_str)
            if kw_row: details.append(kw_row)

        # === Row 4: Summary ===
        sum_row = create_row_with_label(soup, "Summary", paper.get('summary', ''))
        if sum_row: details.append(sum_row)

        # === Row 5: Reason ===
        reason_row = create_row_with_label(soup, "Reason", paper.get('reason', ''))
        if reason_row: details.append(reason_row)

        # === Row 6: Abstract ===
        abs_row = create_row_with_label(soup, "Abstract", paper.get('abstract', ''))
        if abs_row: details.append(abs_row)

        # === Row 7: [移动位置] Authors ===
        # 原作者行被移除，改为标准Label行，插入在 Abstract 和 Comment 之间
        authors_str = ""
        if isinstance(paper['authors'], list):
            authors_str = ", ".join(paper['authors'])
        else:
            authors_str = paper['authors']
        
        auth_row = create_row_with_label(soup, "Authors", authors_str)
        # 为作者行增加一点额外样式(如斜体)，通过操作返回的tag
        if auth_row:
            # 找到内容span (最后一个子元素)
            auth_row.contents[-1]['style'] += "font-style: italic;" 
            details.append(auth_row)

        # === Row 8: Comment ===
        if paper.get('comment'):
            com_row = create_row_with_label(soup, "Comment", paper['comment'])
            if com_row: details.append(com_row)

        # === Row 9: Categories ===
        cat_row = create_row_with_label(soup, "Categories", paper.get('category', ''))
        if cat_row:
            # 移除最后一行的 border
            cat_row['style'] = cat_row['style'].replace('border-bottom: 1px dashed var(--nord04);', '')
            details.append(cat_row)

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

print("HTML injection complete. Layout compacted and rearranged.")
