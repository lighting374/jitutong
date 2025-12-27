<script setup lang="ts">
import { ref, onMounted } from 'vue'
import adminApi from '../../api/admin'
import { fixAvatarUrl } from '@/config/apiConfig'

const users = ref<any[]>([])
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const error = ref('')
const selected = ref<any>(null)
const editing = ref(false)

// 搜索与多选
const q = ref('')
const selectedIds = ref<Record<string, boolean>>({})
const allSelected = ref(false)

// 角色修改对话框
const roleDialogVisible = ref(false)
const roleEditingUser = ref<any>(null)
const newRole = ref('')

const availableRoles = [
  { value: 'user', label: '普通用户', description: '基础权限：浏览、评论、收藏' },
  { value: 'wiki_admin', label: 'Wiki管理员', description: '普通权限 + 编辑Wiki、审核Wiki建议' },
  { value: 'admin', label: '系统管理员', description: '完整权限：用户管理、系统设置、数据分析' },
]

function getRoleLabel(roleValue: string) {
  const role = availableRoles.find(r => r.value === roleValue)
  return role ? role.label : roleValue
}

function getRoleBadgeClass(roleValue: string) {
  switch (roleValue) {
    case 'admin':
      return 'bg-red-100 text-red-700'
    case 'wiki_admin':
      return 'bg-blue-100 text-blue-700'
    default:
      return 'bg-gray-100 text-gray-700'
  }
}

// 获取头像 URL（处理相对路径和绝对路径）
function getAvatarUrl(avatar: string | undefined) {
  return fixAvatarUrl(avatar)
}

// 获取用户名首字母（用于默认头像）
function getInitial(name: string | undefined) {
  if (!name || name.length === 0) return '?'
  const firstChar = name.charAt(0)
  return firstChar ? firstChar.toUpperCase() : '?'
}

function clearSelection() {
  selectedIds.value = {}
  allSelected.value = false
}

async function fetchList() {
  loading.value = true
  error.value = ''
  try {
    const res = await adminApi.getAccountsList(page.value, pageSize.value, q.value)
    // assume res: { items: [], total }
    users.value = res.items || []
    total.value = res.total || users.value.length
    
    // 调试：打印第一个用户的数据
    if (users.value.length > 0) {
      console.log('📊 用户列表数据示例：', users.value[0])
      console.log('📊 第一个用户的role字段：', users.value[0].role)
    }
    
    // 清理已选
    clearSelection()
  } catch (e: any) {
    error.value = e.message || '获取用户列表失败'
  } finally {
    loading.value = false
  }
}

function openEdit(u: any) {
  selected.value = { ...u }
  avatarFile.value = null
  avatarPreview.value = null
  editing.value = true
}

function closeEdit() {
  selected.value = null
  avatarFile.value = null
  avatarPreview.value = null
  editing.value = false
}

async function saveEdit() {
  if (!selected.value) return
  // 简单前端校验
  const username = selected.value.nickname || selected.value.username || ''
  if (!username || String(username).trim() === '') {
    alert('用户名不能为空')
    return
  }

  try {
    // 如果有头像文件需要上传
    if (avatarFile.value) {
      const avatarUrl = await adminApi.uploadAvatar(selected.value.id, avatarFile.value)
      // 更新用户数据中的头像字段
      selected.value.avatar = avatarUrl
    }
    
    // 更新用户信息
    await adminApi.updateAccount(selected.value)
    await fetchList()
    closeEdit()
    alert('保存成功')
  } catch (e: any) {
    alert(e.message || '保存失败')
  }
}

async function doDelete(id: string) {
  if (!confirm('确认删除该用户？')) return
  try {
    await adminApi.deleteAccount(id)
    await fetchList()
    alert('删除成功')
  } catch (e: any) {
    alert(e.message || '删除失败')
  }
}

// 批量删除
async function batchDelete() {
  const ids = Object.keys(selectedIds.value).filter((k) => selectedIds.value[k])
  if (!ids.length) { alert('未选择用户'); return }
  if (!confirm(`确认删除选中的 ${ids.length} 个用户？`)) return
  try {
    // 后端没有批量删除接口，这里逐个调用
    for (const id of ids) {
      // await adminApi.deleteAccount(id)
      // 使用并行会更快，但为了简单逐个执行
      // 若需要并行可以改成 Promise.all
      await adminApi.deleteAccount(id)
    }
    await fetchList()
    alert('批量删除完成')
  } catch (e: any) {
    alert(e.message || '批量删除失败')
  }
}

async function doBan(id: string) {
  const reason = prompt('请输入封禁原因（可选）') || ''
  const until = prompt('请输入封禁结束时间 (ISO 或 空 表示永久)') || undefined
  try {
    await adminApi.banAccount(id, reason, until)
    await fetchList()
    alert('封禁成功')
  } catch (e: any) {
    alert(e.message || '封禁失败')
  }
}

// 批量封禁/解封
async function batchBan() {
  const ids = Object.keys(selectedIds.value).filter((k) => selectedIds.value[k])
  if (!ids.length) { alert('未选择用户'); return }
  const reason = prompt('请输入封禁原因（可选）') || ''
  const until = prompt('请输入封禁结束时间 (ISO 或 空 表示永久)') || undefined
  try {
    for (const id of ids) {
      await adminApi.banAccount(id, reason, until)
    }
    await fetchList()
    alert('批量封禁完成')
  } catch (e: any) {
    alert(e.message || '批量封禁失败')
  }
}

async function batchUnban() {
  const ids = Object.keys(selectedIds.value).filter((k) => selectedIds.value[k])
  if (!ids.length) { alert('未选择用户'); return }
  if (!confirm(`确认解封选中的 ${ids.length} 个用户？`)) return
  try {
    for (const id of ids) {
      await adminApi.unbanAccount(id)
    }
    await fetchList()
    alert('批量解封完成')
  } catch (e: any) {
    alert(e.message || '批量解封失败')
  }
}

async function doUnban(id: string) {
  if (!confirm('确认解封该用户？')) return
  try {
    await adminApi.unbanAccount(id)
    await fetchList()
    alert('解封成功')
  } catch (e: any) {
    alert(e.message || '解封失败')
  }
}

async function changeRole(id: string) {
  const user = users.value.find(u => u.id === id)
  if (!user) return
  
  // 保存用户ID和当前角色
  roleEditingUser.value = { id: user.id, nickname: user.nickname, phone: user.phone, role: user.role }
  newRole.value = user.role || 'user'
  roleDialogVisible.value = true
}

async function confirmRoleChange() {
  if (!roleEditingUser.value || !newRole.value) return
  
  try {
    await adminApi.updatePermission(roleEditingUser.value.id, newRole.value)
    
    // 立即更新本地用户列表中的角色，避免重新请求
    const user = users.value.find(u => u.id === roleEditingUser.value.id)
    if (user) {
      user.role = newRole.value
    }
    
    roleDialogVisible.value = false
    alert('权限更新成功')
  } catch (e: any) {
    alert(e.message || '权限更新失败')
  }
}

function cancelRoleChange() {
  roleDialogVisible.value = false
  roleEditingUser.value = null
  newRole.value = ''
}

function toggleSelectAll() {
  if (allSelected.value) {
    // 取消全部
    clearSelection()
    return
  }
  const map: Record<string, boolean> = {}
  for (const u of users.value) map[u.id] = true
  selectedIds.value = map
  allSelected.value = true
}

function toggleSelect(id: string) {
  const cur = !!selectedIds.value[id]
  if (cur) delete selectedIds.value[id]
  else selectedIds.value[id] = true
  // 更新 allSelected
  allSelected.value = users.value.length > 0 && users.value.every((u) => !!selectedIds.value[u.id])
}

onMounted(() => {
  fetchList()
})

// 头像上传相关
const avatarFile = ref<File | null>(null)
const avatarPreview = ref<string | null>(null)

function onAvatarFileChange(e: Event) {
  const inp = e.target as HTMLInputElement
  const f = inp.files && inp.files[0]
  if (!f) return
  if (!f.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }
  
  // 验证文件大小（限制为5MB）
  if (f.size > 5 * 1024 * 1024) {
    alert('图片文件不能超过5MB')
    return
  }
  
  avatarFile.value = f
  
  // 创建预览
  const reader = new FileReader()
  reader.onload = () => {
    avatarPreview.value = reader.result as string
  }
  reader.readAsDataURL(f)
}
</script>

<template>
  <div>
    <h1 class="text-2xl font-bold mb-4">用户管理</h1>

    <div class="mb-4 flex items-center space-x-3">
      <input v-model="q" @keyup.enter="fetchList" placeholder="按用户名/邮箱搜索" class="border px-2 py-1 rounded w-64" />
      <button @click="fetchList" class="px-3 py-1 bg-blue-500 text-white rounded">搜索</button>
      <div class="flex-1"></div>
      <button @click="batchDelete" class="px-3 py-1 bg-red-500 text-white rounded">批量删除</button>
      <button @click="batchBan" class="px-3 py-1 bg-yellow-500 text-white rounded">批量封禁</button>
      <button @click="batchUnban" class="px-3 py-1 bg-green-500 text-white rounded">批量解封</button>
    </div>

    <div v-if="loading">加载中...</div>
    <div v-if="error" class="text-red-500">{{ error }}</div>

    <table class="min-w-full bg-white" v-if="users.length">
      <thead>
        <tr>
          <th class="px-4 py-2"><input type="checkbox" :checked="allSelected" @change.prevent="toggleSelectAll" /></th>
          <th class="px-4 py-2">用户名</th>
          <th class="px-4 py-2">手机号</th>
          <th class="px-4 py-2">状态</th>
          <th class="px-4 py-2">角色</th>
          <th class="px-4 py-2">操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in users" :key="u.id" class="border-t">
          <td class="px-4 py-2"><input type="checkbox" :checked="!!selectedIds[u.id]" @change.prevent="toggleSelect(u.id)" /></td>
          <td class="px-4 py-2 flex items-center space-x-2">
            <div class="w-8 h-8 rounded-full overflow-hidden flex items-center justify-center bg-gray-200">
              <img 
                v-if="getAvatarUrl(u.avatar)" 
                :src="getAvatarUrl(u.avatar)" 
                alt="avatar" 
                class="w-full h-full object-cover"
                @error="(e) => (e.target as HTMLImageElement).style.display = 'none'"
              />
              <span 
                v-if="!getAvatarUrl(u.avatar)" 
                class="text-xs font-semibold text-gray-500"
              >
                {{ getInitial(u.nickname || u.username) }}
              </span>
            </div>
            <div>{{ u.nickname || u.username || '-' }}</div>
          </td>
          <td class="px-4 py-2">{{ u.phone }}</td>
          <td class="px-4 py-2">{{ u.status }}</td>
          <td class="px-4 py-2">
            <span v-if="u.role" class="px-2 py-1 text-xs rounded" :class="getRoleBadgeClass(u.role)">
              {{ getRoleLabel(u.role) }}
            </span>
            <span v-else class="px-2 py-1 text-xs rounded bg-gray-100 text-gray-500">
              未设置
            </span>
          </td>
          <td class="px-4 py-2 space-x-2">
            <button @click="openEdit(u)" class="px-2 py-1 bg-blue-500 text-white rounded">编辑</button>
            <button @click="doDelete(u.id)" class="px-2 py-1 bg-red-500 text-white rounded">删除</button>
            <button v-if="u.status !== 'banned'" @click="doBan(u.id)" class="px-2 py-1 bg-yellow-500 text-white rounded">封禁</button>
            <button v-else @click="doUnban(u.id)" class="px-2 py-1 bg-green-500 text-white rounded">解封</button>
            <button @click="changeRole(u.id)" class="px-2 py-1 bg-gray-600 text-white rounded">权限</button>
            <router-link :to="`/admin/logs?id=${u.id}`" class="px-2 py-1 bg-indigo-600 text-white rounded">日志</router-link>
          </td>
        </tr>
      </tbody>
    </table>

    <div class="mt-4 flex items-center justify-between">
      <div>共 {{ total }} 条</div>
      <div class="space-x-2">
        <button @click="page>1&&(page-=1);fetchList()" :disabled="page<=1" class="px-3 py-1 border rounded">上一页</button>
        <span>第 {{ page }} 页</span>
        <button @click="page++ ; fetchList()" :disabled="users.length < pageSize" class="px-3 py-1 border rounded">下一页</button>
      </div>
    </div>

    <!-- 编辑弹窗（增强：头像上传、表单校验） -->
    <div v-if="editing" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded w-1/2">
        <h3 class="text-lg font-semibold mb-3">编辑用户</h3>
        <div class="space-y-2">
          <div class="flex items-center space-x-4">
            <div>
              <div class="text-sm text-gray-500">头像预览</div>
              <div class="w-20 h-20 bg-gray-100 rounded-full overflow-hidden flex items-center justify-center">
                <img 
                  v-if="avatarPreview" 
                  :src="avatarPreview" 
                  class="w-full h-full object-cover"
                />
                <img 
                  v-else-if="getAvatarUrl(selected.avatar)" 
                  :src="getAvatarUrl(selected.avatar)" 
                  class="w-full h-full object-cover"
                  @error="(e) => (e.target as HTMLImageElement).style.display = 'none'"
                />
                <div v-else class="text-2xl font-bold text-gray-400">
                  {{ getInitial(selected.nickname || selected.username) }}
                </div>
              </div>
            </div>
            <div class="flex-1">
              <label class="block text-sm text-gray-600">上传头像（可选）</label>
              <input type="file" accept="image/*" @change="onAvatarFileChange" class="text-sm" />
              <div v-if="avatarFile" class="text-xs text-green-600 mt-1">
                ✓ 已选择：{{ avatarFile.name }}
              </div>
              <div class="text-xs text-gray-400 mt-1">
                支持 JPG、PNG、GIF 格式，最大 5MB
              </div>
            </div>
          </div>

          <div>
            <label class="block text-sm text-gray-600">用户名</label>
            <input v-model="selected.nickname" class="w-full border px-2 py-1" placeholder="昵称" />
          </div>
          <div>
            <label class="block text-sm text-gray-600">手机号</label>
            <input v-model="selected.phone" class="w-full border px-2 py-1" />
          </div>
        </div>
        <div class="mt-4 flex justify-end space-x-2">
          <button @click="closeEdit" class="px-3 py-1 border rounded">取消</button>
          <button @click="saveEdit" class="px-3 py-1 bg-primary text-white rounded">保存</button>
        </div>
      </div>
    </div>

    <!-- 角色修改对话框 -->
    <div v-if="roleDialogVisible" class="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div class="bg-white p-6 rounded w-[500px] max-w-[90vw]">
        <h3 class="text-lg font-semibold mb-4">修改用户权限</h3>
        
        <div v-if="roleEditingUser" class="mb-4 p-3 bg-gray-50 rounded">
          <div class="text-sm text-gray-600">用户：<span class="font-medium text-gray-800">{{ roleEditingUser.nickname || roleEditingUser.phone }}</span></div>
          <div class="text-sm text-gray-600">当前角色：
            <span class="px-2 py-1 text-xs rounded font-medium" :class="getRoleBadgeClass(roleEditingUser.role || 'user')">
              {{ getRoleLabel(roleEditingUser.role || 'user') }}
            </span>
          </div>
        </div>

        <div class="space-y-3 mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">选择新角色：</label>
          <div v-for="role in availableRoles" :key="role.value" class="border rounded p-3 cursor-pointer hover:border-blue-500 transition"
               :class="{ 'border-blue-500 bg-blue-50': newRole === role.value }"
               @click="newRole = role.value">
            <div class="flex items-center">
              <input type="radio" :value="role.value" v-model="newRole" class="mr-3" />
              <div class="flex-1">
                <div class="font-medium text-gray-800">{{ role.label }}</div>
                <div class="text-sm text-gray-500">{{ role.description }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-yellow-600 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
            <div class="text-sm text-yellow-800">
              <div class="font-medium">注意事项：</div>
              <ul class="list-disc list-inside mt-1 space-y-1">
                <li>修改角色后，用户需重新登录才能获得新权限</li>
                <li>普通用户：只能浏览和评论</li>
                <li>Wiki管理员：可编辑Wiki和审核建议</li>
                <li>系统管理员：拥有所有权限</li>
              </ul>
            </div>
          </div>
        </div>

        <div class="flex justify-end space-x-2">
          <button @click="cancelRoleChange" class="px-4 py-2 border rounded hover:bg-gray-50">取消</button>
          <button @click="confirmRoleChange" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700" 
                  :disabled="!newRole || newRole === roleEditingUser?.role">
            确认修改
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.bg-primary { background-color: #2563eb; }
</style>
