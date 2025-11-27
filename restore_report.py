import os
from bs4 import BeautifulSoup

def restore_weekly_report(backup_file, current_file):
    # 1. 读取备份的旧网页（包含 AI 报告）
    if not os.path.exists(backup_file):
        print("没有找到备份文件，无法恢复报告。")
        return

    with open(backup_file, 'r', encoding='utf-8') as f:
        old_html = f.read()
    
    # 2. 读取刚刚生成的新网页（纯净版）
    with open(current_file, 'r', encoding='utf-8') as f:
        new_html = f.read()

    soup_old = BeautifulSoup(old_html, 'html.parser')
    soup_new = BeautifulSoup(new_html, 'html.parser')

    # 3. 寻找 AI 周报板块
    # 我们之前的逻辑是：<section class="day-container"> 里面包含 "🏆 Weekly Top Picks"
    # 或者根据 style border 找
    found_report = None
    sections = soup_old.find_all('section', class_='day-container')
    
    for section in sections:
        # 简单判断：只要包含那个奖杯 emoji 或者是 Weekly Top Picks 文字
        if section.get_text() and "🏆 Weekly Top Picks" in section.get_text():
            found_report = section
            break
    
    if found_report:
        print("成功在旧网页中找到 AI 周报板块！正在移植...")
        
        # 4. 插入到新网页
        # 逻辑同 inject_html_v2：插入到 header 之后
        header_container = soup_new.find('section', class_='header-container')
        if header_container:
            header_container.insert_after(found_report)
        else:
            soup_new.body.insert(0, found_report)
            
        # 5. 保存
        with open(current_file, 'w', encoding='utf-8') as f:
            f.write(str(soup_new.prettify()))
        print("AI 周报已恢复到今日构建的页面中。")
    else:
        print("在旧网页中未发现 AI 周报（可能是第一次运行或上一版本无报告）。")

if __name__ == "__main__":
    # backup.html 是我们在 workflow 里下载的旧版
    # target/index.html 是 arxivfeed 刚生成的新版
    restore_weekly_report("backup.html", "target/index.html")
