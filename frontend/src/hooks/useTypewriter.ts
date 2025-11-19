// src/hooks/useTypewriter.ts
import { useState, useEffect, useRef } from 'react';

export const useTypewriter = (text: string, speed: number = 50) => {
  const [displayText, setDisplayText] = useState('');
  // 使用 ref 来存储当前打字的索引，避免闭包问题
  const index = useRef(0);

  useEffect(() => {
    // 当 text 变化时，重置所有状态
    setDisplayText('');
    index.current = 0;

    const timerId = setInterval(() => {
      // 从 ref 中读取当前的索引
      const currentIndex = index.current;

      if (currentIndex < text.length) {
        // 使用函数式更新，确保我们总是基于最新的状态进行修改
        setDisplayText(prev => prev + text[currentIndex]);
        // 更新 ref 中的索引
        index.current += 1;
      } else {
        clearInterval(timerId);
      }
    }, speed);

    // 清理函数
    return () => {
      clearInterval(timerId);
    };
  }, [text, speed]); // 依赖项保持不变

  return displayText;
};
