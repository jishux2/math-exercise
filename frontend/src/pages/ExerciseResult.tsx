import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { exercises } from '../api';
import AIFeedbackPreview from '../components/AIFeedbackPreview';

interface Question {
  id: number;
  content: string;
  correct_answer: number;
  user_answer: number | null;
  time_spent: number | null;
  is_correct: boolean;
}

interface Exercise {
  id: number;
  difficulty: string;
  final_score: number;
  total_time: number;
  questions: Question[];
  ai_feedback: string | null;
}

const ExerciseResult = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [exercise, setExercise] = useState<Exercise | null>(null);
  const [showAIFeedback, setShowAIFeedback] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadExercise = async () => {
      try {
        const data = await exercises.getExercise(parseInt(id!));
        setExercise(data);
      } catch (error) {
        setError('加载练习结果失败');
        console.error('Failed to load exercise:', error);
      } finally {
        setLoading(false);
      }
    };
    loadExercise();
  }, [id]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error || !exercise) {
    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="bg-red-50 border-l-4 border-red-400 p-4 text-red-700">
          {error || '练习不存在'}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      {/* 总体成绩 */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h1 className="text-2xl font-bold mb-4">练习完成！</h1>
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="text-center p-4 bg-blue-50 rounded">
            <div className="text-sm text-gray-600">最终得分</div>
            <div className="text-3xl font-bold text-blue-600">
              {exercise.final_score}
            </div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded">
            <div className="text-sm text-gray-600">总用时</div>
            <div className="text-3xl font-bold text-green-600">
              {exercise.total_time}秒
            </div>
          </div>
        </div>
      </div>

      {/* 答题详情 */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">答题详情</h2>
        <div className="space-y-4">
          {exercise.questions.map((question, index) => (
            <div
              key={question.id}
              className={`p-4 rounded-lg ${
                question.is_correct ? 'bg-green-50' : 'bg-red-50'
              }`}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="font-medium">题目 {index + 1}</div>
                <div className="text-sm text-gray-500">
                  用时：{question.time_spent}秒
                </div>
              </div>
              <div className="mb-2">{question.content} = ?</div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  你的答案：
                  <span className={question.is_correct ? 'text-green-600' : 'text-red-600'}>
                    {question.user_answer}
                  </span>
                </div>
                <div>
                  正确答案：
                  <span className="text-blue-600">{question.correct_answer}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI点评 */}
      {exercise.ai_feedback && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">AI点评</h2>
            <button
              onClick={() => setShowAIFeedback(true)}
              className="text-blue-500 hover:text-blue-700"
            >
              查看完整评价
            </button>
          </div>
          <div className="prose max-w-none">
            {exercise.ai_feedback.split('\n').map((line, index) => (
              <p key={index}>{line}</p>
            ))}
          </div>
        </div>
      )}

      {/* 底部按钮 */}
      <div className="mt-8 flex justify-center space-x-4">
        <button
          onClick={() => navigate('/create-exercise')}
          className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          再来一组
        </button>
        <button
          onClick={() => navigate('/')}
          className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
        >
          返回首页
        </button>
      </div>

      {/* AI反馈预览对话框 */}
      {showAIFeedback && exercise.ai_feedback && (
        <AIFeedbackPreview
          content={exercise.ai_feedback}
          onClose={() => setShowAIFeedback(false)}
        />
      )}
    </div>
  );
};

export default ExerciseResult;