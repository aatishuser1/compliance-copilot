import { useEffect, useRef, useState } from 'react'
import {
  askQuestion,
  getErrorMessage,
  getSummary,
  listDocuments,
  uploadPdf,
  type ChatResponse,
  type ComplianceSummary,
  type DocumentInfo,
  type Priority,
  type RiskLevel,
  type Severity,
  type SourceReference,
} from './api'

// Icons as simple SVG components
const UploadIcon = () => (
  <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
  </svg>
)

const CheckIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
  </svg>
)

const CopyIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
  </svg>
)

const TrashIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
  </svg>
)

const Spinner = () => (
  <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth={4} />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
  </svg>
)

const DocumentIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
)

const ClockIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
)

const PageIcon = () => (
  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
  </svg>
)

const RiskIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
  </svg>
)

const WarningIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
  </svg>
)

const LightbulbIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
  </svg>
)

const OverviewIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
  </svg>
)

const CloseIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
  </svg>
)

type ChatMessage = {
  role: 'user' | 'assistant'
  content: string
  sources?: ChatResponse['sources']
  timestamp?: string
}

function App() {
  const [documents, setDocuments] = useState<DocumentInfo[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [summary, setSummary] = useState<ComplianceSummary | null>(null)
  const [loading, setLoading] = useState('')
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [lastUploadedFile, setLastUploadedFile] = useState<string | null>(null)
  const chatEndRef = useRef<HTMLDivElement>(null)

  async function loadDocuments() {
    const docs = await listDocuments()
    setDocuments(docs)
    if (docs.length > 0 && !selectedId) {
      setSelectedId(docs[0].document_id)
    }
  }

  useEffect(() => {
    loadDocuments().catch(() => {
      setError('Could not reach the backend. Start the API on port 8000.')
    })
  }, [])

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]
    if (!file) return

    setLoading('upload')
    setUploadProgress(0)
    setError('')
    setSuccess('')
    try {
      const result = await uploadPdf(file, setUploadProgress)
      setSelectedId(result.document_id)
      setMessages([])
      setSummary(null)
      setLastUploadedFile(result.filename)
      await loadDocuments()
      setSuccess(`${result.filename} uploaded successfully.`)
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Upload failed.'))
    } finally {
      setLoading('')
      setUploadProgress(0)
      e.target.value = ''
    }
  }

  async function handleChat(e: React.FormEvent) {
    e.preventDefault()
    if (!selectedId || !question.trim() || loading) return

    const userQuestion = question.trim()
    setQuestion('')
    setMessages((prev) => [
      ...prev,
      { role: 'user', content: userQuestion, timestamp: new Date().toISOString() },
    ])
    setLoading('chat')
    setError('')

    try {
      const result = await askQuestion(selectedId, userQuestion)
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: result.answer,
          sources: result.sources,
          timestamp: new Date().toISOString(),
        },
      ])
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Chat request failed.'))
    } finally {
      setLoading('')
    }
  }

  async function handleSummary() {
    if (!selectedId || loading) return

    setLoading('summary')
    setError('')
    setSuccess('')
    try {
      const result = await getSummary(selectedId)
      setSummary(result.summary)
      setSuccess('Compliance intelligence generated.')
    } catch (err: unknown) {
      setError(getErrorMessage(err, 'Summary request failed.'))
    } finally {
      setLoading('')
    }
  }

  const selectedDocument = documents.find((doc) => doc.document_id === selectedId)
  const isBusy = loading !== ''

  const formatTimestamp = (isoString: string) => {
    const date = new Date(isoString)
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const formatUploadTime = (isoString: string | undefined) => {
    if (!isoString) return null
    const date = new Date(isoString)
    if (isNaN(date.getTime())) return null
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    return date.toLocaleDateString()
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  return (
    <div className="min-h-screen bg-white text-slate-900 overflow-x-hidden">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-[1400px] items-center justify-between px-4 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white">
              <DocumentIcon />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-slate-900">Compliance Copilot</h1>
              <p className="text-sm text-slate-500">
                Upload documents, ask questions, and generate compliance intelligence.
              </p>
            </div>
          </div>
        </div>
      </header>

      {(error || success) && (
        <div className="mx-auto max-w-[1400px] px-4 pt-4 sm:px-6">
          {error && (
            <div className="mb-3 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              <RiskIcon />
              <span>{error}</span>
              <button
                onClick={() => setError('')}
                className="ml-auto text-red-400 hover:text-red-600"
                aria-label="Close error"
              >
                <CloseIcon />
              </button>
            </div>
          )}
          {success && (
            <div className="mb-3 flex items-center gap-2 rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
              <CheckIcon />
              <span>{success}</span>
              <button
                onClick={() => setSuccess('')}
                className="ml-auto text-emerald-400 hover:text-emerald-600"
                aria-label="Close success"
              >
                <CloseIcon />
              </button>
            </div>
          )}
        </div>
      )}

      <main className="mx-auto grid max-w-[1400px] gap-8 px-4 py-8 sm:px-6 lg:grid-cols-[340px_1fr] grid-cols-1">
        <aside className="space-y-6 lg:order-first order-last">
          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Upload Document
            </h2>
            <label
              className={`mt-4 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed px-4 py-10 text-center transition-colors ${
                loading === 'upload'
                  ? 'border-blue-300 bg-blue-50'
                  : 'border-slate-300 bg-slate-50 hover:border-slate-400 hover:bg-slate-100'
              }`}
            >
              <input
                type="file"
                accept=".pdf,application/pdf"
                className="hidden"
                onChange={handleUpload}
                disabled={loading === 'upload'}
              />
              {loading === 'upload' ? (
                <div className="flex flex-col items-center">
                  <Spinner />
                  <p className="mt-3 text-sm font-medium text-slate-700">
                    {uploadProgress < 30 ? 'Extracting text...' : uploadProgress < 60 ? 'Generating embeddings...' : 'Finalizing...'}
                  </p>
                  <div className="mt-3 w-48">
                    <div className="h-2 overflow-hidden rounded-full bg-slate-200">
                      <div
                        className="h-full rounded-full bg-blue-600 transition-all duration-300"
                        style={{ width: `${uploadProgress || 15}%` }}
                      />
                    </div>
                    <p className="mt-1 text-xs text-slate-500">{Math.round(uploadProgress)}%</p>
                  </div>
                </div>
              ) : lastUploadedFile ? (
                <div className="flex flex-col items-center">
                  <div className="flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100 text-emerald-600">
                    <CheckIcon />
                  </div>
                  <p className="mt-3 text-sm font-medium text-emerald-700">
                    Uploaded Successfully
                  </p>
                  <p className="mt-1 text-sm text-slate-600">{lastUploadedFile}</p>
                  <span className="mt-4 text-sm text-blue-600 hover:text-blue-700">
                    Click to replace document
                  </span>
                </div>
              ) : (
                <>
                  <UploadIcon />
                  <span className="mt-3 text-sm font-medium text-slate-700">
                    Drop a compliance PDF here or click to browse
                  </span>
                  <span className="mt-1 text-xs text-slate-500">PDF only, up to 25 MB</span>
                </>
              )}
            </label>
          </section>

          <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Documents
            </h2>
            {documents.length === 0 ? (
              <div className="mt-4 flex flex-col items-center py-8 text-center">
                <DocumentIcon />
                <p className="mt-3 text-sm text-slate-500">
                  No documents yet. Upload a compliance PDF to get started.
                </p>
              </div>
            ) : (
              <ul className="mt-4 space-y-2">
                {documents.map((doc) => (
                  <li key={doc.document_id}>
                    <button
                      type="button"
                      onClick={() => {
                        setSelectedId(doc.document_id)
                        setMessages([])
                        setSummary(null)
                      }}
                      className={`w-full rounded-xl border px-4 py-3 text-left text-sm transition focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 hover:shadow-sm ${
                        selectedId === doc.document_id
                          ? 'border-blue-500 bg-blue-50 text-blue-900 shadow-sm'
                          : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'
                      }`}
                      aria-label={`Select document ${doc.filename}`}
                      aria-pressed={selectedId === doc.document_id}
                    >
                      <div className="flex items-start gap-3">
                        <DocumentIcon />
                        <div className="flex-1 min-w-0">
                          <div className="font-medium truncate">{doc.filename}</div>
                          <div
                            className={`mt-1 flex items-center gap-2 text-xs ${
                              selectedId === doc.document_id
                                ? 'text-blue-600'
                                : 'text-slate-500'
                            }`}
                          >
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="inline-flex items-center gap-1 text-xs">
                                <CheckIcon />
                                Indexed
                              </span>
                              <span>·</span>
                              <span className="flex items-center gap-1">
                                <PageIcon />
                                {doc.page_count ?? 0} Pages
                              </span>
                              {formatUploadTime(doc.upload_time) && (
                                <>
                                  <span>·</span>
                                  <span className="flex items-center gap-1">
                                    <ClockIcon />
                                    {formatUploadTime(doc.upload_time)}
                                  </span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        {selectedId === doc.document_id && (
                          <span className="text-blue-600">
                            <CheckIcon />
                          </span>
                        )}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </aside>

        <section className="space-y-6">
          <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5 flex items-center justify-between gap-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  {selectedDocument && <DocumentIcon />}
                  <h2 className="text-lg font-semibold text-slate-900">
                    {selectedDocument ? selectedDocument.filename : 'Chat'}
                  </h2>
                </div>
                {selectedDocument && (
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="inline-flex items-center gap-1 rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-800">
                      <CheckIcon />
                      Ready
                    </span>
                    <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-800">
                      <CheckIcon />
                      Indexed
                    </span>
                    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                      <PageIcon />
                      {selectedDocument.page_count ?? 0} Pages
                    </span>
                    <span className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                      {selectedDocument.chunk_count ?? 0} Chunks
                    </span>
                  </div>
                )}
                {!selectedDocument && (
                  <p className="text-sm text-slate-500">
                    Upload a compliance document to begin.
                  </p>
                )}
              </div>
              {messages.length > 0 && (
                <button
                  type="button"
                  onClick={() => setMessages([])}
                  className="flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-100 disabled:opacity-50"
                  disabled={isBusy}
                  aria-label="Clear chat"
                >
                  <TrashIcon />
                  Clear
                </button>
              )}
            </div>

            <div className="mb-4 h-[400px] overflow-y-auto rounded-xl border border-slate-200 bg-slate-50 p-4">
              {!selectedId ? (
                <div className="flex h-full flex-col items-center justify-center text-center">
                  <DocumentIcon />
                  <p className="mt-3 text-sm text-slate-500">
                    Upload a compliance document to begin.
                  </p>
                </div>
              ) : messages.length === 0 ? (
                <div className="flex h-full flex-col items-center justify-center text-center">
                  <LightbulbIcon />
                  <p className="mt-3 text-sm text-slate-500">
                    Ask a question about the uploaded document.
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex gap-3 ${
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {message.role === 'assistant' && (
                        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white">
                          <DocumentIcon />
                        </div>
                      )}
                      <div
                        className={`rounded-2xl px-5 py-4 text-sm ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white max-w-[75%]'
                            : 'bg-white text-slate-800 shadow-sm border border-slate-200 max-w-[75%]'
                        }`}
                      >
                        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                        {message.sources && message.sources.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-slate-200">
                            <p className="text-xs font-semibold text-slate-500 mb-2">Sources</p>
                            <div className="flex flex-wrap gap-2">
                              {message.sources.map((source) => (
                                <span
                                  key={`${source.page}-${source.chunk}`}
                                  className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-700"
                                >
                                  <PageIcon />
                                  Page {source.page}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}
                        {message.timestamp && (
                          <div className="mt-2 flex items-center justify-between">
                            <span className={`text-xs ${
                              message.role === 'user' ? 'text-blue-200' : 'text-slate-400'
                            }`}>
                              {formatTimestamp(message.timestamp)}
                            </span>
                            {message.role === 'assistant' && (
                              <button
                                onClick={() => copyToClipboard(message.content)}
                                className="text-slate-400 hover:text-slate-600"
                                aria-label="Copy answer"
                              >
                                <CopyIcon />
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  {loading === 'chat' && (
                    <div className="flex gap-3">
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white">
                        <Spinner />
                      </div>
                      <div className="rounded-2xl bg-white px-4 py-3 shadow-sm border border-slate-200">
                        <p className="text-sm text-slate-500">Searching the document...</p>
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
              )}
            </div>

            <form onSubmit={handleChat} className="flex gap-2">
              <div className="flex-1 relative">
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault()
                      handleChat(e)
                    }
                  }}
                  placeholder="Ask a question about this document..."
                  rows={1}
                  className="w-full resize-none rounded-xl border border-slate-300 px-4 py-3 pr-16 text-sm outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-slate-100 disabled:opacity-50"
                  disabled={!selectedId || isBusy}
                  maxLength={2000}
                  aria-label="Chat input"
                />
                <span className="absolute bottom-3 right-3 text-xs text-slate-400">
                  {question.length}/2000
                </span>
              </div>
              <button
                type="submit"
                disabled={!selectedId || isBusy || !question.trim()}
                className="flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-medium text-white hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:opacity-50 transition-colors"
                aria-label="Send message"
              >
                {loading === 'chat' ? <Spinner /> : 'Send'}
              </button>
            </form>
          </div>

          <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">Compliance Intelligence</h2>
                <p className="text-sm text-slate-500">
                  Obligations, risks, penalties, and recommended actions — grounded in your document.
                </p>
              </div>
              <button
                type="button"
                onClick={handleSummary}
                disabled={!selectedId || isBusy}
                className="flex items-center gap-2 rounded-xl border border-slate-300 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                aria-label="Generate compliance intelligence"
              >
                {loading === 'summary' ? <Spinner /> : 'Analyze Document'}
              </button>
            </div>

            {!summary ? (
              <div className="mt-4 flex flex-col items-center py-8 text-center">
                <OverviewIcon />
                <p className="mt-3 text-sm text-slate-500">
                  Run compliance analysis to extract obligations, risks, and penalties.
                </p>
              </div>
            ) : (
              <div className="mt-4 space-y-4">
                <ComplianceOverviewCard summary={summary} />
                {summary.obligations.length > 0 && (
                  <ComplianceSection title="Obligations" icon={<DocumentIcon />} count={summary.obligations.length}>
                    {summary.obligations.map((item) => (
                      <ObligationCard key={item.id} obligation={item} />
                    ))}
                  </ComplianceSection>
                )}
                {summary.risks.length > 0 && (
                  <ComplianceSection title="Risks" icon={<RiskIcon />} count={summary.risks.length}>
                    {summary.risks.map((item) => (
                      <RiskCard key={item.id} risk={item} />
                    ))}
                  </ComplianceSection>
                )}
                {summary.penalties.length > 0 && (
                  <ComplianceSection title="Penalties" icon={<WarningIcon />} count={summary.penalties.length}>
                    {summary.penalties.map((item) => (
                      <PenaltyCard key={item.id} penalty={item} />
                    ))}
                  </ComplianceSection>
                )}
                {summary.recommended_actions.length > 0 && (
                  <ComplianceSection title="Recommended Actions" icon={<LightbulbIcon />} count={summary.recommended_actions.length}>
                    {summary.recommended_actions.map((item) => (
                      <ActionCard key={item.id} action={item} />
                    ))}
                  </ComplianceSection>
                )}
                {summary.missing_information.length > 0 && (
                  <ComplianceSection title="Missing Information" icon={<WarningIcon />} count={summary.missing_information.length}>
                    <ul className="space-y-2">
                      {summary.missing_information.map((item) => (
                        <li key={item} className="flex gap-2 text-sm text-slate-600">
                          <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                          <span className="leading-relaxed">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </ComplianceSection>
                )}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

function ComplianceOverviewCard({ summary }: { summary: ComplianceSummary }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
        <div className="flex items-center gap-2">
          <span className="text-slate-600"><OverviewIcon /></span>
          <h3 className="font-semibold text-slate-900">Executive Overview</h3>
        </div>
        <RiskLevelBadge level={summary.risk_level} />
      </div>
      <p className="text-sm text-slate-600 leading-relaxed">{summary.overview}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        {summary.document_type && (
          <span className="inline-flex rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800">
            {summary.document_type}
          </span>
        )}
        {summary.regulatory_framework && (
          <span className="inline-flex rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-800">
            {summary.regulatory_framework}
          </span>
        )}
      </div>
      {summary.analysis_notes && (
        <p className="mt-3 text-xs text-slate-500 italic border-t border-slate-200 pt-3">
          {summary.analysis_notes}
        </p>
      )}
    </div>
  )
}

function ComplianceSection({
  title,
  icon,
  count,
  children,
}: {
  title: string
  icon: React.ReactNode
  count: number
  children: React.ReactNode
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-slate-600">{icon}</span>
        <h3 className="font-semibold text-slate-900">{title}</h3>
        <span className="ml-auto rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
          {count}
        </span>
      </div>
      <div className="space-y-3">{children}</div>
    </div>
  )
}

function SourceBadges({ sources }: { sources: SourceReference[] }) {
  if (sources.length === 0) return null
  return (
    <div className="mt-2 flex flex-wrap gap-1.5">
      {sources.map((source) => (
        <span
          key={`${source.page}-${source.chunk}`}
          className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-0.5 text-xs text-slate-600"
          title={source.excerpt ?? undefined}
        >
          <PageIcon />
          p.{source.page}
          {source.section && <span className="text-slate-400">· {source.section}</span>}
        </span>
      ))}
    </div>
  )
}

function RiskLevelBadge({ level }: { level: RiskLevel }) {
  const styles: Record<RiskLevel, string> = {
    critical: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    medium: 'bg-amber-100 text-amber-800',
    low: 'bg-emerald-100 text-emerald-800',
  }
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold uppercase ${styles[level]}`}>
      {level} risk
    </span>
  )
}

function PriorityBadge({ priority }: { priority: Priority }) {
  const styles: Record<Priority, string> = {
    critical: 'bg-red-100 text-red-700',
    high: 'bg-orange-100 text-orange-700',
    medium: 'bg-amber-100 text-amber-700',
    low: 'bg-slate-100 text-slate-600',
  }
  return (
    <span className={`inline-flex rounded px-1.5 py-0.5 text-xs font-medium capitalize ${styles[priority]}`}>
      {priority}
    </span>
  )
}

function SeverityBadge({ severity }: { severity: Severity }) {
  const styles: Record<Severity, string> = {
    critical: 'bg-red-100 text-red-700',
    high: 'bg-orange-100 text-orange-700',
    medium: 'bg-amber-100 text-amber-700',
    low: 'bg-slate-100 text-slate-600',
  }
  return (
    <span className={`inline-flex rounded px-1.5 py-0.5 text-xs font-medium capitalize ${styles[severity]}`}>
      {severity}
    </span>
  )
}

function ObligationCard({ obligation }: { obligation: import('./api').ComplianceObligation }) {
  return (
    <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <span className="text-xs font-mono text-slate-400">{obligation.id}</span>
          <h4 className="font-medium text-slate-900">{obligation.title}</h4>
        </div>
        <PriorityBadge priority={obligation.priority} />
      </div>
      <p className="mt-1 text-sm text-slate-600 leading-relaxed">{obligation.description}</p>
      <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-500">
        {obligation.category && <span>Category: {obligation.category}</span>}
        {obligation.deadline && <span>Deadline: {obligation.deadline}</span>}
      </div>
      <SourceBadges sources={obligation.sources} />
    </div>
  )
}

function RiskCard({ risk }: { risk: import('./api').ComplianceRisk }) {
  return (
    <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <span className="text-xs font-mono text-slate-400">{risk.id}</span>
          <h4 className="font-medium text-slate-900">{risk.title}</h4>
        </div>
        <SeverityBadge severity={risk.severity} />
      </div>
      <p className="mt-1 text-sm text-slate-600 leading-relaxed">{risk.description}</p>
      {risk.likelihood && (
        <p className="mt-1 text-xs text-slate-500">Likelihood: {risk.likelihood}</p>
      )}
      {risk.related_obligation_ids.length > 0 && (
        <p className="mt-1 text-xs text-slate-500">
          Related: {risk.related_obligation_ids.join(', ')}
        </p>
      )}
      <SourceBadges sources={risk.sources} />
    </div>
  )
}

function PenaltyCard({ penalty }: { penalty: import('./api').CompliancePenalty }) {
  return (
    <div className="rounded-lg border border-red-100 bg-red-50/50 p-3">
      <span className="text-xs font-mono text-slate-400">{penalty.id}</span>
      <p className="mt-0.5 text-sm text-slate-700 leading-relaxed">{penalty.description}</p>
      {penalty.amount_or_range && (
        <p className="mt-2 text-sm font-semibold text-red-800">{penalty.amount_or_range}</p>
      )}
      <div className="mt-1 flex flex-wrap gap-2 text-xs text-slate-500">
        {penalty.penalty_type && <span>Type: {penalty.penalty_type}</span>}
        {penalty.trigger && <span>Trigger: {penalty.trigger}</span>}
      </div>
      {penalty.related_obligation_ids.length > 0 && (
        <p className="mt-1 text-xs text-slate-500">
          Related: {penalty.related_obligation_ids.join(', ')}
        </p>
      )}
      <SourceBadges sources={penalty.sources} />
    </div>
  )
}

function ActionCard({ action }: { action: import('./api').RecommendedAction }) {
  return (
    <div className="rounded-lg border border-emerald-100 bg-emerald-50/50 p-3">
      <div className="flex items-start justify-between gap-2">
        <div>
          <span className="text-xs font-mono text-slate-400">{action.id}</span>
          <h4 className="font-medium text-slate-900">{action.title}</h4>
        </div>
        <PriorityBadge priority={action.priority} />
      </div>
      <p className="mt-1 text-sm text-slate-600 leading-relaxed">{action.description}</p>
      <p className="mt-1 text-xs text-slate-500 capitalize">Effort: {action.effort}</p>
      {(action.related_risk_ids.length > 0 || action.related_obligation_ids.length > 0) && (
        <p className="mt-1 text-xs text-slate-500">
          Addresses: {[...action.related_obligation_ids, ...action.related_risk_ids].join(', ')}
        </p>
      )}
    </div>
  )
}

export default App
