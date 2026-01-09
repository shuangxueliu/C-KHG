import csv
from tenacity import retry, stop_after_attempt, wait_fixed

from handlers import QuestionHandler

# 定义重试逻辑
@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))  # 重试3次，每次间隔2秒
def safe_process_question(handler, question):
    try:
        return handler.process_question(question)
    except Exception as e:
        print(f"处理失败: {e}, 重试中...")
        raise  # 重新抛出异常以触发重试

def process_and_save():
    input_file = "causal_knowledge_qa.csv"
    output_file = "causal_knowledge_qwen_ours.csv"
    
    handler = QuestionHandler()
    
    # 初始化 CSV 文件并写入表头 (仅第一次)
    with open(output_file, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["问题", "答案"])  # 写入标题
    
    # 逐行读取输入文件
    with open(input_file, mode='r', newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)  # 自动处理标题
        
        for row in reader:
            question = row["问题"]
            try:
                # 使用重试逻辑处理问题
                answer = safe_process_question(handler, question)
            except Exception as e:
                # 如果重试多次后仍然失败，保存错误信息
                answer = f"处理失败: {str(e)}"
                
            # 实时追加写入当前问题的答案
            with open(output_file, mode='a', newline='', encoding='utf-8') as outfile:
                writer = csv.writer(outfile)
                writer.writerow([question, answer])
                
            print(f"已处理问题: {question}")

if __name__ == "__main__":
    process_and_save()