import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { getTeacherStats } from '../../api/teacher';
import type { TeacherStats } from '../../api/teacher';

const TeacherDashboard = () => {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['teacher-stats'],
    queryFn: getTeacherStats
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">教师主页</h1>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="text-sm font-medium text-gray-500">学生总数</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">
              {stats?.total_students || 0}
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="text-sm font-medium text-gray-500">今日完成练习</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">
              {stats?.exercises_today || 0}
            </div>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="text-sm font-medium text-gray-500">平均得分</div>
            <div className="mt-1 text-3xl font-semibold text-gray-900">
              {stats ? `${(stats.average_accuracy * 100).toFixed(1)}` : '0'}
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h2 className="text-lg font-medium">最近活动</h2>
          <div className="mt-4">
            {stats?.recent_activities && stats.recent_activities.length > 0 ? (
              <ul className="divide-y divide-gray-200">
                {stats.recent_activities.map((activity) => (
                  <li key={activity.id} className="py-4">
                    <div className="flex space-x-3">
                      <div className="flex-1">
                        <p className="text-sm font-medium text-gray-900">
                          {activity.student_name}
                        </p>
                        <p className="text-sm text-gray-500">
                          完成练习 #{activity.id} - 得分: {activity.score}
                        </p>
                        <p className="text-xs text-gray-400">
                          {new Date(activity.completed_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-gray-500">暂无活动</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeacherDashboard;
