# app/services/ai_service.py

from typing import Optional, Dict, AsyncGenerator
from datetime import datetime
import asyncio

class AIService:
    # 使用字典存储用户级别的实例
    _user_instances: Dict[int, 'AIService'] = {}
    
    @classmethod
    def get_instance(cls, user_id: int) -> 'AIService':
        """获取指定用户的AI服务实例（保持同步，因为只是获取实例）"""
        # 这部分保持不变
        print(f"\n{'='*50}")
        print(f"正在获取用户{user_id}的AI服务实例")
        print(f"当前所有实例: {[uid for uid in cls._user_instances.keys()]}")
        
        if user_id not in cls._user_instances:
            print(f"用户{user_id}的实例不存在，创建新实例")
            new_instance = cls(user_id)
            print(f"新实例ID: {id(new_instance)}")
            cls._user_instances[user_id] = new_instance
            print(f"已将新实例添加到实例字典中")
        else:
            print(f"用户{user_id}的实例已存在")
            print(f"现有实例ID: {id(cls._user_instances[user_id])}")
            print(f"实例状态: poe_client={'已初始化' if cls._user_instances[user_id].poe_client else '未初始化'}")
        
        instance = cls._user_instances[user_id]
        print(f"返回实例ID: {id(instance)}")
        print(f"{'='*50}\n")
        return instance
    
    @classmethod
    def remove_instance(cls, user_id: int) -> None:
        """移除指定用户的AI服务实例"""
        if user_id in cls._user_instances:
            del cls._user_instances[user_id]

    def __init__(self, user_id: int):
        self.user_id = user_id
        self.poe_client = None  # 现在会是AsyncPoeApi实例
        self._tokens: Dict[str, str] = {}
        self.last_used = datetime.utcnow()
        self._generation_cancelled = False  # 用于取消生成的标志

    async def initialize_client(self, pb_token: str, plat_token: str) -> bool:
        """初始化poe客户端（异步版本）"""
        try:
            from poe_api_wrapper import AsyncPoeApi
            self._tokens = {
                "p-b": pb_token,
                "p-lat": plat_token,
            }
            # 使用异步API并创建客户端实例
            self.poe_client = await AsyncPoeApi(tokens=self._tokens, auto_proxy=True).create()
            self.last_used = datetime.utcnow()
            print(f"用户{self.user_id}的AI客户端初始化成功")
            return True
        except Exception as e:
            print(f"用户{self.user_id}初始化AI客户端失败: {str(e)}")
            self.poe_client = None
            return False

    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        available = self.poe_client is not None
        print(f"AI服务状态: {'可用' if available else '不可用'}")  # 添加调试信息
        return available

    def cancel_generation(self):
        """标记取消生成"""
        self._generation_cancelled = True

    def reset(self):
        """重置状态"""
        self._generation_cancelled = False

    async def generate_feedback_stream(
        self,
        exercise: 'ExerciseResponse',
        feedback_type: str = "detailed"
    ) -> AsyncGenerator[dict, None]:
        """生成练习反馈（异步流式版本）"""
        if not self.is_available():
            yield {"error": "AI服务不可用"}
            return

        prompt = self._build_feedback_prompt(exercise, feedback_type)
        self._generation_cancelled = False  # 重置取消标志
        
        try:
            # 使用异步API的send_message
            async for chunk in self.poe_client.send_message("chinchilla", prompt):
                if self._generation_cancelled:
                    # 如果需要取消，调用API的cancel方法
                    await self.poe_client.cancel_message(chunk)
                    yield {"status": "cancelled"}
                    return
                
                # 从chunk中提取响应文本
                response_text = chunk.get("response", "")
                if response_text:  # 只在有实际内容时才yield
                    yield {"chunk": response_text}
                    
        except Exception as e:
            print(f"生成反馈失败: {str(e)}")
            yield {"error": str(e)}

    def _build_feedback_prompt(
        self,
        exercise: 'ExerciseResponse',
        feedback_type: str
    ) -> str:
        """构建反馈提示（这部分逻辑不变）"""
        # 保持原有实现不变
        system_prompt = """System: 你现在是一位经验丰富的小学数学老师。请注意以下要求：

1. 语气要求：
   - 使用友善、鼓励的语气
   - 重点强调学生的进步空间
   - 避免过于严厉或消极的评价

2. 格式要求：
   - 对于无序列表，所有子内容必须缩进2个空格，如：
     - 子项目1
     - 子项目2
   - 对于有序列表，所有子内容必须缩进3个空格，如：
     1. 第一项
        这是第一项的详细内容
        继续第一项的内容
     2. 第二项
        这是第二项的详细内容

3. 内容结构：
   1. 整体表现评价
      分析完成度、正确率、用时情况等
   2. 存在的问题分析
      指出错题特征、解题思路问题等
   3. 针对性的改进建议
      提供具体可行的练习方法和提高策略"""

        # 构建练习信息部分
        exercise_info = """
练习信息：
| 项目 | 内容 |
|------|------|
| 难度级别 | {} |
| 数值范围 | {} 到 {} |
| 运算类型 | {} |
| 总用时 | {}秒 |
| 最终得分 | {} |""".format(
            exercise.difficulty.value,  # 使用.value获取枚举值
            exercise.number_range[0],
            exercise.number_range[1],
            ', '.join(op.value for op in exercise.operator_types),
            exercise.total_time if exercise.total_time else 0,
            exercise.final_score if exercise.final_score is not None else '未完成'
        )

        # 构建题目记录表格
        questions_table = """
具体题目记录：
| 题号 | 题目内容 | 用户答案 | 正确答案 | 用时(秒) | 是否正确 |
|------|----------|----------|-----------|-----------|----------|"""
        
        for idx, q in enumerate(exercise.questions, 1):
            is_correct = (
                q.user_answer is not None and 
                abs(float(q.correct_answer) - float(q.user_answer)) < 0.001
            )
            questions_table += "\n| {} | {} | {} | {} | {} | {} |".format(
                idx,
                q.content,
                q.user_answer if q.user_answer is not None else '未作答',
                q.correct_answer,
                q.time_spent if q.time_spent else 0,
                '是' if is_correct else '否'
            )

        # 拼接完整提示词
        prompt = f"""{system_prompt}

{exercise_info}
{questions_table}

User: 请针对上述练习情况进行{'详细' if feedback_type == 'detailed' else '简要'}点评。"""

        return prompt


class AIServiceManager:
    # AIServiceManager的实现保持不变
    def __init__(self, cleanup_interval: int = 3600, max_idle_time: int = 7200):
        self.cleanup_interval = cleanup_interval  # 清理间隔（秒）
        self.max_idle_time = max_idle_time  # 最大空闲时间（秒）
        self.running = False
        self.cleanup_task = None

    async def start(self):
        """启动清理任务"""
        self.running = True
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """停止清理任务"""
        self.running = False
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass

    async def _cleanup_loop(self):
        """定期清理过期的服务实例"""
        while self.running:
            try:
                self._cleanup_expired_instances()
                await asyncio.sleep(self.cleanup_interval)
            except Exception as e:
                print(f"清理AI服务实例时出错: {str(e)}")

    def _cleanup_expired_instances(self):
        """清理过期的实例"""
        now = datetime.utcnow()
        expired_users = [
            user_id
            for user_id, instance in AIService._user_instances.items()
            if (now - instance.last_used).total_seconds() > self.max_idle_time
        ]
        for user_id in expired_users:
            AIService.remove_instance(user_id)
            print(f"已清理用户{user_id}的过期AI服务实例")