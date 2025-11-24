import React, { useState, useEffect, useRef, useImperativeHandle, forwardRef } from 'react'; // 1. 引入 forwardRef 和 useImperativeHandle
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, MessageSquareText, Trash2, Settings, BrainCircuit, Loader2 } from 'lucide-react';
import { Conversation } from '../../hooks/useChatHistory';
import { ai } from '../../api';
import AIControl from '../AIControl'; // 1. 引入 AIControl
import AISettingsDialog from '../AISettingsDialog';
import toast from 'react-hot-toast';
import { useAI } from '../../contexts/AIContext';
import ConversationItem from './ConversationItem'; // 引入新组件

interface Props {
  conversations: Conversation[];
  activeConversationId: string | null;
  onSelect: (id: string) => void;
  onCreate: () => void;
  onDelete: (id: string) => void;
  widthPx?: number;
}

// --- 2. 定义暴露给父组件的 ref 类型 ---
export interface SidebarHandles {
  triggerPointsUpdate: () => Promise<void>;
}

const ConversationSidebar = forwardRef<SidebarHandles, Props>(({
  conversations,
  activeConversationId,
  onSelect,
  onCreate,
  onDelete,
  widthPx = 256,
}, ref) => {
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const { isAIInitialized, checkAIStatus } = useAI();
  const [poePoints, setPoePoints] = useState<number | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false); // 用一个更明确的状态名
  const [isPointsLoading, setIsPointsLoading] = useState(false); // 4. 新增加载状态
  
  // 2. 注意这里我们不再需要 settingsButtonRef 了，因为对话框由 AIControl 触发
  const controlRef = useRef<HTMLDivElement>(null);

  // --- 5. 改造 updatePoints 函数 ---
  const updatePoints = async () => {
    setIsPointsLoading(true); // 开始加载
    try {
      const data = await ai.getPoints();
      setPoePoints(data.points);
    } catch (error) {
      console.error("获取积分失败:", error);
      setPoePoints(null); // 出错了就清空
    } finally {
      setIsPointsLoading(false); // 结束加载
    }
  };

  // --- 6. 使用 useImperativeHandle 暴露方法 ---
  useImperativeHandle(ref, () => ({
    triggerPointsUpdate: updatePoints
  }));

  // 初始加载时不再需要自己检查，但当全局状态变化时，需要更新积分
  useEffect(() => {
    if (isAIInitialized) {
      updatePoints();
    } else {
      setPoePoints(null);
    }
  }, [isAIInitialized]);

  const handleSettingsSubmit = async (tokens: { pb_token: string; plat_token: string }) => {
    setIsSubmitting(true);
    try {
      await ai.initialize(tokens);
      toast.success("AI服务初始化成功！");
      await checkAIStatus(); // 刷新全局状态
    } catch (error) {
      toast.error("AI服务初始化失败，请检查Token。");
      throw error;
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggle = () => {
    // 核心逻辑：如果AI没初始化，点击开关就等于打开设置
    if (!isAIInitialized) {
      setIsSettingsOpen(true);
    }
    // 如果已经初始化了，这个开关实际上是“装饰性”的，因为服务一旦开启就无法通过前端关闭
    // 但我们可以保留这个点击行为，未来可以扩展为“暂停服务”等功能
    // 目前，如果已启用，点击它也会打开设置，方便用户更换Token
    else {
      setIsSettingsOpen(true);
    }
  };

  return (
    <div className="bg-gray-50/70 backdrop-blur-sm border-r flex flex-col h-full flex-shrink-0" style={{ width: widthPx }}>
      <div className="p-3 border-b flex items-center justify-between">
        <h2 className="font-semibold text-sm text-gray-700">对话列表</h2>
        <button onClick={onCreate} className="p-2 rounded-lg text-gray-500 hover:bg-gray-200 hover:text-gray-800 transition-colors" title="创建新对话">
          <Plus className="w-4 h-4" />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto p-2 space-y-1">
        <AnimatePresence>
          {conversations.map(convo => (
            <ConversationItem
              key={convo.id}
              convo={convo}
              isActive={activeConversationId === convo.id}
              onSelect={() => onSelect(convo.id)}
              onDelete={() => onDelete(convo.id)}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* --- 3. 底部区域大改造 --- */}
      <div className="p-3 border-t mt-auto space-y-3">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>Poe 积分</span>
          {/* --- 7. 加入加载动画 --- */}
          {isPointsLoading ? (
            <Loader2 className="w-3 h-3 animate-spin text-gray-400" />
          ) : isAIInitialized && poePoints !== null ? (
            <span className="font-semibold text-gray-700 flex items-center gap-1">
              <BrainCircuit className="w-3 h-3 text-green-500" /> {poePoints}
            </span>
          ) : (
            <span className="text-gray-400">N/A</span>
          )}
        </div>
        
        {/* --- C位主角登场！--- */}
        <div ref={controlRef}>
          <AIControl
            enabled={isAIInitialized}
            loading={isSubmitting}
            onToggle={handleToggle}
          />
        </div>
      </div>

      <AISettingsDialog
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSubmit={handleSettingsSubmit}
        buttonRef={controlRef} // 绑定新的 ref
      />
    </div>
  );
}); // --- 8. 闭合 forwardRef ---

export default ConversationSidebar;
