import request from './request'

export function chatWithResearchAssistant(data) {
  return request.post('/api/research-assistant/chat', data)
}

export function getResearchAssistantMessages() {
  return request.get('/api/research-assistant/messages')
}

export function saveResearchPaper(data) {
  return request.post('/api/research-assistant/save-paper', data)
}

export function getSavedResearchPapers() {
  return request.get('/api/research-assistant/saved-papers')
}

export function deleteSavedResearchPaper(id) {
  return request.delete(`/api/research-assistant/saved-papers/${id}`)
}
