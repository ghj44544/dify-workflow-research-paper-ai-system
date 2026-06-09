import request from './request'

export function uploadPaper(file) {
  const formData = new FormData()
  formData.append('file', file)

  return request.post('/api/papers/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function getPaperList() {
  return request.get('/api/papers')
}

export function getPaperDetail(id) {
  return request.get(`/api/papers/${id}`)
}

export function deletePaper(id) {
  return request.delete(`/api/papers/${id}`)
}

export function askPaper(id, question) {
  return request.post(`/api/papers/${id}/ask`, { question })
}

export function getQaRecords(id) {
  return request.get(`/api/papers/${id}/qa-records`)
}

export function generateNote(id, note_style) {
  return request.post(`/api/papers/${id}/note`, { note_style })
}

export function getNotes(id) {
  return request.get(`/api/papers/${id}/notes`)
}
