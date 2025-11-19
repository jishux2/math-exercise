// src/contexts/AIContext.tsx
import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';
import { ai } from '../api';

interface AIContextType {
  isAIInitialized: boolean;
  checkAIStatus: () => Promise<void>;
}

const AIContext = createContext<AIContextType | undefined>(undefined);

export const AIProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAIInitialized, setIsAIInitialized] = useState(false);

  const checkAIStatus = useCallback(async () => {
    try {
      const status = await ai.getStatus();
      setIsAIInitialized(status.is_initialized);
    } catch (error) {
      console.error("检查AI状态失败:", error);
      setIsAIInitialized(false);
    }
  }, []);

  return (
    <AIContext.Provider value={{ isAIInitialized, checkAIStatus }}>
      {children}
    </AIContext.Provider>
  );
};

export const useAI = () => {
  const context = useContext(AIContext);
  if (context === undefined) {
    throw new Error('useAI 必须在 AIProvider 内部使用');
  }
  return context;
};
