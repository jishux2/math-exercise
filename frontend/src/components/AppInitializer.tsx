// src/components/AppInitializer.tsx
import { useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useAI } from '../contexts/AIContext';

// 这个组件没有UI，它只在后台工作
const AppInitializer: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const { checkAIStatus } = useAI();

  useEffect(() => {
    // 监听用户认证状态
    if (isAuthenticated) {
      // 一旦用户通过认证，就立即检查AI服务的状态
      console.log("用户已认证，开始检查AI状态...");
      checkAIStatus();
    }
  }, [isAuthenticated, checkAIStatus]); // 当认证状态变化时触发

  return <>{children}</>;
};

export default AppInitializer;
