// src/components/AIControl.tsx
import type { FC } from 'react';
import { Switch } from '@headlessui/react';
import { Sparkles, Loader2 } from 'lucide-react'; // 引入 Loader2
import { motion } from 'framer-motion';

interface AIControlProps {
  enabled: boolean;
  loading?: boolean;
  disabled?: boolean; // 新增 disabled 状态
  onToggle: () => void;
}

const AIControl: FC<AIControlProps> = ({ enabled, loading = false, disabled = false, onToggle }) => {
  const getLabel = () => {
    if (loading) return '检查状态...';
    if (disabled) return 'AI服务未配置';
    return enabled ? 'AI服务已启用' : 'AI服务已禁用';
  };

  return (
    <div className="flex items-center gap-2">
      <span className={`
        text-sm font-medium transition-colors duration-300
        ${loading || disabled ? 'text-gray-400' : (enabled ? 'text-blue-500' : 'text-gray-500')}
      `}>
        {getLabel()}
      </span>

      <Switch
        checked={enabled}
        onChange={onToggle}
        disabled={loading || disabled}
        className={`
          relative inline-flex h-8 w-14 items-center rounded-full
          transition-colors duration-300 ease-in-out
          focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500
          ${loading || disabled ? 'cursor-not-allowed' : 'cursor-pointer'}
          ${enabled ? 'bg-blue-500' : 'bg-gray-200'}
          ${disabled ? 'opacity-50' : ''}
        `}
      >
        <span
          className={`
            absolute left-1
            flex h-6 w-6 items-center justify-center
            rounded-full bg-white
            transition-transform duration-300
            ${enabled ? 'translate-x-6' : 'translate-x-0'}
          `}
        >
          {loading ? (
            <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
          ) : (
            <Sparkles
              className={`w-3 h-3 transition-colors duration-300 ${
                enabled && !disabled ? 'text-blue-500' : 'text-gray-400'
              }`}
            />
          )}
        </span>
      </Switch>
    </div>
  );
};

export default AIControl;
