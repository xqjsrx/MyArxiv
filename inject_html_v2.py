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

# ================== 样式定义 ==================
# 使用 Flexbox 实现左侧 Label 固定宽度，右侧内容自适应
# Label 宽度固定为 110px，右对齐，增加留白

STYLE_ROW = "display: flex; padding: 8px 0; border-bottom: 1px dashed var(--nord03); align-items: baseline;"
STYLE_LAST_ROW = "display: flex; padding: 8px 0; align-items: baseline;" # 最后一行不要下划线

# Label 样式：固定宽度，右对齐，字体颜色偏淡
STYLE_LABEL_COL = "flex: 0 0 130px; text-align: right; padding-right: 15px; color: var(--nord09); font-weight: bold; font-size: 0.9em;"

# Content 样式：占据剩余空间
STYLE_CONTENT_COL = "flex: 1; color: var(--body-color); line-height: 1.6;"

# 分数样式：大号数字，醒目颜色
STYLE_BIG_SCORE = "font-size: 2.2em; font-weight: 800; color: var(--nord0B); line-height: 1; margin-right: 15px;"

# 标题样式
STYLE_TITLE = "font-size: 1.3em; font-weight: bold; color: var(--nord06); line-height: 1.3;"

# 发表信息 Badge
STYLE_PUB_BADGE = "display: inline-block; font-size: 0.7em; padding: 2px 6px; border-radius: 4px; background: var(--nord0E); color: var(--nord01); vertical-align: middle; margin-left: 8px; font-weight: bold;"


def create_row(soup, label_text, content_html, is_last=False):
    """
    创建一行：左边是 Label，右边是 Content
    content_html 可以是字符串，也可以是 Tag 对象
    """
    if not content_html or content_html == "N/A":
        return None
        
    div = soup.new_tag('div', **{'style': STYLE_LAST_ROW if is_last else STYLE_ROW})
    
    # Left Column (Label)
    label = soup.new_tag('div', **{'style': STYLE_LABEL_COL})
    label.string = label_text
    div.append(label)
    
    # Right Column (Content)
    content_div = soup.new_tag('div', **{'style': STYLE_CONTENT_COL})
    
    if isinstance(content_html, str):
        content_div.string = content_html
    else:
        content_div.append(content_html)
        
    div.append(content_div)
    return div

# ================== 构建页面 ==================

if scored_papers:
    # 外层容器：加一点内边距和圆角，让它看起来更像一个周报卡片
    top_section = soup.new_tag('section', **{'class': 'day-container', 'style': 'margin-top: 20px; border: 2px solid var(--nord08); border-radius: 8px; overflow: hidden;'})
    
    # 大标题
    header_div = soup.new_tag('div', **{'class': 'date', 'style': 'padding: 15px; background: var(--nord01); border-bottom: 1px solid var(--nord03);'})
    header_div.string = f"🏆 Weekly Top Picks ({len(scored_papers)} Papers)"
    top_section.append(header_div)

    for paper in scored_papers:
        # 每篇论文的卡片容器
        article = soup.new_tag('article', **{'style': 'padding: 20px; border-bottom: 4px solid var(--nord00); background: var(--nord01);'})
        # 默认展开
        details = soup.new_tag('details', **{'class': 'article-expander', 'open': 'true', 'style': 'border: none; padding: 0;'})
        
        # --- 头部区域 (Score + Title) ---
        # summary 标签去除默认样式，自定义 Flex 布局
        summary_tag = soup.new_tag('summary', **{'class': 'article-expander-title', 'style': 'display: flex; align-items: flex-start; margin-bottom: 15px;'})
        
        # 1. Big Score (Left)
        score_div = soup.new_tag('div', **{'style': STYLE_BIG_SCORE})
        score_div.string = str(paper['score'])
        summary_tag.append(score_div)
        
        # 2. Title Block (Right)
        title_block = soup.new_tag('div', **{'style': 'flex: 1;'})
        
        # Title Text
        title_text = soup.new_tag('div', **{'style': STYLE_TITLE})
        title_text.string = paper['title']
        
        # Publication Badge (If exists)
        if paper.get('publication') and paper['publication'] != "N/A":
            pub_span = soup.new_tag('span', **{'style': STYLE_PUB_BADGE})
            pub_span.string = paper['publication']
            title_text.append(pub_span)
        
        title_block.append(title_text)
        
        # Authors & Links (Sub-header)
        meta_div = soup.new_tag('div', **{'style': 'margin-top: 8px; font-size: 0.9em; color: var(--nord03); display: flex; align-items: center; flex-wrap: wrap;'})
        
        # Links
        abs_link = paper['id']
        pdf_link = abs_link.replace('/abs/', '/pdf/')
        pdf_link = re.sub(r'v\d+$', '', pdf_link)
        
        link_style = "margin-right: 12px; text-decoration: none; color: var(--nord08); display: inline-flex; align-items: center;"
        
        link_a = soup.new_tag('a', href=abs_link, target="_blank", **{'style': link_style})
        link_a.append(soup.new_tag('i', **{'class': 'ri-links-line', 'style': 'margin-right: 4px;'}))
        link_a.append("Abstract")
        meta_div.append(link_a)
        
        pdf_a = soup.new_tag('a', href=pdf_link, target="_blank", **{'style': link_style})
        pdf_a.append(soup.new_tag('i', **{'class': 'ri-file-pdf-line', 'style': 'margin-right: 4px;'}))
        pdf_a.append("PDF")
        meta_div.append(pdf_a)

        # Separator
        sep = soup.new_tag('span', **{'style': 'margin-right: 12px; color: var(--nord03);'})
        sep.string = "|"
        meta_div.append(sep)

        # Authors
        authors_text = soup.new_tag('span', **{'style': 'font-style: italic;'})
        if isinstance(paper['authors'], list):
            authors_text.string = ", ".join(paper['authors'])
        else:
            authors_text.string = paper['authors']
        meta_div.append(authors_text)
        
        title_block.append(meta_div)
        summary_tag.append(title_block)
        details.append(summary_tag)

        # --- 表格化内容区域 ---
        
        # 容器：给所有详情内容加一个背景色微调，区别于头部
        content_wrapper = soup.new_tag('div', **{'style': 'background: rgba(0,0,0,0.1); padding: 10px 15px; border-radius: 6px;'})

        # 1. Title CN
        if paper.get('title_zh'):
            row = create_row(soup, "Title CN", paper['title_zh'])
            content_wrapper.append(row)

        # 2. Keywords
        keywords = paper.get('keywords', [])
        if keywords:
            if isinstance(keywords, list):
                # 关键词用小标签样式，更漂亮
                kw_container = soup.new_tag('div')
                for k in keywords:
                    k_span = soup.new_tag('span', **{'style': 'display: inline-block; background: var(--nord03); color: var(--nord06); padding: 2px 8px; border-radius: 4px; font-size: 0.85em; margin-right: 6px; margin-bottom: 2px;'})
                    k_span.string = k
                    kw_container.append(k_span)
                row = create_row(soup, "Keywords", kw_container)
            else:
                row = create_row(soup, "Keywords", str(keywords))
            content_wrapper.append(row)

        # 3. AI Summary
        row = create_row(soup, "AI Summary", paper.get('summary', ''))
        if row: content_wrapper.append(row)

        # 4. AI Reason
        # 给理由加一点点高亮背景，因为它是最重要的AI判断
        reason_content = soup.new_tag('span', **{'style': 'color: var(--nord0D);'}) # 使用黄色/橙色高亮
        reason_content.string = paper.get('reason', '')
        row = create_row(soup, "AI Reason", reason_content)
        if row: content_wrapper.append(row)

        # 5. Original Abstract
        # 原文摘要字体弄淡一点，作为折叠内容或者次要内容
        abs_content = soup.new_tag('span', **{'style': 'color: var(--nord03); font-size: 0.9em; text-align: justify; display: block;'})
        abs_content.string = paper.get('abstract', '')
        row = create_row(soup, "Abstract", abs_content)
        if row: content_wrapper.append(row)

        # 6. Comment
        if paper.get('comment'):
            row = create_row(soup, "Comment", paper['comment'])
            content_wrapper.append(row)

        # 7. Categories (Last row, no border)
        row = create_row(soup, "Categories", paper.get('category', ''), is_last=True)
        if row: content_wrapper.append(row)

        details.append(content_wrapper)
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

print("HTML injection complete. Table-like layout applied.")
