import React, { useState } from 'react'
import axios from 'axios'
import { useAppStore } from '../store/useStore'

interface TestQuestion {
  word: string
  options: string[]
  correct_answer: string
  level: string
}

interface TestAnswer {
  question_word: string
  selected_answer: string
  is_correct: boolean
}

const VocabularyTest: React.FC = () => {
  const { user, setUser } = useAppStore()
  const [questions, setQuestions] = useState<TestQuestion[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<TestAnswer[]>([])
  const [testStarted, setTestStarted] = useState(false)
  const [testCompleted, setTestCompleted] = useState(false)
  const [result, setResult] = useState<{ result_level: string; estimated_vocab_size: number; message: string } | null>(null)
  const [loading, setLoading] = useState(false)

  // 开始测试 (支持本地模式)
  const startTest = async () => {
    if (!user) {
      alert('Please login first')
      return
    }

    setLoading(true)
    try {
      // 尝试调用后端API
      const response = await axios.post('https://dull-zoos-melt.loca.lt/api/tests/start/', {
        user_id: user.id,
        test_type: 'vocabulary'
      }, { timeout: 2000 })

      setQuestions(response.data.questions)
      setTestStarted(true)
      setCurrentQuestionIndex(0)
      setAnswers([])
    } catch (error) {
      console.log('Backend not available, using local test mode')
      
      // 本地模拟测试数据（15题，分布：A1(2), A2(3), B1(4), B2(3), C1(2), C2(1)）
      const mockQuestions: TestQuestion[] = [
        // A1 (2题)
        { word: 'the', options: ['这；那', '一个', '一些', '所有'], correct_answer: '这；那', level: 'A1' },
        { word: 'have', options: ['有', '做', '去', '说'], correct_answer: '有', level: 'A1' },
        // A2 (3题)
        { word: 'quick', options: ['快速的', '缓慢的', '聪明的', '懒惰的'], correct_answer: '快速的', level: 'A2' },
        { word: 'brown', options: ['棕色', '红色', '蓝色', '绿色'], correct_answer: '棕色', level: 'A1' },
        { word: 'lazy', options: ['懒惰的', '勤奋的', '聪明的', '勇敢的'], correct_answer: '懒惰的', level: 'A2' },
        // B1 (4题)
        { word: 'fox', options: ['狐狸', '狼', '熊', '鹿'], correct_answer: '狐狸', level: 'B1' },
        { word: 'jump', options: ['跳跃', '跑步', '游泳', '飞行'], correct_answer: '跳跃', level: 'B1' },
        { word: 'accomplish', options: ['完成', '开始', '停止', '放弃'], correct_answer: '完成', level: 'B1' },
        { word: 'challenge', options: ['挑战', '机会', '困难', '成功'], correct_answer: '挑战', level: 'B1' },
        // B2 (3题)
        { word: 'develop', options: ['发展', '破坏', '减少', '保持'], correct_answer: '发展', level: 'B1' },
        { word: 'environment', options: ['环境', '建筑', '技术', '文化'], correct_answer: '环境', level: 'B1' },
        { word: 'knowledge', options: ['知识', '力量', '财富', '智慧'], correct_answer: '知识', level: 'B1' },
        // C1 (2题)
        { word: 'sophisticated', options: ['复杂的；精密的', '简单的', '普通的', '基本的'], correct_answer: '复杂的；精密的', level: 'B2' },
        { word: 'comprehensive', options: ['全面的；综合的', '部分的', '有限的', '单一的'], correct_answer: '全面的；综合的', level: 'B2' },
        // C2 (1题)
        { word: 'ubiquitous', options: ['无处不在的', '罕见的', '特殊的', '局部的'], correct_answer: '无处不在的', level: 'C1' }
      ]
      
      setQuestions(mockQuestions)
      setTestStarted(true)
      setCurrentQuestionIndex(0)
      setAnswers([])
    } finally {
      setLoading(false)
    }
  }

  // 回答问题
  const handleAnswer = (selectedAnswer: string) => {
    const currentQuestion = questions[currentQuestionIndex]
    const isCorrect = selectedAnswer === currentQuestion.correct_answer

    const newAnswer: TestAnswer = {
      question_word: currentQuestion.word,
      selected_answer: selectedAnswer,
      is_correct: isCorrect
    }

    const newAnswers = [...answers, newAnswer]
    setAnswers(newAnswers)

    // 移动到下一题或完成测试
    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    } else {
      submitTest(newAnswers)
    }
  }

  // 提交测试 (支持本地模式)
  const submitTest = async (finalAnswers: TestAnswer[]) => {
    if (!user) return

    setLoading(true)
    try {
      // 尝试调用后端API
      const response = await axios.post('https://dull-zoos-melt.loca.lt/api/tests/submit/', {
        user_id: user.id,
        test_type: 'vocabulary',
        answers: finalAnswers
      }, { timeout: 2000 })

      setResult(response.data)
      setTestCompleted(true)

      // 更新用户等级
      if (user) {
        setUser({
          ...user,
          cefr_level: response.data.result_level
        })
      }
    } catch (error) {
      console.log('Using local test result calculation')
      
      // 本地计算测试结果
      const correctCount = finalAnswers.filter(a => a.is_correct).length
      const totalCount = finalAnswers.length
      const accuracy = correctCount / totalCount
      
      let resultLevel = 'A1'
      let vocabSize = 500
      
      if (accuracy >= 0.9) {
        resultLevel = 'B2'
        vocabSize = 5000
      } else if (accuracy >= 0.7) {
        resultLevel = 'B1'
        vocabSize = 3000
      } else if (accuracy >= 0.5) {
        resultLevel = 'A2'
        vocabSize = 1500
      }
      
      const resultData = {
        result_level: resultLevel,
        estimated_vocab_size: vocabSize,
        message: `Your English level is ${resultLevel}. Estimated vocabulary size: ${vocabSize} words. Correct: ${correctCount}/${totalCount}`
      }
      
      setResult(resultData)
      setTestCompleted(true)
      
      // 更新用户等级
      if (user) {
        setUser({
          ...user,
          cefr_level: resultLevel
        })
      }
    } finally {
      setLoading(false)
    }
  }

  // 重置测试
  const resetTest = () => {
    setTestStarted(false)
    setTestCompleted(false)
    setQuestions([])
    setAnswers([])
    setCurrentQuestionIndex(0)
    setResult(null)
  }

  // 渲染测试结果
  if (testCompleted && result) {
    return (
      <div className="test-result p-8 bg-gradient-to-br from-blue-900 to-purple-900 rounded-lg text-white">
        <h2 className="text-3xl font-bold mb-4">Test Complete!</h2>
        <div className="text-center">
          <p className="text-xl mb-2">Your English Level:</p>
          <p className="text-6xl font-bold text-yellow-400 mb-4">{result.result_level}</p>
          <p className="text-lg mb-2">Estimated Vocabulary Size:</p>
          <p className="text-4xl font-bold text-green-400 mb-6">{result.estimated_vocab_size} words</p>
          <p className="text-gray-300 mb-8">{result.message}</p>
          <button
            onClick={resetTest}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          >
            Retake Test
          </button>
        </div>
      </div>
    )
  }

  // 渲染测试问题
  if (testStarted && questions.length > 0) {
    const currentQuestion = questions[currentQuestionIndex]

    return (
      <div className="test-container p-8 bg-gray-800 rounded-lg">
        <div className="mb-6">
          <div className="flex justify-between items-center mb-4">
            <span className="text-gray-400">
              Question {currentQuestionIndex + 1} of {questions.length}
            </span>
            <span className="px-3 py-1 bg-blue-600 text-white rounded text-sm">
              Level: {currentQuestion.level}
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${((currentQuestionIndex + 1) / questions.length) * 100}%` }}
            />
          </div>
        </div>

        <h3 className="text-3xl font-bold text-white mb-8 text-center">
          {currentQuestion.word}
        </h3>

        <div className="grid grid-cols-1 gap-4">
          {currentQuestion.options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleAnswer(option)}
              disabled={loading}
              className="p-4 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition text-left"
            >
              {option}
            </button>
          ))}
        </div>
      </div>
    )
  }

  // 渲染开始界面
  return (
    <div className="test-start p-8 bg-gray-800 rounded-lg text-center">
      <h2 className="text-3xl font-bold text-white mb-4">English Level Test</h2>
      <p className="text-gray-300 mb-6">
        Take this test to determine your English proficiency level.
        The test consists of {questions.length || 15} questions covering different difficulty levels.
      </p>
      <button
        onClick={startTest}
        disabled={loading || !user}
        className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
      >
        {loading ? 'Loading...' : 'Start Test'}
      </button>
      {!user && (
        <p className="text-red-400 mt-4">Please login first</p>
      )}
    </div>
  )
}

export default VocabularyTest
