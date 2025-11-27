import os
import json
import time
import re
from openai import OpenAI

# 填写API的密钥
API_KEY = os.getenv("API_KEY")

# ================= 配置区域 =================
# 模型名称 (Batch API 支持 qwen-plus, qwen-max 等)
MODEL_NAME = "qwen-plus" 
# 轮询等待时间 (秒)
POLL_INTERVAL = 60 
# 最大等待时间 (秒)，防止 Github Action 超时 (例如设置 3小时)
MAX_WAIT_TIME = 5 * 60 * 60 

# ================= 提示词模板 (保持不变) =================
# 自定义的提示模板
PROMPT_TEMPLATE = """
我是一名人工智能方向的研究生，核心研究领域是 **文档图像理解（DIU / DocVQA）**。
我的目标是利用 **VLM (Multimodal LLM)** 技术解决文档理解中的核心痛点（如OCR幻觉、密集文本、复杂排版、长文档推理）。

请担任一名**挑剔的审稿人**，帮我筛选论文。
**原则：不拘泥于特定技术路线（如必须是Agent或必须是Intervention），只要能提升DIU性能的底层方法都值得关注；但坚决抵制无营养的“平行应用”。**

### 🛑 负面清单（直接打0-3分）
**只要命中以下任意一点，无需留情，直接低分：**
1.  **平行下游应用（Wrapper/Application）**：
    *   例如：“用LLM进行金融报表分析”、“基于RAG的法律文书助手”、“医疗病历结构化”。
    *   **理由**：这些只是把现有技术用在特定数据上，没有方法论创新。我只要提出技术源头的论文。
2.  **无关领域**：
    *   视频理解/生成、纯图像生成/修复、具身智能/机器人、自动驾驶、3D视觉。
    *   纯NLP的安全/对齐（Safety/Jailbreak）/政治正确，除非涉及“视觉幻觉”消除。
3.  **小语种**：非中英的特定语言数据集或模型。

### ✅ 关注领域与评分标准

#### 1. DIU 本题 (High Priority) -> [7-10分]
*   **任务**：DocVQA, Layout Analysis, Table Recognition, VIE/KIE, OCR-free End-to-End。
*   **趋势**：
    *   **DeepSeek-OCR 路线**：**Visual Token Compression (视觉压缩)**、Visual Representation Learning。
    *   **VLM for Doc**：专为文档设计的VLM架构、训练策略或高质量数据集。
*   *注：DIU领域内即使是传统方法或效率优化，也请保留（给及格分），因为圈子小，不宜漏掉。*

#### 2. 关联领域的“军火库” (Tools & Methodology) -> [6-9分]
**筛选标准：这篇上游论文提出的方法，能否被迁移来解决DIU的痛点？**
*   **痛点包括**：OCR幻觉（Hallucination）、细粒度定位（Grounding）、高分辨率处理、复杂逻辑推理。
*   **有价值的工具**：
    *   **Inference Scaling / Test-time Compute**：CoT、Search、Verification机制的**源头工作**。
    *   **VLM Architecture**：能显著提升High-Res输入处理能力或多模态对齐能力的架构改进。
    *   **Agent / Workflow**：能解决长文档阅读、多步信息检索过程中迷失问题的**Agent架构设计**（而非某个垂类Agent应用）。
    *   **Intervention / Steering**：推理阶段的干预或引导技术（作为一种可能的工具）。

### ❌ 这是一个发表信息提取任务
*   **Publication字段**：**仅**允许从 `comment` 字段提取！
*   **严禁**将 `category`（如 "cs.CV", "Computer Vision and Pattern Recognition"）当作发表信息。
*   如果 `comment` 为空或未提及会议/期刊，必须返回 "N/A"。

### 📝 打分参考 (0-10)
*   **9-10 (Must Read)**：DIU的SOTA工作；或者上游领域具有**范式转移（Paradigm Shift）**意义的底层创新（如Visual Token Compression的开山之作，或推理Scaling的新原理）。
*   **7-8 (Strong)**：扎实的DIU工作；或者能明显看到对DIU有迁移价值的上游新方法（如一种新的VQA去幻觉策略）。
*   **4-6 (Weak)**：DIU领域的常规灌水；或者虽是上游热点但迁移到文档极其困难的工作。
*   **0-3 (Reject)**：平行应用、无关领域、小语种。

### ✅ 任务指令
请根据以上标准评估。
1.  **Score**: 整数。
2.  **Title_zh**: 翻译标题。
3.  **Reason**: **中文**。
    *   **DIU论文**：简述其针对什么文档任务做了什么改进。
    *   **上游论文**：**核心必须解释该方法如何迁移到DIU领域**（例如：“该VLM分辨率处理方法可直接用于提升文档细粒度识别”）。
4.  **Summary**: 中文总结。
5.  **Keywords**: 3-5个关键词。
6.  **Publication**: 提取会议/期刊。

论文信息：
title：{title}
authors：{authors}
abstract：{abstract}
comment：{comment}
category：{category}

回复请用json格式，必须只返回json，不要返回其他内容：
"""

# JSON 响应模板
JSON_RESPONSE_TEMPLATE = """
{
  "score": x,
  "title_zh": "中文标题",
  "reason": "xxx",
  "summary": "xxx",
  "keywords": ["word1", "word2"],
  "publication": "xxx"
}
"""

def clean_json_response(response):
    """从LLM返回的字符串中提取JSON部分"""
    start_index = response.find("{")
    end_index = response.rfind("}") + 1
    if start_index != -1 and end_index != -1:
        return response[start_index:end_index]
    return None

def main(input_file, output_file):
    client = OpenAI(
        api_key=API_KEY,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

    # 1. 读取论文列表
    with open(input_file, 'r') as f:
        papers = json.load(f)
    
    if not papers:
        print("没有论文需要评估。")
        return

    print(f"准备评估 {len(papers)} 篇论文，正在构造 Batch 请求文件...")

    # 2. 构造 JSONL 数据 (Batch API 的输入格式)
    jsonl_filename = "batch_tasks.jsonl"
    paper_map = {p['id']: p for p in papers} # 方便后续通过 ID 找回论文对象
    
    with open(jsonl_filename, 'w') as f:
        for paper in papers:
            # 构造 Prompt
            prompt = PROMPT_TEMPLATE.format(
                title=paper['title'],
                authors=', '.join(paper['authors']) if isinstance(paper['authors'], list) else paper['authors'],
                abstract=paper['abstract'],
                comment=paper.get('comment', ''),
                category=paper['category'],
            ) + JSON_RESPONSE_TEMPLATE

            # 构造 Batch Request 对象
            # custom_id 使用论文 ID，方便后续匹配结果
            request_obj = {
                "custom_id": paper['id'], 
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": MODEL_NAME,
                    "messages": [
                        {'role': 'system', 'content': 'You are a critical academic reviewer.'},
                        {'role': 'user', 'content': prompt}
                    ],
                    "temperature": 0.2
                }
            }
            f.write(json.dumps(request_obj) + '\n')

    # 3. 上传文件
    print("正在上传 Batch 文件...")
    batch_input_file = client.files.create(
        file=open(jsonl_filename, "rb"),
        purpose="batch"
    )
    print(f"文件上传成功，ID: {batch_input_file.id}")

    # 4. 创建 Batch 任务
    print("正在创建 Batch 任务...")
    batch_job = client.batches.create(
        input_file_id=batch_input_file.id,
        endpoint="/v1/chat/completions",
        completion_window="24h", # 阿里云目前只支持 24h
        metadata={"description": "weekly_arxiv_evaluation"}
    )
    print(f"Batch 任务创建成功，Job ID: {batch_job.id}")

    # 5. 轮询等待任务完成
    print("开始轮询任务状态 (这可能需要几分钟到几小时)...")
    start_time = time.time()
    
    while True:
        # 获取任务最新状态
        batch_job = client.batches.retrieve(batch_job.id)
        status = batch_job.status
        print(f"当前状态: {status} (已耗时: {int(time.time() - start_time)}s)")

        if status == 'completed':
            print("任务完成！")
            break
        elif status in ['failed', 'expired', 'cancelled']:
            print(f"任务失败，状态: {status}")
            # 打印错误信息
            if batch_job.errors:
                print(batch_job.errors)
            return
        
        # 检查是否超时
        if time.time() - start_time > MAX_WAIT_TIME:
            print("错误：等待超时，脚本终止。")
            return

        time.sleep(POLL_INTERVAL)

    # 6. 下载并处理结果
    if batch_job.output_file_id:
        print("正在下载结果文件...")
        file_response = client.files.content(batch_job.output_file_id)
        result_content = file_response.text
        
        print("正在解析结果并写入最终 JSON...")
        
        # 解析 JSONL 结果
        for line in result_content.splitlines():
            if not line.strip(): continue
            
            result = json.loads(line)
            custom_id = result['custom_id']
            
            # 找到对应的原始论文对象
            if custom_id in paper_map:
                paper = paper_map[custom_id]
                
                # 获取 LLM 的响应内容
                # 注意：Batch API 的返回结构稍微深一点
                try:
                    print(result['response']['body'])
                    choice = result['response']['body']['choices'][0]
                    content = choice['message']['content']
                    
                    # 使用之前的清洗函数解析 JSON
                    cleaned_json = clean_json_response(content)
                    if cleaned_json:
                        try:
                            eval_data = json.loads(cleaned_json)
                            # 更新字段
                            paper['score'] = eval_data.get('score', 0)
                            paper['title_zh'] = eval_data.get('title_zh', '')
                            paper['reason'] = eval_data.get('reason', 'N/A')
                            paper['summary'] = eval_data.get('summary', 'N/A')
                            paper['keywords'] = eval_data.get('keywords', [])
                            paper['publication'] = eval_data.get('publication', 'N/A')
                        except json.JSONDecodeError:
                            print(f"ID {custom_id} JSON 解析失败: {cleaned_json}")
                    else:
                        print(f"ID {custom_id} 未找到有效 JSON 内容")
                        
                except Exception as e:
                    print(f"ID {custom_id} 处理响应时出错: {e}")
            else:
                print(f"警告：收到未知 custom_id {custom_id} 的结果")

        # 写入最终结果
        with open(output_file, 'w') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        
        print(f"处理完成！结果已写入 {output_file}")
    else:
        print("任务完成但没有 output_file_id，可能全部请求都失败了。")

if __name__ == "__main__":
    main("target/latest_papers.json", "target/evaluated_papers.json")
