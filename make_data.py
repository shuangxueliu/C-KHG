from py2neo import Graph, Relationship

# Neo4j配置
uri = "bolt://localhost:7687"
username = "neo4j"
password = "********"  # 请替换为实际密码
graph = Graph(uri, auth=(username, password))

import re

def preprocess_cause_text(cause_text):
    # 定义要过滤的词汇列表
    filters = ["芯片的", "技术", "的", "是", "什么", "吗", "影响", "由", "引起", "会", "影响", "能力", "自动驾驶", "路径规划", "精度","高效",
               "广泛应用于","广泛应用","广泛","应用于","应用","于","是","什么","用于",
               "主要销售给","主要销售","销售给","销售","给","主要","供应给"]
    # 使用正则表达式替换掉这些词汇（这里假设词汇前后可能有空格或其他字符，所以使用\s*来匹配任意数量的空格）
    for filter_word in filters:
        cause_text = re.sub(r'\s*' + re.escape(filter_word) + r'\s*', '', cause_text).strip()
    return cause_text

def contains_cause_keyword(field_text, cause_text):
    # 预处理原因文本
    preprocessed_cause_text = preprocess_cause_text(cause_text)
    
    # 提取预处理后原因文本中的第一个词或词组（空格分隔）
    cause_keywords = preprocessed_cause_text.split()[0] if preprocessed_cause_text else ""
    # 检查字段文本中是否包含关键词（不区分大小写）
    if cause_keywords.lower() in field_text.lower():
        # print(cause_keywords)
        return True
    else:
        return False



# 获取所有Field和Cause节点
fields = graph.nodes.match("Field").all()
causes = graph.nodes.match("Cause").all()
fields_num=0
# 检查包含关系并添加边
for field in fields:
    for cause in causes:
        if contains_cause_keyword(field["field"], cause["name"]):
            # 创建关系
            rel = Relationship(field, "CONTAINS", cause)
            graph.create(rel)
            # print(f"{field['field']}包含{cause['name']}")
            fields_num+=1
        # else:
            # print(f"{field['field']} 不包含{cause['name']}")
            
styles = graph.nodes.match("Style").all()
causes = graph.nodes.match("Cause").all()
styles_num=0
# 检查包含关系并添加边
for style in styles:
    for cause in causes:
        if contains_cause_keyword(style["style"], cause["name"]):
            # 创建关系
            # print("包含")
            rel = Relationship(style, "CONTAINS", cause)
            graph.create(rel)
            # print(f"{style["style"]}包含{cause['name']}")
            styles_num+=1

sales = graph.nodes.match("Sales").all()
causes = graph.nodes.match("Cause").all()
sales_num=0
# 检查包含关系并添加边
for sale in sales:
    for cause in causes:
        if contains_cause_keyword(sale["sales"], cause["name"]):
            # 创建关系
            # print("包含")
            rel = Relationship(sale, "CONTAINS", cause)
            graph.create(rel)
            # print(f"{sale["sales"]}包含{cause['name']}")
            styles_num+=1
print("All checks completed.")


