<template>
  <div class="admin-panel-layout">
    <!-- Header tabs -->
    <div class="admin-tabs premium-card">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'employees' }" 
        @click="activeTab = 'employees'"
      >
        <Users class="tab-icon" />
        Employees Directory
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'stores' }" 
        @click="activeTab = 'stores'"
      >
        <Building class="tab-icon" />
        Sucursales / Stores
      </button>
    </div>

    <!-- EMPLOYEES TAB CONTENT -->
    <div v-if="activeTab === 'employees'" class="tab-content">
      <div class="section-header-bar">
        <div>
          <h2 class="section-title">Manage Staff</h2>
          <p class="section-desc">Create and assign register operators, set store assignments, and generate temporal access codes.</p>
        </div>
        <button class="pos-btn pos-btn-accent" @click="openEmployeeModal">
          <Plus class="btn-icon" />
          Add Employee
        </button>
      </div>

      <!-- Employees Grid / Table -->
      <div class="directory-list-card premium-card">
        <div class="table-container" v-if="employees.length">
          <table class="pos-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Full Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Role</th>
                <th>Sucursal / Store</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="emp in employees" :key="emp.id">
                <td class="username-cell">
                  <span class="user-avatar-small">{{ emp.username.charAt(0).toUpperCase() }}</span>
                  <div class="username-meta">
                    <span class="uname">{{ emp.username }}</span>
                    <span class="pwd-flag" v-if="emp.must_change_password">Needs password change</span>
                  </div>
                </td>
                <td>{{ emp.first_name || '-' }} {{ emp.last_name || '' }} {{ emp.second_last_name || '' }}</td>
                <td>{{ emp.email }}</td>
                <td>{{ emp.contact_phone || '-' }}</td>
                <td>
                  <span class="role-badge" :class="emp.role?.toLowerCase() || 'operator'">
                    {{ emp.role?.toUpperCase() || 'OPERATOR' }}
                  </span>
                </td>
                <td>
                  <span class="store-tag" v-if="emp.store_name">
                    {{ emp.store_name }} ({{ emp.store_code }})
                  </span>
                  <span class="store-tag unassigned" v-else>Unassigned</span>
                </td>
                <td>
                  <span class="status-dot-badge" :class="emp.is_active ? 'active' : 'inactive'">
                    <span class="status-dot"></span>
                    {{ emp.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="empty-directory-state" v-else>
          <Users class="empty-state-icon" />
          <p>No employees registered yet.</p>
        </div>
      </div>
    </div>

    <!-- STORES TAB CONTENT -->
    <div v-if="activeTab === 'stores'" class="tab-content">
      <div class="section-header-bar">
        <div>
          <h2 class="section-title">Sucursales (Stores)</h2>
          <p class="section-desc">Add store locations and code identifiers. Coding letters are used automatically for employee usernames.</p>
        </div>
        <button class="pos-btn pos-btn-accent" @click="openStoreModal">
          <Plus class="btn-icon" />
          Add Store
        </button>
      </div>

      <!-- Stores Grid -->
      <div class="stores-grid" v-if="stores.length">
        <div class="store-card premium-card" v-for="st in stores" :key="st.id">
          <div class="store-card-header">
            <div class="store-title-block">
              <Building class="store-icon" />
              <h3>{{ st.name }}</h3>
            </div>
            <span class="store-code-badge">ID Code: {{ st.code.toUpperCase() }}</span>
          </div>
          <div class="store-card-body">
            <div class="meta-row">
              <span class="meta-label">Location:</span>
              <span class="meta-val">{{ st.location || 'N/A' }}</span>
            </div>
            <div class="meta-row">
              <span class="meta-label">Address:</span>
              <span class="meta-val">{{ st.address || 'N/A' }}</span>
            </div>
          </div>
          <div class="store-card-footer">
            <button class="circle-action-btn edit" @click="openEditStoreModal(st)" title="Edit Store">
              <Edit class="btn-icon-small" />
            </button>
            <button class="circle-action-btn delete" @click="deleteStore(st.id)" title="Delete Store">
              <Trash2 class="btn-icon-small" />
            </button>
          </div>
        </div>
      </div>
      <div class="empty-directory-state premium-card" v-else>
        <Building class="empty-state-icon" />
        <p>No store locations created yet.</p>
      </div>
    </div>

    <!-- ADD/EDIT STORE MODAL -->
    <div class="modal-overlay" v-if="showStoreModal" @click="showStoreModal = false">
      <div class="pos-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditStore ? 'Edit Store Details' : 'Register New Sucursal' }}</h3>
          <button class="close-btn" @click="showStoreModal = false">
            <X />
          </button>
        </div>
        <form @submit.prevent="saveStore" class="modal-form">
          <div class="form-group">
            <label>Store Name *</label>
            <input type="text" v-model="storeForm.name" placeholder="e.g. West Wing" class="pos-input" required />
          </div>
          <div class="form-group">
            <label>Store Code (1-3 Letters) *</label>
            <input 
              type="text" 
              v-model="storeForm.code" 
              placeholder="e.g. W" 
              class="pos-input" 
              required 
              maxlength="3" 
              style="text-transform: uppercase;"
            />
            <small class="form-help">This letter code is appended to employee usernames (e.g., john.d.<b>w</b>12).</small>
          </div>
          <div class="form-group">
            <label>Location / Floor</label>
            <input type="text" v-model="storeForm.location" placeholder="e.g. Building A, 1st Floor" class="pos-input" />
          </div>
          <div class="form-group">
            <label>Full Address</label>
            <input type="text" v-model="storeForm.address" placeholder="e.g. 100 Main Street" class="pos-input" />
          </div>
          <div class="modal-footer">
            <button type="button" class="pos-btn pos-btn-secondary" @click="showStoreModal = false">Cancel</button>
            <button type="submit" class="pos-btn pos-btn-accent">Save Store</button>
          </div>
        </form>
      </div>
    </div>

    <!-- REGISTER EMPLOYEE MODAL -->
    <div class="modal-overlay" v-if="showEmployeeModal" @click="closeEmployeeModal">
      <div class="pos-modal employee-modal" @click.stop>
        <div class="modal-header">
          <h3>Register New Store Employee</h3>
          <button class="close-btn" @click="closeEmployeeModal">
            <X />
          </button>
        </div>
        
        <!-- Registration Form -->
        <form v-if="!credentialsResult" @submit.prevent="registerEmployee" class="modal-form">
          <div class="form-row">
            <div class="form-group">
              <label>First Name *</label>
              <input type="text" v-model="empForm.first_name" placeholder="e.g. John" class="pos-input" required />
            </div>
            <div class="form-group">
              <label>First Surname *</label>
              <input type="text" v-model="empForm.last_name" placeholder="e.g. Doe" class="pos-input" required />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Second Surname (Optional)</label>
              <input type="text" v-model="empForm.second_last_name" placeholder="e.g. Smith" class="pos-input" />
            </div>
            <div class="form-group">
              <label>Contact Phone</label>
              <input type="text" v-model="empForm.contact_phone" placeholder="e.g. 555-0199" class="pos-input" />
            </div>
          </div>

          <div class="form-group">
            <label>Email Address *</label>
            <input type="email" v-model="empForm.email" placeholder="e.g. john.doe@apexpos.com" class="pos-input" required />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>User Type / Role *</label>
              <select v-model="empForm.user_type_id" class="pos-input" required>
                <option :value="3">Operator (Cashier)</option>
                <option :value="2">Manager (Supervisor)</option>
              </select>
            </div>
            <div class="form-group">
              <label>Assign to Sucursal *</label>
              <select v-model="empForm.store_id" class="pos-input" required>
                <option :value="null" disabled>Select Store Assignment</option>
                <option v-for="st in stores" :key="st.id" :value="st.id">
                  {{ st.name }} ({{ st.code.toUpperCase() }})
                </option>
              </select>
            </div>
          </div>

          <div class="modal-footer">
            <button type="button" class="pos-btn pos-btn-secondary" @click="closeEmployeeModal">Cancel</button>
            <button type="submit" class="pos-btn pos-btn-accent">Generate Employee Access</button>
          </div>
        </form>

        <!-- Credentials Result Box -->
        <div v-else class="credentials-result-container">
          <div class="success-icon-badge">
            <Check class="check-icon" />
          </div>
          <h4>Employee Created Successfully!</h4>
          <p class="credential-desc">Please share these temporary credentials with the employee. They will be forced to change their password on their first login.</p>
          
          <div class="credentials-card">
            <div class="credential-line">
              <span class="label">Username:</span>
              <div class="val-copy-box">
                <span class="val">{{ credentialsResult.username }}</span>
                <button class="copy-btn" @click="copyText(credentialsResult.username, 'username')">
                  <Copy class="copy-icon" v-if="copiedField !== 'username'" />
                  <span class="copied-text" v-else>Copied!</span>
                </button>
              </div>
            </div>

            <div class="credential-line">
              <span class="label">Temporary Password:</span>
              <div class="val-copy-box">
                <span class="val temp-pwd">{{ credentialsResult.password }}</span>
                <button class="copy-btn" @click="copyText(credentialsResult.password, 'password')">
                  <Copy class="copy-icon" v-if="copiedField !== 'password'" />
                  <span class="copied-text" v-else>Copied!</span>
                </button>
              </div>
            </div>
          </div>

          <div class="credentials-actions">
            <button class="pos-btn pos-btn-accent full-width" @click="closeEmployeeModal">Done</button>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { Users, Building, Plus, X, Edit, Trash2, Check, Copy, Key } from 'lucide-vue-next'

const activeTab = ref('employees')
const employees = ref([])
const stores = ref([])

// Store Modals
const showStoreModal = ref(false)
const isEditStore = ref(false)
const editStoreId = ref(null)
const storeForm = ref({
  name: '',
  code: '',
  location: '',
  address: ''
})

// Employee Modals
const showEmployeeModal = ref(false)
const empForm = ref({
  first_name: '',
  last_name: '',
  second_last_name: '',
  contact_phone: '',
  email: '',
  user_type_id: 3,
  store_id: null
})

// Generated Result
const credentialsResult = ref(null)
const copiedField = ref(null)

const loadData = async () => {
  try {
    const [storesRes, usersRes] = await Promise.all([
      axios.get('/api/stores'),
      axios.get('/api/auth/users')
    ])
    stores.value = storesRes.data
    // Filter to display only Managers and Operators in the directory
    employees.value = usersRes.data.filter(u => u.role !== 'admin')
  } catch (err) {
    console.error('Failed to load admin management data', err)
  }
}

// Store CRUD
const openStoreModal = () => {
  isEditStore.value = false
  editStoreId.value = null
  storeForm.value = { name: '', code: '', location: '', address: '' }
  showStoreModal.value = true
}

const openEditStoreModal = (st) => {
  isEditStore.value = true
  editStoreId.value = st.id
  storeForm.value = {
    name: st.name,
    code: st.code,
    location: st.location || '',
    address: st.address || ''
  }
  showStoreModal.value = true
}

const saveStore = async () => {
  try {
    // Upper case the code
    storeForm.value.code = storeForm.value.code.toUpperCase()
    
    if (isEditStore.value) {
      await axios.put(`/api/stores/${editStoreId.value}`, storeForm.value)
    } else {
      await axios.post('/api/stores', storeForm.value)
    }
    showStoreModal.value = false
    await loadData()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to save store info')
  }
}

const deleteStore = async (id) => {
  if (!confirm('Are you sure you want to delete this store location? Users assigned to this store will be detached.')) return
  try {
    await axios.delete(`/api/stores/${id}`)
    await loadData()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete store')
  }
}

// Employee Registration
const openEmployeeModal = () => {
  empForm.value = {
    first_name: '',
    last_name: '',
    second_last_name: '',
    contact_phone: '',
    email: '',
    user_type_id: 3,
    store_id: stores.value.length > 0 ? stores.value[0].id : null
  }
  credentialsResult.value = null
  copiedField.value = null
  showEmployeeModal.value = true
}

const closeEmployeeModal = () => {
  showEmployeeModal.value = false
  credentialsResult.value = null
  copiedField.value = null
}

const registerEmployee = async () => {
  try {
    const response = await axios.post('/api/auth/employees', empForm.value)
    credentialsResult.value = {
      username: response.data.user.username,
      password: response.data.temporal_password
    }
    await loadData()
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to register new employee')
  }
}

const copyText = (text, field) => {
  navigator.clipboard.writeText(text)
  copiedField.value = field
  setTimeout(() => {
    if (copiedField.value === field) {
      copiedField.value = null
    }
  }, 2000)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.admin-panel-layout {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.admin-tabs {
  display: flex;
  gap: 8px;
  padding: 8px;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-weight: 500;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn:hover {
  background-color: var(--bg-body);
  color: var(--text-primary);
}

.tab-btn.active {
  background-color: var(--accent-lime);
  color: var(--bg-app);
  font-weight: 600;
}

.tab-icon {
  width: 18px;
  height: 18px;
}

.section-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.section-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

/* Directory table */
.directory-list-card {
  padding: 24px;
}

.table-container {
  overflow-x: auto;
}

.pos-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.pos-table th {
  padding: 14px 16px;
  font-size: 12px;
  text-transform: uppercase;
  color: var(--text-secondary);
  font-weight: 600;
  border-bottom: 1px solid var(--border-color);
}

.pos-table td {
  padding: 16px;
  font-size: 14px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
}

.username-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar-small {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: var(--bg-body);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  border: 1px solid var(--border-color);
}

.username-meta {
  display: flex;
  flex-direction: column;
}

.uname {
  font-weight: 500;
}

.pwd-flag {
  font-size: 11px;
  color: #f87171;
  font-weight: 400;
  margin-top: 2px;
}

.store-tag {
  display: inline-block;
  padding: 4px 8px;
  background-color: var(--bg-body);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
}

.store-tag.unassigned {
  background-color: rgba(239, 68, 68, 0.05);
  border-color: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.status-dot-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 500;
}

.status-dot-badge .status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.status-dot-badge.active {
  color: var(--accent-lime);
}
.status-dot-badge.active .status-dot {
  background-color: var(--accent-lime);
}

.status-dot-badge.inactive {
  color: var(--text-secondary);
}
.status-dot-badge.inactive .status-dot {
  background-color: var(--text-secondary);
}

.empty-directory-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--text-secondary);
}

.empty-state-icon {
  width: 48px;
  height: 48px;
  color: var(--border-color);
  margin-bottom: 16px;
}

/* Stores tab grid */
.stores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.store-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.store-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 12px;
}

.store-title-block {
  display: flex;
  align-items: center;
  gap: 12px;
}

.store-title-block h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.store-icon {
  width: 22px;
  height: 22px;
  color: var(--accent-lime);
}

.store-code-badge {
  font-size: 11px;
  background-color: var(--bg-body);
  border: 1px solid var(--border-color);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: monospace;
  font-weight: 600;
}

.store-card-body {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.meta-label {
  color: var(--text-secondary);
}

.meta-val {
  color: var(--text-primary);
  font-weight: 500;
  text-align: right;
}

.store-card-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  border-top: 1px solid var(--border-color);
  padding-top: 12px;
}

.circle-action-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 1px solid var(--border-color);
  background-color: var(--bg-body);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.circle-action-btn:hover {
  background-color: var(--border-color);
}

.circle-action-btn.edit {
  color: var(--text-primary);
}

.circle-action-btn.delete {
  color: #f87171;
}
.circle-action-btn.delete:hover {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.2);
}

.btn-icon-small {
  width: 14px;
  height: 14px;
}

/* Modals & Forms */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pos-modal {
  background-color: #ffffff;
  width: 100%;
  max-width: 480px;
  border-radius: var(--radius-lg);
  padding: 24px;
  box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1), 0 10px 10px -5px rgba(0,0,0,0.04);
  animation: modal-enter var(--transition-medium) ease-out;
}

.pos-modal.employee-modal {
  max-width: 580px;
}

@keyframes modal-enter {
  from {
    transform: scale(0.95);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: var(--text-primary);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-group {
  flex: 1;
}

.form-help {
  font-size: 11px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}

/* Credentials Output Box */
.credentials-result-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 16px 0;
}

.success-icon-badge {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background-color: rgba(184, 241, 90, 0.15);
  color: var(--accent-lime);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
}

.check-icon {
  width: 28px;
  height: 28px;
  stroke-width: 3px;
}

.credentials-result-container h4 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.credential-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 24px;
  max-width: 400px;
}

.credentials-card {
  width: 100%;
  background-color: var(--bg-body);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.credential-line {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}

.credential-line .label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-secondary);
}

.val-copy-box {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #ffffff;
  border: 1px solid var(--border-color);
  padding: 10px 14px;
  border-radius: var(--radius-sm);
}

.val-copy-box .val {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  font-family: monospace;
}

.val-copy-box .val.temp-pwd {
  color: var(--accent-lime);
  background-color: #111111;
  padding: 2px 6px;
  border-radius: 4px;
}

.copy-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--text-secondary);
  font-size: 12px;
  font-weight: 500;
}

.copy-btn:hover {
  color: var(--text-primary);
}

.copy-icon {
  width: 16px;
  height: 16px;
}

.copied-text {
  color: var(--accent-lime);
  font-weight: 600;
}

.full-width {
  width: 100%;
}
</style>
