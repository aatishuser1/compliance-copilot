import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

export type UploadResponse = {
  document_id: string
  filename: string
  page_count: number
  chunk_count: number
  message: string
}

export type DocumentInfo = {
  document_id: string
  filename: string
  page_count?: number
  chunk_count?: number
  upload_time?: string
}

export type SourceChunk = {
  page: number
  chunk: number
  excerpt: string
  section?: string | null
}

export type ChatResponse = {
  answer: string
  sources: SourceChunk[]
  found_in_document: boolean
}

export type ComplianceSummary = {
  overview: string
  key_obligations: string[]
  risks: string[]
  missing_information: string[]
  recommendations: string[]
}

export type SummaryResponse = {
  document_id: string
  summary: ComplianceSummary
}

export type ApiError = {
  error: string
  detail?: string
}

export function getErrorMessage(err: unknown, fallback: string): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as ApiError | { detail?: string } | undefined
    if (data && 'error' in data && data.error) return data.error
    if (data && 'detail' in data && data.detail) return data.detail
  }
  return fallback
}

export async function uploadPdf(file: File, onProgress?: (percent: number) => void) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<UploadResponse>('/api/upload', form, {
    onUploadProgress: (event) => {
      if (!onProgress || !event.total) return
      onProgress(Math.round((event.loaded / event.total) * 100))
    },
  })
  return data
}

export async function listDocuments() {
  const { data } = await api.get<DocumentInfo[]>('/api/upload/documents')
  return data
}

export async function askQuestion(documentId: string, question: string) {
  const { data } = await api.post<ChatResponse>('/api/chat', {
    document_id: documentId,
    question,
  })
  return data
}

export async function getSummary(documentId: string) {
  const { data } = await api.post<SummaryResponse>('/api/summary', {
    document_id: documentId,
  })
  return data
}
