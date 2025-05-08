import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth, getDefaultRoute } from './contexts/AuthContext';
import ProtectedRoute, { 
  StudentRoute, 
  TeacherRoute, 
  ParentRoute, 
  AdminRoute 
} from './components/auth/ProtectedRoute';  // 添加 ProtectedRoute

// 页面组件
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import CreateExercise from './pages/student/CreateExercise';
import Exercise from './pages/student/Exercise';
import TeacherDashboard from './pages/teacher/TeacherDashboard';
import ParentDashboard from './pages/parent/ParentDashboard';
import Profile from './pages/Profile';
import ExerciseHistory from './pages/student/ExerciseHistory';
import MyScores from './pages/student/MyScores';
import ExerciseResult from './pages/student/ExerciseResult';  // 添加导入

const queryClient = new QueryClient();

// 创建一个重定向组件
const DefaultRedirect = () => {
  const { user } = useAuth();
  return <Navigate to={getDefaultRoute(user?.role)} replace />;
};

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AuthProvider>
          <Routes>
            {/* 公共路由 */}
            <Route path="/login" element={<Login />} />

            {/* 需要认证的路由 */}
            <Route element={<Layout />}>
              {/* 根路径重定向 */}
              <Route index element={<DefaultRedirect />} />

              {/* 学生路由 */}
              <Route path="student">
                <Route
                  path="create-exercise"
                  element={
                    <StudentRoute>
                      <CreateExercise />
                    </StudentRoute>
                  }
                />
                <Route
                  path="exercise-history"
                  element={
                    <StudentRoute>
                      <ExerciseHistory />
                    </StudentRoute>
                  }
                />
                <Route
                  path="my-scores"
                  element={
                    <StudentRoute>
                      <MyScores />
                    </StudentRoute>
                  }
                />
                <Route
                  path="exercise/:id"
                  element={
                    <StudentRoute>
                      <Exercise />
                    </StudentRoute>
                  }
                />
                <Route
                  path="result/:id"
                  element={
                    <StudentRoute>
                      <ExerciseResult />
                    </StudentRoute>
                  }
                />
              </Route>

              {/* 教师路由 */}
              <Route path="teacher">
                <Route
                  path="dashboard"
                  element={
                    <TeacherRoute>
                      <TeacherDashboard />
                    </TeacherRoute>
                  }
                />
                {/* 其他教师路由... */}
              </Route>

              {/* 家长路由 */}
              <Route path="parent">
                <Route
                  path="dashboard"
                  element={
                    <ParentRoute>
                      <ParentDashboard />
                    </ParentRoute>
                  }
                />
                {/* 其他家长路由... */}
              </Route>

              {/* 个人资料路由 */}
              <Route
                path="profile"
                element={
                  <ProtectedRoute>
                    <Profile />
                  </ProtectedRoute>
                }
              />

              {/* 通配符路由重定向 */}
              <Route path="*" element={<DefaultRedirect />} />
            </Route>
          </Routes>
        </AuthProvider>
      </Router>
    </QueryClientProvider>
  );
};

export default App;