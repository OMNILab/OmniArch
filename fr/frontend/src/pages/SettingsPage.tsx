import { useState } from 'react'
import { toast } from 'react-hot-toast'
import { 
  UsersIcon, 
  BuildingOfficeIcon, 
  DocumentTextIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline'

interface User {
  id: string
  username: string
  role: 'organizer' | 'participant' | 'admin'
  department: string
}

interface Template {
  id: string
  name: string
  description: string
}

const mockUsers: User[] = [
  { id: '1', username: 'admin', role: 'admin', department: '管理部' },
  { id: '2', username: '张三', role: 'organizer', department: '研发部' },
  { id: '3', username: '李四', role: 'participant', department: '测试部' },
  { id: '4', username: '王五', role: 'organizer', department: '市场部' },
]

const mockTemplates: Template[] = [
  { id: 'default', name: '默认模板', description: '标准会议纪要模板' },
  { id: 'project', name: '项目会议模板', description: '适用于项目相关会议' },
  { id: 'review', name: '评审会议模板', description: '适用于技术评审会议' },
]

export function SettingsPage() {
  const [activeTab, setActiveTab] = useState('users')
  const [users, setUsers] = useState<User[]>(mockUsers)
  const [templates, setTemplates] = useState<Template[]>(mockTemplates)
  const [newUser, setNewUser] = useState<{ username: string; role: 'organizer' | 'participant' | 'admin'; department: string }>({ username: '', role: 'participant', department: '' })
  const [newTemplate, setNewTemplate] = useState({ name: '', description: '' })

  const handleAddUser = () => {
    if (!newUser.username || !newUser.department) {
      toast.error('请填写完整信息')
      return
    }

    const user: User = {
      id: Date.now().toString(),
      username: newUser.username,
      role: newUser.role,
      department: newUser.department
    }
    setUsers([...users, user])
    setNewUser({ username: '', role: 'participant', department: '' })
    toast.success('用户添加成功')
  }

  const handleDeleteUser = (userId: string) => {
    setUsers(users.filter(user => user.id !== userId))
    toast.success('用户删除成功')
  }

  const handleAddTemplate = () => {
    if (!newTemplate.name || !newTemplate.description) {
      toast.error('请填写完整信息')
      return
    }

    const template: Template = {
      id: Date.now().toString(),
      ...newTemplate
    }
    setTemplates([...templates, template])
    setNewTemplate({ name: '', description: '' })
    toast.success('模板添加成功')
  }

  const handleDeleteTemplate = (templateId: string) => {
    setTemplates(templates.filter(template => template.id !== templateId))
    toast.success('模板删除成功')
  }

  const getRoleText = (role: User['role']) => {
    switch (role) {
      case 'admin': return '管理员'
      case 'organizer': return '组织者'
      case 'participant': return '参与者'
      default: return role
    }
  }

  const tabs = [
    { id: 'users', name: '用户管理', icon: UsersIcon },
    { id: 'departments', name: '组织架构', icon: BuildingOfficeIcon },
    { id: 'templates', name: '纪要模板', icon: DocumentTextIcon },
    { id: 'system', name: '系统设置', icon: Cog6ToothIcon },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">系统设置</h1>
        <p className="text-gray-600">管理系统用户、组织架构和配置</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon className="h-4 w-4" />
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="card">
        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">用户管理</h3>
              <button className="btn-primary">导出用户列表</button>
            </div>

            {/* Add User Form */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
              <input
                type="text"
                placeholder="用户名"
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                className="input-field"
              />
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({ ...newUser, role: e.target.value as User['role'] })}
                className="input-field"
              >
                <option value="participant">参与者</option>
                <option value="organizer">组织者</option>
                <option value="admin">管理员</option>
              </select>
              <input
                type="text"
                placeholder="部门"
                value={newUser.department}
                onChange={(e) => setNewUser({ ...newUser, department: e.target.value })}
                className="input-field"
              />
              <button onClick={handleAddUser} className="btn-primary">
                添加用户
              </button>
            </div>

            {/* Users Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      用户名
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      角色
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      部门
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      操作
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map(user => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {user.username}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {getRoleText(user.role)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {user.department}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          删除
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'departments' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">组织架构管理</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {['研发部', '测试部', '市场部', '产品部', '管理部'].map(dept => (
                <div key={dept} className="card p-4">
                  <h4 className="font-semibold text-gray-900">{dept}</h4>
                  <p className="text-sm text-gray-500 mt-1">
                    {users.filter(user => user.department === dept).length} 人
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'templates' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">纪要模板管理</h3>
              <button className="btn-primary">导入模板</button>
            </div>

            {/* Add Template Form */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg">
              <input
                type="text"
                placeholder="模板名称"
                value={newTemplate.name}
                onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                className="input-field"
              />
              <input
                type="text"
                placeholder="模板描述"
                value={newTemplate.description}
                onChange={(e) => setNewTemplate({ ...newTemplate, description: e.target.value })}
                className="input-field"
              />
              <button onClick={handleAddTemplate} className="btn-primary">
                添加模板
              </button>
            </div>

            {/* Templates Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {templates.map(template => (
                <div key={template.id} className="card p-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="font-semibold text-gray-900">{template.name}</h4>
                      <p className="text-sm text-gray-500 mt-1">{template.description}</p>
                    </div>
                    <button
                      onClick={() => handleDeleteTemplate(template.id)}
                      className="text-red-600 hover:text-red-900 text-sm"
                    >
                      删除
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'system' && (
          <div className="space-y-6">
            <h3 className="text-lg font-semibold">系统配置</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">自动生成纪要</h4>
                  <p className="text-sm text-gray-500">会议结束后自动生成纪要</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" defaultChecked />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
              
              <div className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">任务自动分配</h4>
                  <p className="text-sm text-gray-500">根据会议内容自动分配任务</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" className="sr-only peer" />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary-600"></div>
                </label>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 