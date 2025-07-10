import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { MicrophoneIcon, PaperAirplaneIcon } from '@heroicons/react/24/outline'
import { getMatchScoreColor } from '@/lib/utils'

interface MeetingIntent {
  datetime: string
  participants: number
  location: string
  requirements: string[]
}

interface RoomRecommendation {
  room_id: string
  name: string
  capacity: number
  equipment: string[]
  status: string
  match_score: number
  deviation: string[]
}

export function BookingPage() {
  const [inputText, setInputText] = useState('')
  const [isProcessing, setIsProcessing] = useState(false)
  const [intent, setIntent] = useState<MeetingIntent | null>(null)
  const [recommendations, setRecommendations] = useState<RoomRecommendation[]>([])
  const [showBookingModal, setShowBookingModal] = useState(false)
  const [selectedRoom, setSelectedRoom] = useState<RoomRecommendation | null>(null)
  const [bookingForm, setBookingForm] = useState({
    title: '',
    duration: 60,
  })

  // Mock data for demonstration
  const mockRecommendations: RoomRecommendation[] = [
    {
      room_id: 'A301',
      name: 'A栋301会议室',
      capacity: 12,
      equipment: ['视频会议', '白板', '投影仪'],
      status: 'available',
      match_score: 0.92,
      deviation: [],
    },
    {
      room_id: 'A305',
      name: 'A栋305会议室',
      capacity: 10,
      equipment: ['白板', '投影仪'],
      status: 'available',
      match_score: 0.75,
      deviation: ['缺少视频会议'],
    },
    {
      room_id: 'B201',
      name: 'B栋201会议室',
      capacity: 15,
      equipment: ['视频会议', '白板', '投影仪', '音响'],
      status: 'available',
      match_score: 0.88,
      deviation: ['容量超出需求'],
    },
  ]

  const handleSubmit = async () => {
    if (!inputText.trim()) {
      toast.error('请输入会议需求')
      return
    }

    setIsProcessing(true)
    
    // Simulate API call
    setTimeout(() => {
      const mockIntent: MeetingIntent = {
        datetime: '2025-01-15T15:00:00',
        participants: 10,
        location: 'A栋',
        requirements: ['视频会议'],
      }
      
      setIntent(mockIntent)
      setRecommendations(mockRecommendations)
      setIsProcessing(false)
      toast.success('已识别您的需求，为您推荐会议室')
    }, 2000)
  }

  const handleBookRoom = (room: RoomRecommendation) => {
    setSelectedRoom(room)
    setShowBookingModal(true)
  }

  const confirmBooking = async () => {
    if (!bookingForm.title.trim()) {
      toast.error('请输入会议主题')
      return
    }

    setIsProcessing(true)
    
    // Simulate booking API call
    setTimeout(() => {
      toast.success('会议室预定成功！')
      setShowBookingModal(false)
      setSelectedRoom(null)
      setBookingForm({ title: '', duration: 60 })
      setIsProcessing(false)
    }, 1000)
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">智能预定</h1>
        <p className="text-gray-600">用自然语言描述您的会议需求，AI将为您推荐合适的会议室</p>
      </div>

      {/* Input Section */}
      <div className="card">
        <div className="flex space-x-4">
          <div className="flex-1">
            <textarea
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="例如：明天下午三点，10人，A栋，需要视频会议"
              className="input-field h-20 resize-none"
              disabled={isProcessing}
            />
          </div>
          <div className="flex flex-col space-y-2">
            <button
              onClick={handleSubmit}
              disabled={isProcessing}
              className="btn-primary flex items-center space-x-2"
            >
              <PaperAirplaneIcon className="h-4 w-4" />
              <span>识别需求</span>
            </button>
            <button className="btn-secondary flex items-center space-x-2">
              <MicrophoneIcon className="h-4 w-4" />
              <span>语音输入</span>
            </button>
          </div>
        </div>
      </div>

      {/* Intent Display */}
      {intent && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">识别结果</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-500">时间</p>
              <p className="font-medium">{new Date(intent.datetime).toLocaleString('zh-CN')}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">人数</p>
              <p className="font-medium">{intent.participants}人</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">地点</p>
              <p className="font-medium">{intent.location}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">需求</p>
              <p className="font-medium">{intent.requirements.join(', ')}</p>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold">推荐会议室</h3>
          <div className="grid gap-4">
            {recommendations.map((room) => (
              <div key={room.room_id} className="card">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h4 className="text-lg font-semibold">{room.name}</h4>
                      <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                        {room.status === 'available' ? '可预定' : '已占用'}
                      </span>
                    </div>
                    
                    <div className="space-y-2">
                      <p className="text-gray-600">
                        容纳 {room.capacity} 人 • {room.equipment.join(', ')}
                      </p>
                      
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">匹配度：</span>
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${getMatchScoreColor(room.match_score)}`}
                            style={{ width: `${room.match_score * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium">{Math.round(room.match_score * 100)}%</span>
                      </div>
                      
                      {room.deviation.length > 0 && (
                        <div className="text-sm text-orange-600">
                          ⚠️ {room.deviation.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <button
                    onClick={() => handleBookRoom(room)}
                    className="btn-primary ml-4"
                    disabled={room.status !== 'available'}
                  >
                    预定
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Booking Modal */}
      {showBookingModal && selectedRoom && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">确认预定</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  会议室
                </label>
                <p className="text-gray-900">{selectedRoom.name}</p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  会议主题 *
                </label>
                <input
                  type="text"
                  value={bookingForm.title}
                  onChange={(e) => setBookingForm({ ...bookingForm, title: e.target.value })}
                  className="input-field"
                  placeholder="请输入会议主题"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  时长（分钟）
                </label>
                <select
                  value={bookingForm.duration}
                  onChange={(e) => setBookingForm({ ...bookingForm, duration: Number(e.target.value) })}
                  className="input-field"
                >
                  <option value={30}>30分钟</option>
                  <option value={60}>1小时</option>
                  <option value={90}>1.5小时</option>
                  <option value={120}>2小时</option>
                </select>
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowBookingModal(false)}
                className="btn-secondary flex-1"
              >
                取消
              </button>
              <button
                onClick={confirmBooking}
                disabled={isProcessing}
                className="btn-primary flex-1"
              >
                {isProcessing ? '预定中...' : '确认预定'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 