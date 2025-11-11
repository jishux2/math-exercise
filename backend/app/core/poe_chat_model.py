from typing import Any, List, Optional, Iterator, AsyncIterator, Dict
from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage, AIMessageChunk
from langchain_core.outputs import ChatGeneration, ChatResult, ChatGenerationChunk
import asyncio
from poe_api_wrapper import AsyncPoeApi


class PoeChatModel(BaseChatModel):
    """
    Poe API的LangChain聊天模型包装
    
    这个类将AsyncPoeApi封装成LangChain标准的聊天模型接口，
    使其可以与LangChain的Agent框架无缝集成
    """
    
    # Poe客户端实例（用户级别）
    poe_client: Optional[AsyncPoeApi] = None
    # 使用的bot名称
    bot_name: str = "chinchilla"
    # 当前对话的chatCode（用于保持会话连续性）
    chat_code: Optional[str] = None
    # 当前对话的chatId
    chat_id: Optional[int] = None
    # 是否启用流式输出
    streaming: bool = False
    
    class Config:
        arbitrary_types_allowed = True
    
    @property
    def _llm_type(self) -> str:
        """返回模型类型标识"""
        return "poe"
    
    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """返回标识参数"""
        return {
            "bot_name": self.bot_name,
            "model_name": self.bot_name
        }
    
    def _convert_messages_to_prompt(self, messages: List[BaseMessage]) -> str:
        """
        将LangChain消息列表转换为Poe API可接受的prompt
        
        LangChain的agent会将完整上下文（包括系统提示、历史对话、格式说明等）
        打包成一条HumanMessage，因此直接取第一条消息的内容即可
        """
        return messages[0].content if messages else ""
    
    def _handle_stop_sequences(self, text: str, stop: Optional[List[str]]) -> str:
        """
        处理stop sequences，截断文本
        
        参数：
            text: 完整的响应文本
            stop: stop序列列表
            
        返回：
            截断后的文本
        """
        if not stop:
            return text
        
        # 找到最早出现的stop序列
        min_index = len(text)
        for stop_seq in stop:
            index = text.find(stop_seq)
            if index != -1 and index < min_index:
                min_index = index
        
        return text[:min_index] if min_index < len(text) else text
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        异步生成响应（核心方法）
        
        这是LangChain要求实现的主要方法，负责调用Poe API并返回结果
        """
        if not self.poe_client:
            raise ValueError("Poe client not initialized. Call initialize() first.")
        
        # 获取完整的prompt内容
        prompt = messages[0].content if messages else ""
        
        # 调用Poe API获取响应
        # 注意：chatId和chatCode设为None，每次创建新对话
        # 这样可以避免LangChain重复发送完整上下文导致的积分浪费
        full_response = ""
        try:
            async for chunk in self.poe_client.send_message(
                bot=self.bot_name,
                message=prompt,
                chatId=None,  # 不复用对话，每次独立请求
                chatCode=None,
                timeout=30
            ):
                full_response = chunk.get("text", "")
                
                if chunk.get("state") == "complete":
                    break
        
        except Exception as e:
            raise RuntimeError(f"Failed to generate response from Poe: {str(e)}")
        
        # 处理stop sequences
        full_response = self._handle_stop_sequences(full_response, stop)
        
        # 封装返回结果
        message = AIMessage(content=full_response)
        return ChatResult(generations=[ChatGeneration(message=message)])
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """
        同步生成响应（通过异步方法实现）
        """
        return asyncio.run(self._agenerate(messages, stop, run_manager, **kwargs))
    
    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        """
        异步流式生成（可选实现）
        
        逐步返回生成的内容，提升用户体验
        LangChain会优先调用此方法而非_agenerate
        """
        if not self.poe_client:
            raise ValueError("Poe client not initialized. Call initialize() first.")
        
        prompt = messages[0].content if messages else ""
        
        try:
            # 每次创建新对话，原因同_agenerate
            async for chunk in self.poe_client.send_message(
                bot=self.bot_name,
                message=prompt,
                chatId=None,
                chatCode=None,
                timeout=30
            ):
                response_chunk = chunk.get("response", "")
                if response_chunk:
                    # 使用AIMessageChunk而非AIMessage，这是流式输出所需的特殊类型
                    message = AIMessageChunk(content=response_chunk)
                    yield ChatGenerationChunk(message=message)
                
                if chunk.get("state") == "complete":
                    break
        
        except Exception as e:
            raise RuntimeError(f"Failed to stream response from Poe: {str(e)}")
    
    def reset_conversation(self):
        """
        重置对话状态，开始新的会话
        
        注意：当前实现每次都创建新对话，所以这个方法实际上不需要做什么
        保留此方法是为了保持接口的完整性
        """
        self.chat_code = None
        self.chat_id = None