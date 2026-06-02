import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import API from '../api/client'
import { Upload as UploadIcon, FileText, X, CheckCircle, AlertCircle, Loader } from 'lucide-react'

export default function Upload() {
  const navigate              = useNavigate()
  const inputRef              = useRef(null)
  const [file, setFile]       = useState(null)
  const [dragging, setDrag]   = useState(false)
  const [status, setStatus]   = useState('idle')  
  const [error, setError]     = useState('')

  const accept = (f) => {
    if (!f) return
    if (f.type !== 'application/pdf') {
      setError('Only PDF files are supported. Please upload a PDF lab report.')
      return
    }
    if (f.size > 10 * 1024 * 1024) {
      setError('File size must be under 10MB.')
      return
    }
    setError('')
    setFile(f)
  }

  const onDrop = (e) => {
    e.preventDefault()
    setDrag(false)
    accept(e.dataTransfer.files[0])
  }

  const submit = async () => {
    if (!file) return
    setStatus('uploading')
    setError('')

    const form = new FormData()
    form.append('file', file)

    try {
      const res = await API.post('/reports/analyse', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 120000  
      })
      setStatus('success')
      setTimeout(() => {
        navigate(`/report/${res.data.report_id}`, { state: { result: res.data } })
      }, 800)
    } catch (err) {
      setStatus('error')
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-12">
        <div className="text-center mb-10">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Upload Your Lab Report</h1>
          <p className="text-gray-500 text-sm">
            Upload any blood test PDF — CBC, LFT, KFT, Lipid Profile, Thyroid, or comprehensive panels.
          </p>
        </div>

        <div className="card">
          <div
            onDragOver={(e) => { e.preventDefault(); setDrag(true) }}
            onDragLeave={() => setDrag(false)}
            onDrop={onDrop}
            onClick={() => !file && inputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl transition-all cursor-pointer
              ${dragging         ? 'border-blue-500 bg-blue-50'
              : file            ? 'border-green-300 bg-green-50 cursor-default'
              : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'}
              p-10 text-center`}
          >
            <input ref={inputRef} type="file" accept=".pdf" className="hidden"
              onChange={(e) => accept(e.target.files[0])} />

            {file ? (
              <div>
                <div className="w-14 h-14 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <FileText className="w-7 h-7 text-green-600" />
                </div>
                <p className="text-gray-900 font-medium">{file.name}</p>
                <p className="text-gray-400 text-sm mt-1">{(file.size / 1024).toFixed(1)} KB</p>
                <button
                  onClick={(e) => { e.stopPropagation(); setFile(null); setStatus('idle'); setError('') }}
                  className="mt-3 inline-flex items-center gap-1 text-xs text-red-500 hover:text-red-700"
                >
                  <X className="w-3 h-3" /> Remove file
                </button>
              </div>
            ) : (
              <div>
                <div className="w-14 h-14 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <UploadIcon className="w-7 h-7 text-blue-500" />
                </div>
                <p className="text-gray-700 font-medium">Drop your PDF here</p>
                <p className="text-gray-400 text-sm mt-1">or click to browse</p>
                <p className="text-gray-300 text-xs mt-3">PDF only · Max 10MB</p>
              </div>
            )}
          </div>

          {error && (
            <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg mt-4">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              {error}
            </div>
          )}

          {status === 'uploading' && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-3 text-blue-700">
                <Loader className="w-4 h-4 animate-spin" />
                <div>
                  <div className="text-sm font-medium">Analysing your report...</div>
                  <div className="text-xs text-blue-500 mt-0.5">Extracting biomarkers, running risk models, generating AI analysis. This may take 20–40 seconds.</div>
                </div>
              </div>
              <div className="mt-3 bg-blue-200 rounded-full h-1.5 overflow-hidden">
                <div className="bg-blue-600 h-1.5 rounded-full w-2/3 animate-pulse" />
              </div>
            </div>
          )}

          {status === 'success' && (
            <div className="flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 text-sm px-4 py-3 rounded-lg mt-4">
              <CheckCircle className="w-4 h-4" />
              Analysis complete! Redirecting to your report...
            </div>
          )}

          <button
            onClick={submit}
            disabled={!file || status === 'uploading' || status === 'success'}
            className="btn-primary w-full mt-6 flex items-center justify-center gap-2"
          >
            {status === 'uploading'
              ? <><Loader className="w-4 h-4 animate-spin" /> Analysing...</>
              : status === 'success'
              ? <><CheckCircle className="w-4 h-4" /> Done!</>
              : <><UploadIcon className="w-4 h-4" /> Analyse Report</>
            }
          </button>

          <p className="text-center text-xs text-gray-400 mt-4">
            🔒 Your report is processed securely. We never share your health data.
          </p>
        </div>

        <div className="mt-6 card">
          <p className="text-xs font-semibold text-gray-500 mb-3">SUPPORTED REPORT TYPES</p>
          <div className="flex flex-wrap gap-2">
            {['Complete Blood Count (CBC)', 'Liver Function Test (LFT)', 'Kidney Function Test (KFT)',
              'Lipid Profile', 'Thyroid Panel (TSH, T3, T4)', 'Blood Sugar / HbA1c',
              'Vitamin D & B12', 'Comprehensive Health Panel'].map(t => (
              <span key={t} className="text-xs bg-gray-50 border border-gray-200 text-gray-600 px-2.5 py-1 rounded-full">{t}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}