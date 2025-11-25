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

# 1. 每一行的容器：Flex布局 + 底部虚线 + 适度垂直间距
STYLE_ROW_DIV = (
    "display: flex; "
    "align-items: baseline; "
    "padding: 6px 0; " # 减小一点内边距，更紧凑
    "border-bottom: 1px dashed var(--nord04); "
)

# 2. 标签样式：
# - 移除 text-align: center (因为 chip 是 flex，不起作用)
# - 增加 justify-content: center (让文字在 flex 容器中居中)
# - 宽度设为 100px (足够放下 Categories 和 Keywords)
STYLE_LABEL_FIXED = (
    "width: 100px; "       
    "justify-content: center; " # Flex 布局下的水平居中
    "flex-shrink: 0; "     
    "margin-right: 15px; " 
)

# 3. 分数样式：
# - 移除 font-size (回归原生)
# - 保留背景色和 padding 以维持徽章形状
STYLE_SCORE = (
    "background: var(--nord0B); "
    "color: white; "
    "font-weight: bold; "
    "padding: 2px 8px; " 
    "margin-right: 10px;"
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
    
    # Content: 移除所有自定义样式，继承父元素
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
        article = soup.new_tag('article', **{'style': 'margin-bottom: 25px; padding-bottom: 5px; border-bottom: 3px double var(--nord03);'})
        details = soup.new_tag('details', **{'class': 'article-expander', 'open': 'true'})
        
        # === Row 1: Header (Score | Title | Publication) ===
        summary_tag = soup.new_tag('summary', **{'class': 'article-expander-title', 'style': 'display: flex; align-items: center; padding-bottom: 8px; border-bottom: 1px solid var(--nord04);'})
        
        # Score
        score_span = soup.new_tag('span', **{'class': 'chip', 'style': STYLE_SCORE})
        score_span.string = str(paper['score'])
        summary_tag.append(score_span)
        
        # Title Container
        title_container = soup.new_tag('div', **{'style': 'flex-grow: 1; display: flex; align-items: baseline; flex-wrap: wrap;'})
        
        # Title: 移除 font-size，只保留粗体
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

        # === Row 2: Meta (Links | Authors) ===
        meta_div = soup.new_tag('div', **{'class': 'article-authors', 'style': STYLE_ROW_DIV})
        
        # Links Container (左对齐)
        links_container = soup.new_tag('div', **{'style': 'width: 100px; text-align: center; flex-shrink: 0; margin-right: 15px; display: flex; justify-content: center;'})
        
        # Link Logic
        abs_link = paper['id']
        pdf_link = abs_link.replace('/abs/', '/pdf/')
        pdf_link = re.sub(r'v\d+$', '', pdf_link)

        link_a = soup.new_tag('a', href=abs_link, target="_blank", **{'style': 'margin-right: 15px; text-decoration: none;'})
        link_i = soup.new_tag('i', **{'class': 'ri-links-line'}) # 移除 font-size 放大
        link_a.append(link_i)
        links_container.append(link_a)
        
        pdf_a = soup.new_tag('a', href=pdf_link, target="_blank", **{'style': 'text-decoration: none;'})
        pdf_i = soup.new_tag('i', **{'class': 'ri-file-pdf-line'}) # 移除 font-size 放大
        pdf_a.append(pdf_i)
        links_container.append(pdf_a)
        
        meta_div.append(links_container)

        # Authors: 移除所有颜色和字体样式，完全继承原生
        authors_text = soup.new_tag('span', **{'style': 'font-style: italic;'})
        if isinstance(paper['authors'], list):
            authors_text.string = ", ".join(paper['authors'])
        else:
            authors_text.string = paper['authors']
        meta_div.append(authors_text)
        
        details.append(meta_div)

        # === Row 3: Title CN ===
        if paper.get('title_zh'):
            trans_row = create_row_with_label(soup, "Title CN", paper['title_zh'])
            if trans_row: details.append(trans_row)

        # === Row 4: Keywords ===
        keywords = paper.get('keywords', [])
        if keywords:
            if isinstance(keywords, list):
                keywords_str = " · ".join(keywords)
            else:
                keywords_str = keywords
            kw_row = create_row_with_label(soup, "Keywords", keywords_str)
            if kw_row: details.append(kw_row)

        # === Row 5: Summary ===
        sum_row = create_row_with_label(soup, "Summary", paper.get('summary', ''))
        if sum_row: details.append(sum_row)

        # === Row 6: Reason ===
        reason_row = create_row_with_label(soup, "Reason", paper.get('reason', ''))
        if reason_row: details.append(reason_row)

        # === Row 7: Abstract (Shortened Label) ===
        abs_row = create_row_with_label(soup, "Abstract", paper.get('abstract', ''))
        if abs_row: details.append(abs_row)

        # === Row 8: Comment (Shortened Label) ===
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

print("HTML injection complete. Styles reset to default.")
