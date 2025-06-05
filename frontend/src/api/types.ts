export enum UserRole {
  STUDENT = "student",
  TEACHER = "teacher",
  PARENT = "parent",
  ADMIN = "admin"
}

export interface BaseUser {
  id: number;
  email: string;
  username: string;
  is_active: boolean;
  role: UserRole;
}

export interface User extends BaseUser {
  is_superuser?: boolean;
  student_profile?: {
    grade: string;
    class_name: string;
  };
  teacher_profile?: {
    subjects: string[];
  };
  parent_profile?: {
    student_ids: number[];
  };
  admin_profile?: {
    permissions: string[];
    is_superuser: boolean;
  };
}

export interface Admin extends BaseUser {
  role: UserRole.ADMIN;
  is_superuser: boolean;
  admin_profile: {
    permissions: string[];
    is_superuser: boolean;
  };
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

export interface AdminProfile {
  is_superuser: boolean;
  permissions: string[];
}

export interface User {
  id: number;
  email: string;
  username: string;
  role: UserRole;
  is_active: boolean;
  is_superuser?: boolean;
  created_at: string;
  
  // 角色特定的配置信息
  student_profile?: StudentProfile;    // 仅当role为STUDENT时存在
  teacher_profile?: TeacherProfile;    // 仅当role为TEACHER时存在
  admin_profile?: AdminProfile;        // 仅当role为ADMIN时存在
}

export interface Admin extends User {
  is_superuser: boolean;
  admin_profile: AdminProfile;
}

export interface AdminCreate {
  email: string;
  username: string;
  password: string;
  is_superuser?: boolean;
  permissions?: string[];
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