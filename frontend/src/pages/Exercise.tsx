import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { exercises, ai } from '../api';
import AISettingsDialog from '../components/AISettingsDialog';
import AIFeedbackPreview from '../components/AIFeedbackPreview';

const Exercise = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [exercise, setExercise] = useState<any>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answer, setAnswer] = useState('');
  const [startTime, setStartTime] = useState<number>(0);
  
  // AI相关状态
  const [isAIEnabled, setIsAIEnabled] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [aiFeedback, setAIFeedback] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    const loadExercise = async () => {
      try {
        const data = await exercises.getExercise(parseInt(id!));
        setExercise(data);
        setStartTime(Date.now());
      } catch (error) {
        console.error('Failed to load exercise:', error);
      }
    };
    loadExercise();
  }, [id]);

  const handleSubmitAnswer = async () => {
    if (!exercise || !answer) return;
  
    const question = exercise.questions[currentQuestionIndex];
    const timeSpent = Math.round((Date.now() - startTime) / 1000);
  
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
        
        // 如果启用了AI点评，获取反馈但不立即跳转
        if (isAIEnabled) {
          try {
            await getFeedback();
          } catch (error) {
            console.error('AI feedback failed:', error);
          }
        }
        
        // 完成后跳转到结果页面
        // navigate(`/result/${exercise.id}`);
      }
    } catch (error) {
      console.error('Failed to submit answer:', error);
    }
  };

  // AI相关函数
  const handleAIToggle = () => {
    if (!isAIEnabled) {
      setIsSettingsOpen(true);
    } else {
      setIsAIEnabled(false);
      setAIFeedback('');
    }
  };

  const handleSettingsSubmit = async (tokens: { pb_token: string; plat_token: string }) => {
    try {
      const result = await ai.initialize(tokens);
      if (result.success) {
        setIsAIEnabled(true);
        setIsSettingsOpen(false);
      } else {
        alert('AI服务初始化失败');
      }
    } catch (error) {
      console.error('Failed to initialize AI:', error);
      alert('AI服务初始化失败');
    }
  };

  const getFeedback = async () => {
    if (!isAIEnabled || isGenerating) return;
    
    setIsGenerating(true);
    setAIFeedback('');
    let feedback = '';

    try {
      await ai.getFeedback(
        parseInt(id!),
        'detailed',
        (chunk) => {
          feedback += chunk;
          setAIFeedback(feedback);
        },
        (error) => {
          console.error('AI feedback error:', error);
          alert('获取AI反馈失败');
        }
      );
    } finally {
      setIsGenerating(false);
    }
  };

  if (!exercise) return <div>Loading...</div>;

  const currentQuestion = exercise.questions[currentQuestionIndex];

  return (
    <div className="max-w-2xl mx-auto p-6">
      {/* AI控制按钮 */}
      <div className="flex justify-between items-center mb-6">
        <div className="text-lg font-semibold">
          题目 {currentQuestionIndex + 1} / {exercise.questions.length}
        </div>
        <button
          onClick={handleAIToggle}
          className={`
            px-4 py-2 rounded-full text-sm font-medium
            ${isAIEnabled 
              ? 'bg-green-500 text-white' 
              : 'bg-gray-200 text-gray-700'
            }
          `}
        >
          {isAIEnabled ? 'AI点评已启用' : '启用AI点评'}
        </button>
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

      {/* AI反馈区域 */}
      {aiFeedback && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-medium">AI点评</h3>
            <button
              onClick={() => setShowPreview(true)}
              className="text-blue-500 hover:text-blue-700"
            >
              查看完整评价
            </button>
          </div>
          <div className="text-gray-600 line-clamp-3">{aiFeedback}</div>
        </div>
      )}

      {/* AI设置对话框 */}
      <AISettingsDialog
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onSubmit={handleSettingsSubmit}
      />

      {/* AI反馈预览 */}
      {showPreview && (
        <AIFeedbackPreview
          content={aiFeedback}
          onClose={() => setShowPreview(false)}
        />
      )}
    </div>
  );
};

export default Exercise;