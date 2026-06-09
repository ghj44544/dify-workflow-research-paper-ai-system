import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getPaperList } from '../api/paper'
import { normalizeList } from '../utils/format'

export const usePaperStore = defineStore('paper', () => {
  const papers = ref([])
  const loading = ref(false)

  async function fetchPapers() {
    loading.value = true
    try {
      const data = await getPaperList()
      papers.value = normalizeList(data)
    } finally {
      loading.value = false
    }
  }

  return {
    papers,
    loading,
    fetchPapers
  }
})
