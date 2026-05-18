<template>
  <div class="page-card list-page-card">
    <div class="search-bar">
      <el-select v-model="query.module" placeholder="全部模块" clearable style="width: 160px" @change="loadData(true)">
        <el-option label="商品" value="商品" />
        <el-option label="分类" value="分类" />
        <el-option label="用户" value="用户" />
        <el-option label="认证" value="认证" />
      </el-select>
      <div style="flex: 1" />
    </div>

    <el-table :data="tableData" style="width: 100%">
      <el-table-column prop="id" label="ID" width="70" align="center" />
      <el-table-column prop="username" label="操作人" width="120" />
      <el-table-column prop="module" label="模块" width="100" align="center">
        <template #default="{ row }">
          <el-tag size="small">{{ row.module }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="action" label="操作" width="100" align="center" />
      <el-table-column prop="method" label="请求方法" min-width="200" show-overflow-tooltip />
      <el-table-column prop="ip" label="IP" width="140" align="center" />
      <el-table-column prop="created_at" label="操作时间" width="200" align="center">
        <template #default="{ row }">
          <span style="white-space: nowrap;">{{ formatTime(row.created_at) }}</span>
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
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { getLogs } from '../api'

const formatTime = (val) => {
  if (!val) return ''
  return val.replace('T', ' ').replace(/\.\d+$/, '').slice(0, 19)
}

const tableData = ref([])
const total = ref(0)
const query = reactive({ page: 1, page_size: 10, module: '' })

const loadData = async (resetPage = false) => {
  if (resetPage) query.page = 1
  const params = { ...query }
  if (!params.module) delete params.module
  const res = await getLogs(params)
  tableData.value = res.data.items
  total.value = res.data.total
  if (tableData.value.length === 0 && query.page > 1) {
    query.page = Math.max(1, Math.ceil(total.value / query.page_size))
    const retryParams = { ...query }
    if (!retryParams.module) delete retryParams.module
    const retryRes = await getLogs(retryParams)
    tableData.value = retryRes.data.items
    total.value = retryRes.data.total
  }
}

onMounted(() => loadData())
</script>
