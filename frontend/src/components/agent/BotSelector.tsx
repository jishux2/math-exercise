// src/components/agent/BotSelector.tsx
import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion'; // 引入 AnimatePresence
import { ChevronDown, Check } from 'lucide-react';
import { bots } from '../../api';
import { useOnClickOutside } from '../../hooks/useOnClickOutside'; // 引入新 Hook

interface Bot {
  handle: string;
  displayName: string;
  description: string;
  avatarUrl: string;
}

interface Props {
  selectedBot: Bot;
  onSelect: (bot: Bot) => void;
}

const BotSelector: React.FC<Props> = ({ selectedBot, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [botList, setBotList] = useState<Bot[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // 创建一个 ref 来引用选择器的根元素
  const selectorRef = useRef<HTMLDivElement>(null);

  // 使用 Hook，当点击外部时，关闭列表
  useOnClickOutside(selectorRef, () => setIsOpen(false));

  useEffect(() => {
    // 只在列表打开时才获取数据，避免不必要的请求
    if (isOpen && botList.length === 0) {
      const fetchBots = async () => {
        setIsLoading(true);
        try {
          const initialBots = await bots.getList(50);
          setBotList(initialBots);
        } catch (error) {
          console.error("获取机器人列表失败:", error);
        } finally {
          setIsLoading(false);
        }
      };
      fetchBots();
    }
  }, [isOpen, botList.length]);

  return (
    <div className="relative" ref={selectorRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-200 transition-colors w-full text-left"
      >
        <img src={selectedBot.avatarUrl} alt={selectedBot.displayName} className="w-6 h-6 rounded-full" />
        <span className="font-semibold text-gray-800 text-sm">{selectedBot.displayName}</span>
        <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95, transition: { duration: 0.15 } }}
            transition={{ type: 'spring', damping: 20, stiffness: 300 }}
            className="absolute top-full mt-2 w-64 max-h-80 overflow-y-auto bg-white border rounded-lg shadow-xl p-2 z-20"
          >
            {isLoading ? (
              <div className="text-center p-4 text-gray-500">加载中...</div>
            ) : (
              botList.map(bot => (
                <div
                  key={bot.handle}
                  onClick={() => {
                    onSelect(bot);
                    setIsOpen(false);
                  }}
                  className="flex items-center justify-between p-2 rounded-md hover:bg-gray-100 cursor-pointer"
                >
                  <div className="flex items-center gap-2">
                    <img src={bot.avatarUrl} alt={bot.displayName} className="w-6 h-6 rounded-full" />
                    <span className="text-sm">{bot.displayName}</span>
                  </div>
                  {selectedBot.handle === bot.handle && <Check className="w-4 h-4 text-blue-500" />}
                </div>
              ))
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default BotSelector;
