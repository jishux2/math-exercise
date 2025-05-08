import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { User } from '../../api/types';  // 确保导入User类型
import { users } from '../../api';

const ParentDashboard = () => {
    // 明确指定查询返回的数据类型为User数组
    const { data: children = [], isLoading } = useQuery<User[], Error>({
      queryKey: ['parent-children'],
      queryFn: users.getParentStudents
    });
  
    if (isLoading) {
      return <div>Loading...</div>;
    }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">家长主页</h1>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="text-sm font-medium text-gray-500">关联学生</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">
              {children?.length || 0}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium">孩子列表</h2>
          <div className="mt-4">
            {children?.length ? (
              <ul className="divide-y divide-gray-200">
                {children.map((child: User) => (  // 明确指定child的类型
                  <li key={child.id} className="py-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {child.username}
                        </p>
                        <p className="text-sm text-gray-500 truncate">
                          {child.student_profile?.grade} {child.student_profile?.class_name}
                        </p>
                      </div>
                      <div>
                        <button className="bg-blue-500 text-white px-4 py-2 rounded-md text-sm">
                          查看详情
                        </button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500">暂未关联学生</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ParentDashboard;