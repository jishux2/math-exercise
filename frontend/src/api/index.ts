import axios, { AxiosError } from 'axios';

const BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器添加token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    // 确保token格式正确
    config.headers.Authorization = `Bearer ${token}`;
    // 调试输出
    console.log('Request headers:', config.headers);
  }
  return config;
});

// 响应拦截器处理错误
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // token过期或无效，清除token并跳转到登录页
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const auth = {
  login: async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);  // OAuth2 uses username field for email
    formData.append('password', password);
    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',  // 重要！登录接口需要这个
      },
    });
    return response.data;
  },
};

export const exercises = {
  create: async (data: any) => {
    const response = await api.post('/exercises', data);
    return response.data;
  },
  
  getExercise: async (id: number) => {
    const response = await api.get(`/exercises/${id}`);
    return response.data;
  },
  
  submitAnswer: async (exerciseId: number, questionId: number, data: any) => {
    const response = await api.post(
      `/exercises/${exerciseId}/questions/${questionId}/answer`,
      data
    );
    return response.data;
  },
  
  complete: async (id: number) => {
    const response = await api.post(`/exercises/${id}/complete`);
    return response.data;
  },
};

export default api;

export const ai = {
  initialize: async (tokens: { pb_token: string; plat_token: string }) => {
    const response = await api.post('/exercises/ai/initialize', tokens);
    return response.data;
  },

  getFeedback: async (
    exerciseId: number,
    feedbackType: 'detailed' | 'summary' = 'detailed',
    onChunk: (chunk: string) => void,
    onError: (error: any) => void
  ) => {
    try {
      const response = await fetch(
        `${BASE_URL}/exercises/${exerciseId}/ai-feedback?feedback_type=${feedbackType}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            if (data.error) {
              onError(data.error);
              return;
            }
            if (data.status === 'stopped') {
              return;
            }
            if (data.chunk) {
              onChunk(data.chunk);
            }
          }
        }
      }
    } catch (error) {
      onError(error);
    }
  },

  stopFeedback: async (exerciseId: number) => {
    const response = await api.post(`/exercises/${exerciseId}/ai-feedback/stop`);
    return response.data;
  },
};
