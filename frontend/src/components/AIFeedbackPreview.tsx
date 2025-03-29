import React, { useState } from 'react';
import { Tab } from '@headlessui/react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';  // 添加GFM支持

interface Props {
  content: string;
  onClose: () => void;
}

export default function AIFeedbackPreview({ content, onClose }: Props) {
  const [selectedTab, setSelectedTab] = useState(0);

  // 预处理markdown内容，确保列表正确渲染
  const processContent = (content: string) => {
    return content
      // 确保有序列表前有空行
      .replace(/(\d+\.)/g, '\n$1')
      // 确保无序列表前有空行
      .replace(/([^\n])([-\*\+])/g, '$1\n$2')
      // 删除多余的空行
      .replace(/\n\s*\n\s*\n/g, '\n\n');
  };

  return (
    <div className="fixed inset-0 bg-white z-50 overflow-hidden flex flex-col">
      <div className="flex justify-between items-center px-6 py-4 border-b">
        <h2 className="text-xl font-semibold">AI点评预览</h2>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          关闭
        </button>
      </div>

      <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
        <Tab.List className="flex px-6 border-b">
          <Tab className={({ selected }) => `
            px-4 py-2 focus:outline-none
            ${selected 
              ? 'border-b-2 border-blue-500 text-blue-600' 
              : 'text-gray-500 hover:text-gray-700'
            }
          `}>
            富文本
          </Tab>
          <Tab className={({ selected }) => `
            px-4 py-2 focus:outline-none
            ${selected 
              ? 'border-b-2 border-blue-500 text-blue-600' 
              : 'text-gray-500 hover:text-gray-700'
            }
          `}>
            纯文本
          </Tab>
        </Tab.List>

        <Tab.Panels className="flex-1 overflow-auto">
          <Tab.Panel className="h-full">
            <div className="max-w-3xl mx-auto p-6">
              <article className="prose prose-sm sm:prose lg:prose-lg xl:prose-xl mx-auto">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    // 自定义列表渲染
                    ol: ({node, ...props}) => (
                      <ol className="list-decimal pl-4 my-2" {...props} />
                    ),
                    ul: ({node, ...props}) => (
                      <ul className="list-disc pl-4 my-2" {...props} />
                    ),
                    li: ({node, ...props}) => (
                      <li className="my-1" {...props} />
                    ),
                    p: ({node, ...props}) => (
                      <p className="my-2" {...props} />
                    ),
                  }}
                >
                  {content}
                </ReactMarkdown>
              </article>
            </div>
          </Tab.Panel>
          <Tab.Panel className="h-full">
            <pre className="p-6 font-mono text-sm whitespace-pre-wrap">
              {content}
            </pre>
          </Tab.Panel>
        </Tab.Panels>
      </Tab.Group>
    </div>
  );
}