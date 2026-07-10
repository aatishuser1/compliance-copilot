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

export type Priority = 'critical' | 'high' | 'medium' | 'low'
export type Severity = 'critical' | 'high' | 'medium' | 'low'
export type Effort = 'low' | 'medium' | 'high'
export type RiskLevel = 'critical' | 'high' | 'medium' | 'low'

export type SourceReference = {
  page: number
  chunk?: number | null
  section?: string | null
  excerpt?: string | null
}

export type ComplianceObligation = {
  id: string
  title: string
  description: string
  priority: Priority
  category?: string | null
  deadline?: string | null
  sources: SourceReference[]
}

export type ComplianceRisk = {
  id: string
  title: string
  description: string
  severity: Severity
  likelihood?: string | null
  related_obligation_ids: string[]
  sources: SourceReference[]
}

export type CompliancePenalty = {
  id: string
  description: string
  amount_or_range?: string | null
  penalty_type?: string | null
  trigger?: string | null
  related_obligation_ids: string[]
  sources: SourceReference[]
}

export type RecommendedAction = {
  id: string
  title: string
  description: string
  priority: Priority
  effort: Effort
  related_risk_ids: string[]
  related_obligation_ids: string[]
}

export type ComplianceSummary = {
  overview: string
  document_type?: string | null
  regulatory_framework?: string | null
  risk_level: RiskLevel
  obligations: ComplianceObligation[]
  risks: ComplianceRisk[]
  penalties: CompliancePenalty[]
  missing_information: string[]
  recommended_actions: RecommendedAction[]
  analysis_notes?: string | null
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
