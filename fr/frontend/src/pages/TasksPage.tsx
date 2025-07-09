import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { 
  ClockIcon, 
  UserIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { getStatusColor } from '@/lib/utils'

interface Task {
  id: string
  description: string
  owner: string
  department: string
  due_date: string
  status: 'draft' | 'confirmed' | 'done'
}

const departments = ['研发部', '测试部', '市场部', '产品部']

const mockTasks: Task[] = [
  {
    id: '1',
    description: '完成前端主要功能开发',
    owner: '张三',
    department: '研发部',
    due_date: '2025-01-20',
    status: 'confirmed'
  },
  {
    id: '2',
    description: '补充测试用例到80%覆盖率',
    owner: '李四',
    department: '测试部',
    due_date: '2025-01-18',
    status: 'draft'
  },
  {
    id: '3',
    description: '准备产品发布材料',
    owner: '王五',
    department: '市场部',
    due_date: '2025-01-25',
    status: 'draft'
  },
  {
    id: '4',
    description: '优化后端性能',
    owner: '赵六',
    department: '研发部',
    due_date: '2025-01-22',
    status: 'done'
  },
  {
    id: '5',
    description: '用户调研报告',
    owner: '孙七',
    department: '产品部',
    due_date: '2025-01-30',
    status: 'confirmed'
  }
]

const chartData = [
  { department: '研发部', tasks: 2 },
  { department: '测试部', tasks: 1 },
  { department: '市场部', tasks: 1 },
  { department: '产品部', tasks: 1 }
]

export function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>(mockTasks)

  const getTasksByDepartment = (department: string) => {
    return tasks.filter(task => task.department === department)
  }

  const updateTaskStatus = (taskId: string, newStatus: Task['status']) => {
    setTasks(tasks.map(task => 
      task.id === taskId ? { ...task, status: newStatus } : task
    ))
    toast.success('任务状态已更新')
  }

  const updateTaskOwner = (taskId: string, newOwner: string) => {
    setTasks(tasks.map(task => 
      task.id === taskId ? { ...task, owner: newOwner } : task
    ))
    toast.success('任务负责人已更新')
  }

  const getStatusText = (status: Task['status']) => {
    switch (status) {
      case 'draft': return '草稿'
      case 'confirmed': return '已确认'
      case 'done': return '已完成'
      default: return status
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">任务看板</h1>
        <p className="text-gray-600">从会议纪要中自动提取的任务，按部门分类管理</p>
      </div>

      {/* Statistics Chart */}
      <div className="card">
        <div className="flex items-center space-x-2 mb-4">
          <ChartBarIcon className="h-6 w-6 text-primary-600" />
          <h3 className="text-lg font-semibold">任务统计</h3>
        </div>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="department" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="tasks" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {departments.map(department => (
          <div key={department} className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">{department}</h3>
              <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded-full">
                {getTasksByDepartment(department).length}
              </span>
            </div>
            
            <div className="space-y-3">
              {getTasksByDepartment(department).map(task => (
                <div key={task.id} className="card p-4">
                  <div className="space-y-3">
                    <p className="text-sm text-gray-700">{task.description}</p>
                    
                    <div className="flex items-center justify-between text-xs text-gray-500">
                      <div className="flex items-center space-x-1">
                        <UserIcon className="h-3 w-3" />
                        <span>{task.owner}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <ClockIcon className="h-3 w-3" />
                        <span>{new Date(task.due_date).toLocaleDateString('zh-CN')}</span>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                      <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(task.status)}`}>
                        {getStatusText(task.status)}
                      </span>
                      
                      <div className="flex space-x-1">
                        <select
                          value={task.owner}
                          onChange={(e) => updateTaskOwner(task.id, e.target.value)}
                          className="text-xs border border-gray-300 rounded px-1 py-0.5"
                        >
                          <option value="张三">张三</option>
                          <option value="李四">李四</option>
                          <option value="王五">王五</option>
                          <option value="赵六">赵六</option>
                          <option value="孙七">孙七</option>
                        </select>
                        
                        <select
                          value={task.status}
                          onChange={(e) => updateTaskStatus(task.id, e.target.value as Task['status'])}
                          className="text-xs border border-gray-300 rounded px-1 py-0.5"
                        >
                          <option value="draft">草稿</option>
                          <option value="confirmed">已确认</option>
                          <option value="done">已完成</option>
                        </select>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="card">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-gray-900">{tasks.length}</p>
            <p className="text-sm text-gray-500">总任务数</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-blue-600">
              {tasks.filter(t => t.status === 'confirmed').length}
            </p>
            <p className="text-sm text-gray-500">已确认</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-green-600">
              {tasks.filter(t => t.status === 'done').length}
            </p>
            <p className="text-sm text-gray-500">已完成</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-orange-600">
              {tasks.filter(t => t.status === 'draft').length}
            </p>
            <p className="text-sm text-gray-500">草稿</p>
          </div>
        </div>
      </div>
    </div>
  )
} 