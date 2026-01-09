from xinference.client import RESTfulClient
from config import XINFERENCE_ENDPOINT, XINFERENCE_MODEL_NAME

class XinferenceClient:
    def __init__(self):
        self.client = RESTfulClient(XINFERENCE_ENDPOINT)
        self.model = self.client.get_model(XINFERENCE_MODEL_NAME)
    
    def chat(self, prompt, system_prompt="您是汽车芯片设计和生产领域的专家。您的任务是严格根据下面提供的信息生成清晰且技术上准确的答案。不要引入超出给定内容的外部知识或假设。"):
        # system_prompt="You are a domain expert in automotive chip design and production. Your task is to generate a clear and technically accurate answer based strictly on the information provided below. Do not introduce external knowledge or assumptions beyond the given content."
        response = self.model.chat(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            generate_config={"max_tokens": 1024}
        )
        
        return response["choices"][0]["message"]["content"].strip()