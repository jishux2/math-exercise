import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Login from './pages/Login';
import CreateExercise from './pages/CreateExercise';
import Exercise from './pages/Exercise';
import ExerciseResult from './pages/ExerciseResult';  // 添加导入
import MarkdownTest from './pages/MarkdownTest';  // 添加这行

const queryClient = new QueryClient();

// 受保护的路由组件
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/create-exercise"
        element={
          <ProtectedRoute>
            <CreateExercise />
          </ProtectedRoute>
        }
      />
      <Route
        path="/exercise/:id"
        element={
          <ProtectedRoute>
            <Exercise />
          </ProtectedRoute>
        }
      />
      {/* 添加结果页面路由 */}
      <Route
        path="/result/:id"
        element={
          <ProtectedRoute>
            <ExerciseResult />
          </ProtectedRoute>
        }
      />
      <Route path="/" element={<Navigate to="/create-exercise" replace />} />
      <Route path="/markdown-test" element={<MarkdownTest />} />
    </Routes>
  );
};

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
