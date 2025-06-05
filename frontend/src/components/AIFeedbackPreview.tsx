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

  return (
    <div className="fixed inset-0 bg-white z-50 flex flex-col overflow-hidden">
      {/* 头部栏 */}
      <div className="shrink-0 flex justify-between items-center px-6 py-4 border-b bg-white">
        <h2 className="text-xl font-semibold">AI点评预览</h2>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-100"
        >
          关闭
        </button>
      </div>

      {/* Tab栏 */}
      <div className="shrink-0">
        <Tab.Group selectedIndex={selectedTab} onChange={setSelectedTab}>
          <Tab.List className="flex px-6 border-b bg-white">
            <Tab className={({ selected }) => `
              px-4 py-2 focus:outline-none whitespace-nowrap
              ${selected 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
              }
            `}>
              富文本
            </Tab>
            <Tab className={({ selected }) => `
              px-4 py-2 focus:outline-none whitespace-nowrap
              ${selected 
                ? 'border-b-2 border-blue-500 text-blue-600' 
                : 'text-gray-500 hover:text-gray-700'
              }
            `}>
              纯文本
            </Tab>
          </Tab.List>

          {/* 内容区域 */}
          <Tab.Panels className="flex-1 h-[calc(100vh-8rem)] overflow-auto">
            <Tab.Panel className="h-full overflow-y-auto">
              <div className="max-w-4xl mx-auto p-6">
                <div className="flex justify-center w-full">
                  <article className="prose prose-sm prose-slate sm:prose-sm md:prose-base lg:prose">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        ol: ({node, ...props}) => (
                          <ol className="list-decimal pl-4 my-2 space-y-2" {...props} />
                        ),
                        ul: ({node, ...props}) => (
                          <ul className="list-disc pl-4 my-2 space-y-2" {...props} />
                        ),
                        li: ({node, children, ...props}) => (
                          <li className="my-1" {...props}>
                            {children}
                          </li>
                        ),
                        p: ({node, ...props}) => (
                          <p className="my-2 leading-relaxed" {...props} />
                        ),
                        table: ({node, ...props}) => (
                          <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200 my-4" {...props} />
                          </div>
                        ),
                        th: ({node, ...props}) => (
                          <th className="px-3 py-2 bg-gray-50 text-left text-sm font-semibold text-gray-600" {...props} />
                        ),
                        td: ({node, ...props}) => (
                          <td className="px-3 py-2 text-sm text-gray-500 border-t" {...props} />
                        ),
                      }}
                    >
                      {content}
                    </ReactMarkdown>
                  </article>
                </div>
              </div>
            </Tab.Panel>
            <Tab.Panel className="h-full overflow-y-auto">
              <pre className="p-6 font-mono text-sm whitespace-pre-wrap max-w-4xl mx-auto">
                {content}
              </pre>
            </Tab.Panel>
          </Tab.Panels>
        </Tab.Group>
      </div>
    </div>
  );
}