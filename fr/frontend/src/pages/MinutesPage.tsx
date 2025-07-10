import React, { useState } from 'react'
import { toast } from 'react-hot-toast'
import { 
  CloudArrowUpIcon, 
  PlayIcon, 
  DocumentTextIcon,
  CheckCircleIcon,
  ClockIcon,
  UserIcon
} from '@heroicons/react/24/outline'

interface TranscriptItem {
  speaker: string
  text: string
  timestamp: string
}

interface MeetingMinutes {
  title: string
  summary: string
  points: string[]
  decisions: string[]
  transcript: TranscriptItem[]
}

export function MinutesPage() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [minutes, setMinutes] = useState<MeetingMinutes | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      if (file.type.startsWith('audio/')) {
        setSelectedFile(file)
        toast.success('音频文件已选择')
      } else {
        toast.error('请选择音频文件')
      }
    }
  }

  const handleTranscribe = async () => {
    if (!selectedFile) {
      toast.error('请先选择音频文件')
      return
    }

    setIsProcessing(true)
    
    // Simulate transcription process
    setTimeout(() => {
      const mockMinutes: MeetingMinutes = {
        title: '项目复盘会议纪要',
        summary: '本次会议主要讨论了Q4项目进展，确定了下一阶段的开发计划，并分配了相关任务。',
        points: [
          '前端开发进度符合预期，预计下周完成主要功能',
          '后端API接口已全部完成，等待联调测试',
          'UI设计稿已通过评审，可以开始开发',
          '测试用例覆盖率需要提升到80%以上'
        ],
        decisions: [
          '确定下周三进行系统联调测试',
          '分配张三负责前端优化工作',
          '李四负责后端性能调优',
          '王五负责测试用例补充'
        ],
        transcript: [
          {
            speaker: '主持人',
            text: '大家好，今天我们召开项目复盘会议，首先请各部门汇报一下进展。',
            timestamp: '00:00:00'
          },
          {
            speaker: '张三',
            text: '前端这边主要功能已经完成80%，预计下周可以完成所有核心功能。',
            timestamp: '00:01:30'
          },
          {
            speaker: '李四',
            text: '后端API接口已经全部开发完成，现在等待前端联调。',
            timestamp: '00:03:15'
          },
          {
            speaker: '王五',
            text: '测试用例目前覆盖率是65%，还需要补充一些边界情况的测试。',
            timestamp: '00:05:20'
          },
          {
            speaker: '主持人',
            text: '好的，那我们确定下周三进行系统联调测试，大家做好准备。',
            timestamp: '00:08:45'
          }
        ]
      }
      
      setMinutes(mockMinutes)
      setIsProcessing(false)
      toast.success('会议纪要生成完成！')
    }, 3000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">会议纪要</h1>
        <p className="text-gray-600">上传会议录音，AI将自动生成结构化会议纪要</p>
      </div>

      {/* Upload Section */}
      <div className="card">
        <div className="space-y-4">
          <div className="flex items-center space-x-2">
            <DocumentTextIcon className="h-6 w-6 text-primary-600" />
            <h3 className="text-lg font-semibold">音频上传</h3>
          </div>
          
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400" />
            <div className="mt-4">
              <label htmlFor="file-upload" className="btn-primary cursor-pointer">
                选择音频文件
              </label>
              <input
                id="file-upload"
                type="file"
                accept="audio/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
            <p className="mt-2 text-sm text-gray-600">
              支持 MP3, WAV 格式，最大 100MB
            </p>
            {selectedFile && (
              <p className="mt-2 text-sm text-green-600">
                已选择: {selectedFile.name}
              </p>
            )}
          </div>
          
          <button
            onClick={handleTranscribe}
            disabled={!selectedFile || isProcessing}
            className="btn-primary w-full flex items-center justify-center space-x-2"
          >
            <PlayIcon className="h-4 w-4" />
            <span>{isProcessing ? '正在生成纪要...' : '开始生成纪要'}</span>
          </button>
        </div>
      </div>

      {/* Minutes Display */}
      {minutes && (
        <div className="space-y-6">
          {/* Summary */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">会议摘要</h3>
            <p className="text-gray-700 leading-relaxed">{minutes.summary}</p>
          </div>

          {/* Key Points */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">会议要点</h3>
            <ul className="space-y-2">
              {minutes.points.map((point, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <CheckCircleIcon className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">{point}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Decisions */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">会议决策</h3>
            <ul className="space-y-2">
              {minutes.decisions.map((decision, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="h-5 w-5 bg-primary-500 text-white rounded-full flex items-center justify-center text-xs font-bold mt-0.5 flex-shrink-0">
                    !
                  </div>
                  <span className="text-gray-700">{decision}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Transcript */}
          <div className="card">
            <h3 className="text-lg font-semibold mb-4">会议记录</h3>
            <div className="space-y-4">
              {minutes.transcript.map((item, index) => (
                <div key={index} className="flex space-x-3">
                  <div className="flex-shrink-0">
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <ClockIcon className="h-4 w-4" />
                      <span>{item.timestamp}</span>
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <UserIcon className="h-4 w-4 text-gray-400" />
                      <span className="font-medium text-gray-900">{item.speaker}</span>
                    </div>
                    <p className="text-gray-700">{item.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-3">
            <button className="btn-primary">
              导出 PDF
            </button>
            <button className="btn-secondary">
              导出 Markdown
            </button>
            <button className="btn-secondary">
              编辑纪要
            </button>
          </div>
        </div>
      )}
    </div>
  )
} 