# handlers.py
from neo4j_client4 import Neo4jClient
from xinference_client import XinferenceClient
from pyvis.network import Network
import re
import matplotlib.pyplot as plt
#适用于百川模型,qwen，yi
# def extract_chip_name(chip_name_line):
#     # 定义正则表达式规则
#     # 1. 匹配中文冒号、英文冒号、逗号或空格后的内容
#     # 2. 匹配引号中间的内容
#     pattern = r"""
#         (?:[:：,]\s*)([^：,]+)  # 匹配中文冒号、英文冒号、逗号后的内容
#         |                     # 或
#         "(.*?)"               # 匹配双引号中的内容
#         |                     # 或
#         '(.*?)'               # 匹配单引号中的内容
#         |                         
#         ^(.+)$            # 最后兜底匹配整行
# # 匹配单引号中的内容
#     """
#     # 使用 re.VERBOSE 允许正则表达式中添加注释
#     match = re.search(pattern, chip_name_line, re.VERBOSE)
    
#     if match:
#         # 提取匹配的组，优先提取非引号部分
#         for group in match.groups():
#             if group:  # 如果组不为空
#                 # 去除多余的空格
#                 return group.strip()
#         # 如果匹配到引号中的内容
#         if match.group(2):  # 双引号内容
#             return match.group(2).strip("'")
#         if match.group(3):  # 单引号内容
#             return match.group(3).strip("'")
#     else:
#         # 如果没有匹配到任何内容，返回 None 或其他默认值
#         return None
#适用于deepseek模型
def extract_chip_name(chip_name_line):
    # 改进后的正则表达式规则
    pattern = r"""
        "(.*?)"                   # 优先匹配双引号内容
        |                         # 或
        '(.*?)'                   # 或匹配单引号内容
        |                         # 或
        (?:^|:|：|,)\s*([^：,]+)  # 匹配标点/行首后的内容
        |                         # 或
        ^(.+)$                    # 最后兜底匹配整行
    """
    match = re.search(pattern, chip_name_line, re.VERBOSE)
    
    if match:
        for group in match.groups():
            if group:
                return group.strip()
    return None

class QuestionHandler:
    def __init__(self):
        self.neo4j = Neo4jClient()
        self.model = XinferenceClient()

   
    # ------------------------- 处理非因果问题 -------------------------
    def extract_chip_and_question_direction(self, question):
        prompt = f"""
        下面是一个用户提问：{question}
        请从问题中提取出芯片名称,请用中文回答问题。
        请按照如下格式返回，只回答“芯片名称”，不要有多余的话，不要有换行：
        芯片名称：<芯片名称> 
        """
        response = self.model.chat(prompt, system_prompt="")
        
        
        try:
            # 将响应按换行符分割成列表，并取第一行
            chip_name_line = response.split("\n")[0]
            # 从第一行中提取芯片名称（冒号后面的部分）
            chip_name = chip_name_line.split("芯片名称：")[1].strip()#适用于glm模型、deepseek模型
            # chip_name = extract_chip_name(chip_name_line)
        except (IndexError, ValueError):
            print("无法提取芯片名称，请检查问题格式。")
            return None
        
        return chip_name
#知识图谱问题处理
    def handle_user_question(self, question):
        chip_name= self.extract_chip_and_question_direction(question)
        if not chip_name:
           print("无法提取芯片名称，请检查问题格式。")
           chip_info_str = "无"
          
        else:
            query_result = self.neo4j.query_chip_info(chip_name)
            if not query_result:
                print("在图谱中未找到关于芯片",chip_name,"的相关信息。")
                chip_info_str ="无"
            else:
                print(f"找到关于芯片 '{chip_name}' 的相关信息。")
                chip_info = query_result[0]
                chip_info_str = f"芯片名称: {chip_info['ChipName']}\n"
                chip_info_str += f"设计风格: {chip_info.get('Style', '无数据')}\n"
                chip_info_str += f"技术领域: {chip_info.get('Field', '无数据')}\n"
                chip_info_str += f"生产厂商: {chip_info.get('Producer', '无数据')}\n"
                chip_info_str += f"质量认证: {chip_info.get('QualityControl', '无数据')}\n"
                chip_info_str += f"销售数据: {chip_info.get('Sales', '无数据')}\n"
                chip_info_str += f"相关原因: {chip_info.get('Causes', '无数据')}\n"
                chip_info_str += f"造成影响: {chip_info.get('Effects', '无数据')}\n"
                
                
        # 构造最终prompt
        prompt = f"""
        问题：{question}
        检索到的信息：{chip_info_str}
        1、答案仅基于检索到的信息。
        2、以逻辑和连贯的方式组织解释。
        3、如果信息中描述了因果关系，请明确解释。
        4、提供简明且适用于领域的最终答案。
        """
        response = self.model.chat(prompt, system_prompt="您是汽车芯片设计和生产领域的专家。您的任务是严格根据下面提供的信息生成清晰且技术上准确的答案。不要引入超出给定内容的外部知识或假设。")
        
        return response


    # ------------------------- 主处理函数 -------------------------
    def process_question(self, question):
        print(question)
        return self.handle_user_question(question)
        