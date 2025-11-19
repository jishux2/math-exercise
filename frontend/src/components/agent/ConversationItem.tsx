// src/components/agent/ConversationItem.tsx
import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquareText, Trash2 } from 'lucide-react';
import { useTypewriter } from '../../hooks/useTypewriter';
import { Conversation } from '../../hooks/useChatHistory';

interface Props {
  convo: Conversation;
  isActive: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

const ConversationItem: React.FC<Props> = ({ convo, isActive, onSelect, onDelete }) => {
  // 只有当这个对话是“新的对话”且不是当前激活的对话时，我们才使用打字机效果的初始状态
  // 一旦它被命名或被激活，就直接显示完整标题
  const isNewlyNamed = convo.title !== '新的对话';
  const animatedTitle = useTypewriter(isNewlyNamed ? convo.title : '新的对话', 50);

  return (
    <motion.div
      key={convo.id}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.2 }}
      className={`group w-full flex items-center justify-between p-2.5 rounded-lg cursor-pointer text-sm transition-colors relative ${
        isActive ? 'bg-white shadow-sm' : 'text-gray-600 hover:bg-gray-200/60'
      }`}
      onClick={onSelect}
    >
      {isActive && (
        <motion.div 
          layoutId="active-convo-indicator" 
          className="absolute left-0 top-0 bottom-0 w-1 bg-blue-500 rounded-l-lg"
          transition={{ type: "spring", damping: 25, stiffness: 250 }}
        />
      )}
      
      <MessageSquareText className="w-4 h-4 flex-shrink-0 ml-1" />
      <div className="flex-1 overflow-hidden mx-2">
        {/* 使用打字动画的标题 */}
        <p className="truncate font-medium">{animatedTitle}</p>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className="opacity-0 group-hover:opacity-100 text-gray-400 hover:text-red-500 p-1 flex-shrink-0"
      >
        <Trash2 className="w-4 h-4" />
      </button>
    </motion.div>
  );
};

export default ConversationItem;
