import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { users } from '../../api';

const TeacherDashboard = () => {
  const { data: students, isLoading } = useQuery({
    queryKey: ['teacher-students'],
    queryFn: users.getTeacherStudents
  });

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">教师主页</h1>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="text-sm font-medium text-gray-500">学生总数</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">
              {students?.length || 0}
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="text-sm font-medium text-gray-500">今日完成练习</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">0</div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="text-sm font-medium text-gray-500">平均正确率</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">0%</div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium">最近活动</h2>
          <div className="mt-4">
            {/* 这里添加活动列表 */}
            <p className="text-gray-500">暂无活动</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;