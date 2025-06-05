import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { adminAPI } from '../../api/admin';
import { Admin, User, UserRole } from '../../api/types';
import { 
  UserGroupIcon, 
  ChartBarIcon, 
  CogIcon,
  AcademicCapIcon,
  UserIcon,
  UsersIcon
} from '@heroicons/react/24/outline';
import StatsCard from './components/StatsCard';
import TeachersList from './components/TeachersList';
import ParentsList from './components/ParentsList';
import AdminsList from './components/AdminsList';
import UserManagement from './components/UserManagement';
import SystemSettings from './components/SystemSettings';
import CreateTeacherForm from './components/CreateTeacherForm';
import CreateParentForm from './components/CreateParentForm';
import CreateAdminForm from './components/CreateAdminForm';
import UserRelationships from './components/UserRelationships';

interface SystemStats {
  totalStudents: number;
  totalTeachers: number;
  totalParents: number;
  activeExercises: number;
  completedExercises: number;
  averageScore: number;
}

const AdminDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  
  const { data: stats } = useQuery<SystemStats>({
    queryKey: ['admin-stats'],
    queryFn: () => adminAPI.getSystemStats()
  });

  const { data: teachers } = useQuery({
    queryKey: ['admin-teachers'],
    queryFn: () => adminAPI.getTeachers()
  });

  const { data: parents } = useQuery({
    queryKey: ['admin-parents'],
    queryFn: () => adminAPI.getParents()
  });

  const { data: admins = [] } = useQuery<Admin[]>({
    queryKey: ['admin-admins'],
    queryFn: async () => {
      const users = await adminAPI.getAdmins();
      return users.map(user => ({
        ...user,
        role: UserRole.ADMIN,
        is_superuser: user.admin_profile?.is_superuser || false,
        admin_profile: {
          permissions: user.admin_profile?.permissions || [],
          is_superuser: user.admin_profile?.is_superuser || false
        }
      })) as Admin[];
    }
  });

  const navigationItems = [
    { name: '概览', icon: ChartBarIcon, key: 'overview' },
    { name: '用户管理', icon: UserGroupIcon, key: 'users' },
    { name: '教师管理', icon: AcademicCapIcon, key: 'teachers' },
    { name: '家长管理', icon: UserIcon, key: 'parents' },
    { name: '管理员', icon: UsersIcon, key: 'admins' },
    { name: '用户关系', icon: UsersIcon, key: 'relationships' },
    { name: '系统设置', icon: CogIcon, key: 'settings' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">管理员控制台</h1>
        
        {/* Navigation Tabs */}
        <div className="flex space-x-4 mb-8">
          <nav className="space-x-4">
            {navigationItems.map(item => (
              <button
                key={item.key}
                onClick={() => setActiveTab(item.key)}
                className={`inline-flex items-center px-4 py-2 rounded-md text-sm font-medium
                  ${activeTab === item.key 
                    ? 'bg-indigo-100 text-indigo-700' 
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'}`}
              >
                <item.icon className="h-5 w-5 mr-2" />
                {item.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Overview Dashboard */}
        {activeTab === 'overview' && stats && (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <StatsCard
              title="总学生数"
              value={stats.totalStudents}
              icon={UserGroupIcon}
              trend={5}
            />
            <StatsCard
              title="总教师数"
              value={stats.totalTeachers}
              icon={AcademicCapIcon}
              trend={2}
            />
            <StatsCard
              title="总家长数"
              value={stats.totalParents}
              icon={UserIcon}
              trend={3}
            />
            <StatsCard
              title="活跃练习"
              value={stats.activeExercises}
              icon={ChartBarIcon}
              trend={10}
            />
            <StatsCard
              title="已完成练习"
              value={stats.completedExercises}
              icon={ChartBarIcon}
            />
            <StatsCard
              title="平均分数"
              value={stats.averageScore.toFixed(1)}
              icon={ChartBarIcon}
              suffix="%"
            />
          </div>
        )}

        {/* Teachers Management */}
        {activeTab === 'teachers' && (
          <div className="space-y-6">
            <CreateTeacherForm />
            <TeachersList teachers={teachers || []} />
          </div>
        )}

        {/* Parents Management */}
        {activeTab === 'parents' && (
          <div className="space-y-6">
            <CreateParentForm />
            <ParentsList parents={parents || []} />
          </div>
        )}

        {/* Admins Management */}
        {activeTab === 'admins' && (
          <div className="space-y-6">
            <CreateAdminForm />
            <AdminsList admins={admins || []} />
          </div>
        )}

        {/* User Management */}
        {activeTab === 'users' && (
          <UserManagement />
        )}

        {/* User Relationships */}
        {activeTab === 'relationships' && (
          <UserRelationships />
        )}

        {/* System Settings */}
        {activeTab === 'settings' && (
          <SystemSettings />
        )}
      </div>

    </div>
  );
};

export default AdminDashboard;
