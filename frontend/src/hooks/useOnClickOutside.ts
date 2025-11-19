// src/hooks/useOnClickOutside.ts
import { useEffect, RefObject } from 'react';

type Event = MouseEvent | TouchEvent;

// --- 核心修复点：修改函数的签名 ---
export const useOnClickOutside = (
  ref: RefObject<HTMLElement | null>, // 明确告诉它，ref.current 可以是 null
  handler: (event: Event) => void
) => {
  useEffect(() => {
    const listener = (event: Event) => {
      const el = ref?.current;
      // 这里的逻辑本身就是安全的，因为它已经检查了 el 是否存在
      if (!el || el.contains((event?.target as Node) || null)) {
        return;
      }
      handler(event);
    };

    document.addEventListener('mousedown', listener);
    document.addEventListener('touchstart', listener);

    return () => {
      document.removeEventListener('mousedown', listener);
      document.removeEventListener('touchstart', listener);
    };
  }, [ref, handler]);
};
