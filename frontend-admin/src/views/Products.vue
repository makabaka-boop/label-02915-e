<template>
  <div>
    <div class="page-card list-page-card">
      <div class="search-bar">
        <el-input v-model="query.keyword" placeholder="搜索商品名称..." clearable style="width: 240px" @clear="loadData(true)" @keyup.enter="loadData(true)">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-select v-model="query.category_id" placeholder="全部分类" clearable style="width: 160px" @change="loadData(true)">
          <el-option v-for="c in categoryList" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
        <el-select v-model="query.status" placeholder="全部状态" clearable style="width: 130px" @change="loadData(true)">
          <el-option label="上架" :value="1" />
          <el-option label="下架" :value="0" />
        </el-select>
        <div style="flex: 1" />
        <el-button type="primary" :icon="Plus" @click="openDialog()">新增商品</el-button>
      </div>

      <el-table :data="tableData" style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" align="center" />
        <el-table-column label="图片" width="80" align="center">
          <template #default="{ row }">
            <el-image
              v-if="row.image"
              :src="resolveImageUrl(row.image)"
              :preview-src-list="[resolveImageUrl(row.image)]"
              fit="cover"
              style="width: 48px; height: 48px; border-radius: 8px;"
              preview-teleported
            />
            <div v-else style="width: 48px; height: 48px; border-radius: 8px; background: var(--bg-page); display: flex; align-items: center; justify-content: center; color: var(--text-muted); font-size: 12px; margin: 0 auto;">无</div>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="商品名称" min-width="180" show-overflow-tooltip />
        <el-table-column prop="category_name" label="分类" width="120" align="center" />
        <el-table-column prop="price" label="价格" width="130" align="right">
          <template #default="{ row }">
            <span style="font-weight: 600; font-variant-numeric: tabular-nums; white-space: nowrap;">¥{{ Number(row.price).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="stock" label="库存" width="90" align="center">
          <template #default="{ row }">
            <span :style="{ color: row.stock < 10 ? 'var(--danger)' : 'inherit', fontWeight: row.stock < 10 ? 600 : 400 }">
              {{ row.stock }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? '上架' : '下架' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" align="center" fixed="right">
          <template #default="{ row }">
            <div class="table-actions">
              <el-button type="primary" link size="small" @click="openDialog(row)">编辑</el-button>
              <el-popconfirm title="确定删除该商品？" @confirm="handleDelete(row.id)">
                <template #reference>
                  <el-button type="danger" link size="small">删除</el-button>
                </template>
              </el-popconfirm>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="query.page"
          v-model:page-size="query.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @size-change="loadData"
          @current-change="loadData"
        />
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑商品' : '新增商品'" width="560px" destroy-on-close>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入商品名称" />
      </el-form-item>
      <el-form-item label="分类" prop="category_id">
        <el-select v-model="form.category_id" placeholder="请选择分类" style="width: 100%">
          <el-option v-for="c in categoryList" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="价格" prop="price">
        <el-input-number v-model="form.price" :min="0" :precision="2" :step="1" style="width: 100%" />
      </el-form-item>
      <el-form-item label="库存" prop="stock">
        <el-input-number v-model="form.stock" :min="0" :step="1" style="width: 100%" />
      </el-form-item>
      <el-form-item label="图片" prop="image">
        <el-upload
          class="image-uploader"
          :show-file-list="false"
          :http-request="handleUpload"
          accept=".jpg,.jpeg,.png,.gif,.webp"
        >
          <img v-if="form.image" :src="imagePreviewUrl" class="upload-preview" alt="商品图片" />
          <div v-else class="upload-placeholder">
            <el-icon :size="24"><Plus /></el-icon>
            <span>点击上传</span>
          </div>
        </el-upload>
      </el-form-item>
      <el-form-item label="描述">
        <el-input v-model="form.description" type="textarea" :rows="3" placeholder="商品描述(可选)" />
      </el-form-item>
      <el-form-item label="状态">
        <el-switch v-model="form.status" :active-value="1" :inactive-value="0" active-text="上架" inactive-text="下架" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
    </template>
  </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Search, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { getProducts, createProduct, updateProduct, deleteProduct, getAllCategories, uploadImage } from '../api'

const tableData = ref([])
const total = ref(0)
const categoryList = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref(null)
const submitLoading = ref(false)
const formRef = ref(null)

const query = reactive({ page: 1, page_size: 10, keyword: '', category_id: null, status: null })

const form = reactive({ name: '', category_id: null, price: 0, stock: 0, image: '', description: '', status: 1 })

const rules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择分类', trigger: 'change' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
}

const loadData = async (resetPage = false) => {
  if (resetPage) query.page = 1
  const params = { ...query }
  if (!params.keyword) delete params.keyword
  if (!params.category_id) delete params.category_id
  if (params.status === null || params.status === '') delete params.status
  const res = await getProducts(params)
  tableData.value = res.data.items
  total.value = res.data.total
  if (tableData.value.length === 0 && query.page > 1) {
    query.page = Math.max(1, Math.ceil(total.value / query.page_size))
    const retryParams = { ...query }
    if (!retryParams.keyword) delete retryParams.keyword
    if (!retryParams.category_id) delete retryParams.category_id
    if (retryParams.status === null || retryParams.status === '') delete retryParams.status
    const retryRes = await getProducts(retryParams)
    tableData.value = retryRes.data.items
    total.value = retryRes.data.total
  }
}

const loadCategories = async () => {
  const res = await getAllCategories()
  categoryList.value = res.data
}

const resolveImageUrl = (url) => {
  if (!url) return ''
  if (url.startsWith('http')) return url
  if (url.startsWith('/uploads/')) return url
  return `/api${url}`
}

const imagePreviewUrl = computed(() => resolveImageUrl(form.image))

const handleUpload = async ({ file }) => {
  try {
    const res = await uploadImage(file)
    form.image = res.data.url
    ElMessage.success('上传成功')
  } catch {
    ElMessage.error('上传失败')
  }
}

const openDialog = (row) => {
  isEdit.value = !!row
  editId.value = row?.id || null
  Object.assign(form, row ? {
    name: row.name, category_id: row.category_id, price: Number(row.price),
    stock: row.stock, image: row.image || '', description: row.description || '', status: row.status,
  } : { name: '', category_id: null, price: 0, stock: 0, image: '', description: '', status: 1 })
  dialogVisible.value = true
}

const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updateProduct(editId.value, form)
      ElMessage.success('更新成功')
    } else {
      await createProduct(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadData()
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = async (id) => {
  await deleteProduct(id)
  ElMessage.success('删除成功')
  loadData()
}

onMounted(() => {
  loadData()
  loadCategories()
})
</script>
