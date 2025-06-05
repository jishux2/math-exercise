import { api } from './index';

export interface Activity {
  id: number;
  student_name: string;
  score: number;
  completed_at: string;
  type: string;
}

export interface TeacherStats {
  total_students: number;
  exercises_today: number;
  average_accuracy: number;
  recent_activities: Array<Activity>;
}

export const getTeacherStats = () => 
  api.get<TeacherStats>('/users/me/teacher-stats').then((res: any) => res.data as TeacherStats);
