"""
旅游智能助手 - 基于LangChain的AI对话和简介生成模块
使用LangChain实现带记忆的对话管理和景点简介智能生成
"""
import os
import json
import random
from typing import List, Dict, Any, Optional

# LangChain核心组件
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_classic.memory import ConversationBufferMemory

# 景点简介生成提示词模板
SCENIC_INTRO_TEMPLATE = """你是一位资深旅游达人。请为景点"{scenic_name}"（位于{city}）撰写一段150字左右的简介。

景点标签：{tags}
景点类型：{scenic_type}

要求：
1. 语言生动有感染力，适合旅游宣传
2. 突出景点特色、历史底蕴或自然风光
3. 包含游览亮点和特色建议
4. 适合作为旅游宣传文案
"""

# 智能旅游问答系统提示词
TRAVEL_ASSISTANT_SYSTEM_PROMPT = """你是一位热情专业的旅游助手，专门帮助用户规划旅行、解答旅游相关问题。

你的职责：
1. 解答关于景点、美食���住宿、交通等旅游问题
2. 根据用户偏好推荐旅游景点和行程
3. 提供实用的旅行建议和注意事项
4. 帮助用户规划行程和预算

特点：
- 回答亲切友好，像朋友聊天一样
- 提供实用的建议和tips
- 适当引用用户之前提到的偏好
- 可以询问用户的具体需求以便更好推荐

如果用户的问题与旅游无关，可以礼貌地引导回到旅游话题。"""

# 行程规划对话提示词
ITINERARY_PLANNING_SYSTEM_PROMPT = """你是一位专业的旅行规划师，擅长根据用户需求定制个性化行程。

工作流程：
1. 先了解用户的基本信息（目的地、天数、人数、预算、偏好）
2. 根据信息推荐适合的景点和活动
3. 合理安排时间，确保行程既充实又不会太累
4. 提供交通、餐饮、住宿建议

回答风格：
- 专业但亲切
- 具体到景点名称和游览时长
- 适当给出时间建议
- 提醒注意事项和最佳游览时间

当信息不足时，你会主动询问用户。"""


class TravelChatManager:
    """旅游智能对话管理器"""
    
    def __init__(self):
        self.sessions: Dict[str, ConversationBufferMemory] = {}
        self.conversation_histories: Dict[str, List[Dict]] = {}
        # API地址：支持环境变量配置，默认使用chatanywhere
        self.api_base = os.environ.get('OPENAI_API_BASE', 'https://api.chatanywhere.tech/v1')
    
    def get_or_create_memory(self, session_id: str) -> ConversationBufferMemory:
        """获取或创建会话记忆"""
        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history"
            )
            self.conversation_histories[session_id] = []
        return self.sessions[session_id]
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """获取对话历史"""
        return self.conversation_histories.get(session_id, [])
    
    def chat(self, session_id: str, user_input: str, api_key: str, 
            model: str = "gpt-3.5-turbo", temperature: float = 0.7) -> str:
        """
        智能旅游问答（带记忆）
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            api_key: OpenAI API密钥
            model: 模型名称
            temperature: 创造性参数
        
        Returns:
            AI回复文本
        """
        if not api_key:
            return "请先配置您的AI API密钥才能使用智能问答功能。"
        
        # 获取会话记忆
        memory = self.get_or_create_memory(session_id)
        
        # 构建消息列表
        messages = [SystemMessage(content=TRAVEL_ASSISTANT_SYSTEM_PROMPT)]
        
        # 添加历史对话
        if hasattr(memory, 'chat_memory') and memory.chat_memory.messages:
            for msg in memory.chat_memory.messages:
                messages.append(msg)
        
        # 添加当前用户输入
        messages.append(HumanMessage(content=user_input))
        
        try:
            # 调用模型
            llm = ChatOpenAI(
                model=model,
                openai_api_key=api_key,
                openai_api_base=self.api_base,
                temperature=temperature
            )
            
            response = llm.invoke(messages)
            
            # 更新记忆
            memory.chat_memory.add_user_message(user_input)
            memory.chat_memory.add_ai_message(response.content)
            
            # 更新历史记录
            self.conversation_histories[session_id].append({
                'role': 'user',
                'content': user_input
            })
            self.conversation_histories[session_id].append({
                'role': 'ai', 
                'content': response.content
            })
            
            return response.content
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            # 常见错误处理
            if "api_key" in error_msg.lower() or "auth" in error_msg.lower():
                return f"API密钥无效或已过期，请检查您的API Key是否正确。"
            elif "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                return f"请求超时，网络连接不稳定，请稍后重试。"
            elif "connection" in error_msg.lower():
                return f"网络连接失败，请检查网络环境。"
            else:
                return f"服务出现问题：{error_msg}。请稍后再试。"
    
    def plan_itinerary_chat(self, session_id: str, user_input: str, api_key: str,
                           model: str = "gpt-3.5-turbo", temperature: float = 0.7) -> str:
        """
        行程规划对话（带记忆）
        
        Args:
            session_id: 会话ID
            user_input: 用户输入
            api_key: OpenAI API密钥
            model: 模型名称
            temperature: 创造性参数
        
        Returns:
            AI回复文本（行程建议）
        """
        if not api_key:
            return "请先配置您的AI API密钥才能使用行程规划功能。"
        
        memory = self.get_or_create_memory(f"itinerary_{session_id}")
        
        messages = [SystemMessage(content=ITINERARY_PLANNING_SYSTEM_PROMPT)]
        
        # 添加历史对话
        if hasattr(memory, 'chat_memory') and memory.chat_memory.messages:
            for msg in memory.chat_memory.messages:
                messages.append(msg)
        
        messages.append(HumanMessage(content=user_input))
        
        try:
            llm = ChatOpenAI(
                model=model,
                openai_api_key=api_key,
                openai_api_base=self.api_base,
                temperature=temperature
            )
            
            response = llm.invoke(messages)
            
            # 更新记忆
            memory.chat_memory.add_user_message(user_input)
            memory.chat_memory.add_ai_message(response.content)
            
            return response.content
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            if "api_key" in error_msg.lower() or "auth" in error_msg.lower():
                return f"API密钥无效或已过期，请检查您的API Key。"
            elif "timeout" in error_msg.lower():
                return f"请求超时，请稍后重试。"
            elif "connection" in error_msg.lower():
                return f"网络连接失败，请检查网络。"
            else:
                return f"行程规划出现问题：{error_msg}。"
    
    def reset_conversation(self, session_id: str):
        """重置对话"""
        if session_id in self.sessions:
            self.sessions[session_id] = ConversationBufferMemory(return_messages=True)
            self.conversation_histories[session_id] = []


class ScenicIntroGenerator:
    """景点简介生成器"""
    
    def __init__(self):
        self.api_base = os.environ.get('OPENAI_API_BASE', 'https://api.chatanywhere.tech/v1')
    
    def generate_intro(self, scenic_name: str, city: str, tags: str = "",
                       scenic_type: str = "景点", api_key: str = "",
                       model: str = "gpt-3.5-turbo") -> str:
        """
        生成景点AI简介
        
        Args:
            scenic_name: 景点名称
            city: 所在城市
            tags: 景点标签（逗号分隔）
            scenic_type: 景点类型
            api_key: API密钥
            model: 模型名称
        
        Returns:
            生成的简介文本
        """
        if not api_key:
            return "请先配置您的AI API密钥才能生成景点简介。"
        
        try:
            # 构建提示词
            prompt = SCENIC_INTRO_TEMPLATE.format(
                scenic_name=scenic_name,
                city=city,
                tags=tags or "热门景点",
                scenic_type=scenic_type
            )
            
            # 调用模型
            llm = ChatOpenAI(
                model=model,
                openai_api_key=api_key,
                openai_api_base=self.api_base,
                temperature=0.8  # 较高创造性，适合生成文案
            )
            
            response = llm.invoke([
                HumanMessage(content=prompt)
            ])
            
            return response.content
            
        except Exception as e:
            return f"生成简介失败：{str(e)}"


# 全局实例
travel_chat_manager = TravelChatManager()
scenic_intro_generator = ScenicIntroGenerator()


def get_travel_response(session_id: str, user_input: str, api_key: str,
                        chat_type: str = "qa", model: str = "gpt-3.5-turbo",
                        temperature: float = 0.7) -> str:
    """
    统一获取旅游AI响应接口
    
    Args:
        session_id: 会话ID
        user_input: 用户输入
        api_key: API密钥
        chat_type: 对话类型 ("qa"=问答, "itinerary"=行程规划)
        model: 模型名称
        temperature: 创造性参数
    
    Returns:
        AI响应文本
    """
    if chat_type == "itinerary":
        return travel_chat_manager.plan_itinerary_chat(
            session_id, user_input, api_key, model, temperature
        )
    else:
        return travel_chat_manager.chat(
            session_id, user_input, api_key, model, temperature
        )


def reset_travel_chat(session_id: str):
    """重置对话"""
    travel_chat_manager.reset_conversation(session_id)
