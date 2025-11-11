from typing import Optional, Dict, Any, List, AsyncIterator
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.orm import Session
from poe_api_wrapper import AsyncPoeApi

from ..core.poe_chat_model import PoeChatModel
from .tools import (
    GetExerciseStatsTool,
    GetRecentExercisesTool,
    GetExerciseDetailTool,
    AnalyzeLearningTrendTool,
    GetPoeAccountInfoTool,
    ListPoeBotsTool
)
from ..models import User


class AgentService:
    """智能体服务类"""
    
    def __init__(
        self,
        db: Session,
        current_user: User,
        poe_client: Optional[AsyncPoeApi] = None
    ):
        self.db = db
        self.current_user = current_user
        self.poe_client = poe_client
        self.chat_model: Optional[PoeChatModel] = None
        self.agent_executor: Optional[AgentExecutor] = None
    
    async def initialize(self, bot_name: str = "chinchilla") -> bool:
        """
        初始化智能体
        
        参数：
            bot_name: 使用的Poe机器人名称
            
        返回：
            是否初始化成功
        """
        if not self.poe_client:
            return False
        
        # 创建聊天模型
        self.chat_model = PoeChatModel(
            poe_client=self.poe_client,
            bot_name=bot_name
        )
        
        # 创建工具列表
        tools = [
            GetExerciseStatsTool(db=self.db, current_user=self.current_user),
            GetRecentExercisesTool(db=self.db, current_user=self.current_user),
            GetExerciseDetailTool(db=self.db, current_user=self.current_user),
            AnalyzeLearningTrendTool(db=self.db, current_user=self.current_user),
            GetPoeAccountInfoTool(poe_client=self.poe_client),
            ListPoeBotsTool(poe_client=self.poe_client)
        ]
        
        # 获取系统提示并嵌入模板
        # 使用f-string将system_prompt在创建时就替换掉，避免LangChain尝试填充不存在的变量
        system_prompt = self._get_system_prompt()
        
        # ReAct格式的提示模板
        # 注意：tools、tool_names、input、agent_scratchpad使用双大括号{{}}，这些由LangChain在运行时填充
        # 特别强调AI不要自己编造Observation，必须等待工具返回真实结果
        template = f'''{system_prompt}

你有以下工具可用：

{{tools}}

**严格遵循以下格式（每个字段单独一行）：**

Question: 用户的问题
Thought: 我的思考
Action: 工具名（只能是 {{tool_names}} 中的一个）
Action Input: 工具的输入参数
Observation: 等待系统自动填充
... (可以重复Thought/Action/Action Input/Observation)
Thought: 我现在知道最终答案了
Final Answer: 给用户的最终回复

**关键规则：**
1. 写完Action Input后，立即停止，等待Observation
2. 绝对不要自己编造Observation的内容
3. Observation会由系统自动填充
4. 每次只执行一个Action，看到Observation后再决定下一步

**正确流程：**
第一步：写Thought、Action、Action Input，然后停止
第二步：系统返回Observation
第三步：写新的Thought分析结果，决定继续Action还是给出Final Answer

现在开始：

Question: {{input}}
{{agent_scratchpad}}'''
        
        prompt = ChatPromptTemplate.from_template(template)
        
        # 创建ReACT智能体
        agent = create_react_agent(
            llm=self.chat_model,
            tools=tools,
            prompt=prompt
        )
        
        # 创建执行器，控制agent行为
        # max_iterations: 限制思考轮数，避免过度消耗API积分
        # early_stopping_method: 达到上限时的处理方式，"force"表示直接停止并返回当前结果
        # return_intermediate_steps: 保留中间推理过程，便于调试和观察agent的思考链路
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=3,
            early_stopping_method="force",
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        
        return True
    
    def _get_system_prompt(self) -> str:
        """获取系统提示"""
        return """你是一个智能学习助手，专门帮助学生分析数学练习情况并提供学习建议。

当用户提出问题时，请按照以下步骤思考：
1. 理解用户的需求
2. 确定需要使用哪些工具
3. 调用相应的工具获取信息
4. 基于获取的信息给出专业、友好的回答

回答时请注意：
- 使用友善、鼓励的语气
- 提供具体、可行的建议
- 突出学生的进步和优点
- 对于需要改进的地方，给出明确的练习方向"""
    
    async def chat(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        与智能体对话
        
        参数：
            message: 用户消息
            chat_history: 聊天历史（可选）
            
        返回：
            智能体的回复
        """
        if not self.agent_executor:
            raise ValueError("Agent not initialized. Call initialize() first.")
        
        # 准备输入
        agent_input = {
            "input": message,
        }
        
        # 如果有聊天历史，添加到输入中
        if chat_history:
            agent_input["chat_history"] = [
                HumanMessage(content=msg["content"]) if msg["role"] == "user"
                else SystemMessage(content=msg["content"])
                for msg in chat_history
            ]
        
        # 执行智能体
        result = await self.agent_executor.ainvoke(agent_input)
        
        return result["output"]
    
    async def chat_stream(
        self,
        message: str,
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncIterator[str]:
        """
        流式对话（如果支持的话）
        
        参数：
            message: 用户消息
            chat_history: 聊天历史
            
        返回：
            异步迭代器，逐步返回响应文本
        """
        # 注意：LangChain的AgentExecutor目前对流式支持有限
        # 这里先实现一个简单版本，后续可以优化
        
        response = await self.chat(message, chat_history)
        
        # 模拟流式输出
        words = response.split()
        for i, word in enumerate(words):
            if i > 0:
                yield " "
            yield word
    
    def reset(self):
        """重置智能体会话"""
        if self.chat_model:
            self.chat_model.reset_conversation()