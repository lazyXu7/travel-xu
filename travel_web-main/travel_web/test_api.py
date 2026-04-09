import os
os.environ['http_proxy'] = 'http://127.0.0.1:7890'
os.environ['https_proxy'] = 'http://127.0.0.1:7890'

import httpx
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

proxy_url = 'http://127.0.0.1:7890'
http_client = httpx.Client(proxy=proxy_url, timeout=60.0, verify=False)

llm = ChatOpenAI(
    model='gpt-3.5-turbo',
    openai_api_key='sk-PchUepVEcPVNvV2O4xk9DCbuiONgBHZ4Cb38IuPilbWM945Z',
    openai_api_base='https://api.chatanywhere.tech/v1',
    temperature=0.7,
    http_client=http_client
)

try:
    response = llm.invoke([HumanMessage(content='你好')])
    print('Success:', response.content)
except Exception as e:
    print('Error:', type(e).__name__)
    print(str(e)[:500])


