export function displayValue(value, fallback = '未提及') {
  if (value === null || value === undefined || value === '') {
    return fallback
  }

  if (Array.isArray(value)) {
    return value.length ? value.join('、') : fallback
  }

  return value
}

export function formatDate(value) {
  if (!value) {
    return '未提及'
  }

  const date = new Date(value)
  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function getPaperTitle(paper) {
  return displayValue(paper?.title || paper?.paper_title || paper?.name, '未命名论文')
}

export function getAuthors(paper) {
  return displayValue(paper?.authors || paper?.author)
}

export function normalizeList(data) {
  if (Array.isArray(data)) {
    return data
  }

  if (Array.isArray(data?.items)) {
    return data.items
  }

  if (Array.isArray(data?.records)) {
    return data.records
  }

  if (Array.isArray(data?.list)) {
    return data.list
  }

  return []
}

export function pickContent(data, keys = ['content', 'answer', 'note', 'result']) {
  if (typeof data === 'string') {
    return data
  }

  for (const key of keys) {
    if (data?.[key]) {
      return data[key]
    }
  }

  return ''
}
