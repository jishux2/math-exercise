// src/pages/student/Exercise.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { exercises } from '../../api';
import { useAI } from '../../contexts/AIContext';
import { Sparkles, HelpCircle } from 'lucide-react'; // 引入新图标

const Exercise = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAIInitialized } = useAI(); // 只获取全局状态

  const [exercise, setExercise] = useState<any>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [startTime, setStartTime] = useState<number>(0);

  useEffect(() => {
    const abortController = new AbortController();

    const loadExercise = async () => {
      try {
        const data = await exercises.getExercise(parseInt(id!), abortController.signal);
        
        if (abortController.signal.aborted) return;
        
        setExercise(data);
        setStartTime(Date.now());
      } catch (error) {
        if (!abortController.signal.aborted) {
          console.error('Failed to load exercise:', error);
        }
      }
    };

    loadExercise();

    return () => {
      abortController.abort();
    };
  }, [id]);

  const handleSubmitAnswer = async () => {
    if (!exercise || !answer) return;
  
    const question = exercise.questions[currentQuestionIndex];
    const timeSpent = Math.max(1, Math.round((Date.now() - startTime) / 1000));  // 确保至少为1秒
  
    try {
      await exercises.submitAnswer(exercise.id, question.id, {
        user_answer: parseFloat(answer),
        time_spent: timeSpent
      });
  
      if (currentQuestionIndex < exercise.questions.length - 1) {
        setCurrentQuestionIndex(prev => prev + 1);
        setAnswer('');
        setStartTime(Date.now());
      } else {
        // 完成练习
        await exercises.complete(exercise.id);
        navigate(`/student/result/${exercise.id}`, {
          state: { shouldGenerateAI: isAIInitialized } // 如果AI已初始化，就去生成
        });
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  if (!exercise) return <div>Loading...</div>;

  const currentQuestion = exercise.questions[currentQuestionIndex];

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <div className="text-lg font-semibold">
          题目 {currentQuestionIndex + 1} / {exercise.questions.length}
        </div>
        
        {/* --- 优雅的提示信息 --- */}
        <div className="relative group">
          {isAIInitialized ? (
            <div className="flex items-center gap-1.5 text-sm text-green-600">
              <Sparkles className="w-4 h-4" />
              <span>AI点评已启用</span>
            </div>
          ) : (
            <div className="flex items-center gap-1.5 text-sm text-gray-400">
              <HelpCircle className="w-4 h-4" />
              <span>AI点评不可用</span>
            </div>
          )}
          <div className="absolute bottom-full mb-2 w-48 p-2 text-xs text-white bg-gray-800 rounded-md opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
            {isAIInitialized 
              ? "完成练习后将自动生成AI点评。" 
              : "请点击右下角AI助手图标，在侧边栏配置AI服务以启用点评功能。"
            }
          </div>
        </div>
      </div>

      {/* 题目内容 */}
      <div className="mb-6">
        <div className="text-xl mt-4">{currentQuestion.content} = ?</div>
      </div>

      {/* 答题区域 */}
      <div className="space-y-4">
        <input
          type="number"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          className="w-full p-2 border rounded"
          placeholder="请输入答案"
        />

        <button
          onClick={handleSubmitAnswer}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          提交答案
        </button>
      </div>
    </div>
  );
};

export default Exercise;