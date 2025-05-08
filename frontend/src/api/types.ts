export enum UserRole {
  STUDENT = "student",
  TEACHER = "teacher",
  PARENT = "parent",
  ADMIN = "admin"
}

export interface Question {
  id: number;
  exercise_id: number;
  content: string;
  correct_answer: number;
  user_answer?: number;
  time_spent?: number;
  operator_types: string[];
  arithmetic_tree?: any;  // 或者定义更具体的类型
  is_correct: boolean;
}

export interface Exercise {
  id: number;
  user_id: number;
  difficulty: string;
  number_range: [number, number];
  operator_types: string[];
  created_at: string;
  completed_at?: string;
  final_score?: number;
  total_time?: number;
  ai_feedback?: string;
  questions: Question[];
}

export interface ExerciseListResponse {
  total: number;
  exercises: Exercise[];
  page: number;
  page_size: number;
}

export interface ExerciseStats {
  total_exercises: number;
  completed_exercises: number;
  average_score: number;
  accuracy_rate: number;
  score_history: Array<{
    date: string;
    score: number;
  }>;
}

export interface StudentProfile {
  grade: string;
  class_name: string;
}

export interface TeacherProfile {
  subjects: string[];
}

export interface User {
  id: number;
  email: string;
  username: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  
  // 角色特定的配置信息
  student_profile?: StudentProfile;    // 仅当role为STUDENT时存在
  teacher_profile?: TeacherProfile;    // 仅当role为TEACHER时存在
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface UserResponse {
  success: boolean;
  user: User;
}

export interface ErrorResponse {
  success: boolean;
  error: string;
  error_code?: string;
  details?: string | string[] | Record<string, any>;
}