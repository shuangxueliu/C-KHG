#知识图谱+因果图
from py2neo import Graph
from config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

class Neo4jClient:
    def __init__(self):
        self.graph = Graph(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    def query_causal_relationship(self, cause, effect):
        query = f"""
        MATCH (cause:Node {{name: '{cause}'}})-[:CAUSES*]->(effect:Node {{name: '{effect}'}})
        RETURN cause.name AS Cause, effect.name AS Effect
        """
        result = self.graph.run(query)
        return [record for record in result]
    
    def query_chip_info(self, chip_name):
        query = f"""
        MATCH (a:Chip {{name: '{chip_name}'}})
        OPTIONAL MATCH (a)-[:HAS_FIELD]->(b:Field)
        OPTIONAL MATCH (a)-[:HAS_STYLE]->(c:Style)
        OPTIONAL MATCH (a)-[:PRODUCED_BY]->(d:Producer)
        OPTIONAL MATCH (a)-[:HAS_QUALITY_CONTROL]->(e:QualityControl)
        OPTIONAL MATCH (a)-[:HAS_SALES]->(f:Sales)
        // 捕获通过 Field/Style 连接到 Cause 的路径
        OPTIONAL MATCH (a)-[:HAS_FIELD|HAS_STYLE]->(middle)-[:CONTAINS]->(cause:Cause)
        // 从 Cause 到 Effect 的路径
        OPTIONAL MATCH (cause)-[:CAUSES]->(effect:Effect)
        RETURN a.name AS ChipName, b.field AS Field, c.style AS Style, d.producer AS Producer, 
               e.qualityControl AS QualityControl,
            COLLECT(DISTINCT f.sales) AS Sales,
            COLLECT(DISTINCT cause.name) AS Causes,      // 收集所有原因节点
            COLLECT(DISTINCT effect.name) AS Effects     // 收集所有影响节点
        """
        result = self.graph.run(query)
        return [record for record in result]