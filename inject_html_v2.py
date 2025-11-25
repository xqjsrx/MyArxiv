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
# 统一样式，避免混乱
STYLE_CHIP_BASE = "font-size: 0.85em; padding: 2px 8px; border-radius: 12px; margin-right: 8px; font-weight: bold; display: inline-block;"
STYLE_CHIP_SCORE = f"{STYLE_CHIP_BASE} background: var(--nord0B); color: white;" # 红色分数
STYLE_CHIP_PUB = f"{STYLE_CHIP_BASE} background: var(--nord0E); color: var(--nord01);" # 绿色发表信息
STYLE_CHIP_LABEL = f"{STYLE_CHIP_BASE} background: var(--nord09); color: var(--nord00);" # 蓝色通用Label

# 内容文字样式 - 移除特定颜色，跟随主题（亮色/暗色）
STYLE_CONTENT_TEXT = "font-size: 0.95em; line-height: 1.5;"

def create_row_with_label(soup, label_text, content_text):
    """辅助函数：创建统一格式的 'Label + Content' 行"""
    if not content_text or content_text == "N/A":
        return None
        
    div = soup.new_tag('div', **{'class': 'article-summary-box-inner', 'style': 'margin-top: 6px;'})
    
    # Label
    label = soup.new_tag('span', **{'style': STYLE_CHIP_LABEL})
    label.string = label_text
    div.append(label)
    
    # Content
    content = soup.new_tag('span', **{'style': STYLE_CONTENT_TEXT})
    content.string = str(content_text)
    div.append(content)
    
    return div

# ----------------- 构建页面 -----------------

if scored_papers:
    top_section = soup.new_tag('section', **{'class': 'day-container', 'style': 'margin-top: 20px; border: 2px solid var(--nord08);'})
    
    header_div = soup.new_tag('div', **{'class': 'date', 'style': 'color: var(--nord08); padding-bottom: 15px; border-bottom: 1px solid var(--nord04); margin-bottom: 15px;'})
    header_div.string = f"🏆 Weekly Top Picks ({len(scored_papers)} Papers)"
    top_section.append(header_div)

    for paper in scored_papers:
        article = soup.new_tag('article', **{'style': 'margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px dashed var(--nord03);'})
        details = soup.new_tag('details', **{'class': 'article-expander', 'open': 'true'})
        
        # --- Row 1: Score + Title + Publication ---
        summary_tag = soup.new_tag('summary', **{'class': 'article-expander-title', 'style': 'display: flex; align-items: baseline; flex-wrap: wrap;'})
        
        # 1. Score
        score_span = soup.new_tag('span', **{'style': STYLE_CHIP_SCORE})
        score_span.string = str(paper['score'])
        summary_tag.append(score_span)
        
        # 2. Title
        title_span = soup.new_tag('span', **{'style': 'font-size: 1.1em; margin-right: 10px; font-weight: bold;'})
        title_span.string = paper['title']
        summary_tag.append(title_span)
        
        # 3. Publication (Extracted by AI)
        if paper.get('publication') and paper['publication'] != "N/A":
            pub_span = soup.new_tag('span', **{'style': STYLE_CHIP_PUB})
            pub_span.string = paper['publication']
            summary_tag.append(pub_span)
            
        details.append(summary_tag)

        # --- Row 2: Links + Authors ---
        meta_div = soup.new_tag('div', **{'class': 'article-authors', 'style': 'margin: 5px 0; display: flex; align-items: center;'})
        
        # Link Logic
        abs_link = paper['id']
        # 构造 PDF 链接: 把 /abs/ 换成 /pdf/，并去掉末尾的版本号 (v1, v2)
        pdf_link = abs_link.replace('/abs/', '/pdf/')
        pdf_link = re.sub(r'v\d+$', '', pdf_link)

        # Abs Icon
        link_a = soup.new_tag('a', href=abs_link, target="_blank", **{'style': 'margin-right: 10px; text-decoration: none; color: var(--nord08);'})
        link_a.string = "[ABS]" # 或者保留原本的 icon 逻辑
        meta_div.append(link_a)
        
        # PDF Icon
        pdf_a = soup.new_tag('a', href=pdf_link, target="_blank", **{'style': 'margin-right: 15px; text-decoration: none; color: var(--nord0B);'})
        pdf_a.string = "[PDF]" 
        meta_div.append(pdf_a)

        # Authors
        authors_text = soup.new_tag('span', **{'style': 'font-style: italic; color: var(--nord03); font-size: 0.9em;'})
        if isinstance(paper['authors'], list):
            authors_text.string = ", ".join(paper['authors'])
        else:
            authors_text.string = paper['authors']
        meta_div.append(authors_text)
        
        details.append(meta_div)

        # --- Row 3: AI Keywords ---
        keywords = paper.get('keywords', [])
        if keywords:
            # 如果是列表转字符串
            if isinstance(keywords, list):
                keywords_str = " · ".join(keywords)
            else:
                keywords_str = keywords
            
            kw_row = create_row_with_label(soup, "AI Keywords", keywords_str)
            if kw_row: details.append(kw_row)

        # --- Row 4: AI Summary ---
        sum_row = create_row_with_label(soup, "AI Summary", paper.get('summary', ''))
        if sum_row: details.append(sum_row)

        # --- Row 5: AI Reason ---
        reason_row = create_row_with_label(soup, "AI Reason", paper.get('reason', ''))
        if reason_row: details.append(reason_row)

        # --- Row 6: Original Abstract ---
        # 你的需求：这里字体太淡了。
        # 这里的 STYLE_CONTENT_TEXT 没有设置 color，会自动继承父元素颜色（通常是黑色或白色），应该能解决问题。
        # 如果需要更弱化一点，可以加 opacity: 0.8
        abs_div = soup.new_tag('div', **{'class': 'article-summary-box-inner', 'style': 'margin-top: 6px; opacity: 0.9;'})
        abs_label = soup.new_tag('span', **{'style': f"{STYLE_CHIP_LABEL} background: var(--nord04);"}) # 灰色Label
        abs_label.string = "Original Abstract"
        abs_div.append(abs_label)
        
        abs_content = soup.new_tag('span', **{'style': 'font-size: 0.9em; display: block; margin-top: 4px;'})
        abs_content.string = paper.get('abstract', '')
        abs_div.append(abs_content)
        details.append(abs_div)

        # --- Row 7: Raw Comment (如果有且不为空) ---
        if paper.get('comment'):
            com_row = create_row_with_label(soup, "Raw Comment", paper['comment'])
            if com_row: details.append(com_row)

        # --- Row 8: Categories ---
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

print("HTML injection complete with new layout.")
