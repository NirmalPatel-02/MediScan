import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Navbar from '../components/Navbar'
import API from '../api/client'
import { Upload, FileText, Clock, TrendingUp, AlertCircle, ChevronRight } from 'lucide-react'

function ScoreBadge({ score }) {
  const color = score >= 75 ? 'text-green-600 bg-green-50 border-green-200'
              : score >= 50 ? 'text-amber-600 bg-amber-50 border-amber-200'
              : 'text-red-600 bg-red-50 border-red-200'
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${color}`}>
      Score: {score}
    </span>
  )
}

export default function Dashboard() {
  const { user }              = useAuth()
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState('')

  useEffect(() => {
    API.get('/reports/history')
      .then(r => setReports(r.data.reports || []))
      .catch(() => setError('Failed to load reports.'))
      .finally(() => setLoading(false))
  }, [])

  const formatDate = (str) => new Date(str).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric'
  })

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user?.name?.split(' ')[0]} 👋
            </h1>
            <p className="text-gray-500 text-sm mt-1">
              {reports.length > 0
                ? `You have ${reports.length} report${reports.length > 1 ? 's' : ''} analysed so far.`
                : 'Upload your first lab report to get started.'}
            </p>
          </div>
          <Link to="/upload" className="btn-primary flex items-center gap-2 self-start sm:self-auto">
            <Upload className="w-4 h-4" />
            Upload Report
          </Link>
        </div>

        {reports.length > 0 && (
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mb-8">
            <div className="card text-center">
              <div className="text-3xl font-bold text-blue-600">{reports.length}</div>
              <div className="text-sm text-gray-500 mt-1">Reports Analysed</div>
            </div>
            <div className="card text-center">
              <div className="text-3xl font-bold text-gray-900">
                {reports[0]?.health_score ?? '—'}
              </div>
              <div className="text-sm text-gray-500 mt-1">Latest Health Score</div>
            </div>
            <div className="card text-center col-span-2 sm:col-span-1">
              <div className="text-3xl font-bold text-gray-900">
                {reports[0]?.biomarkers_found ?? '—'}
              </div>
              <div className="text-sm text-gray-500 mt-1">Biomarkers Last Report</div>
            </div>
          </div>
        )}

        <div className="card">
          <div className="flex items-center gap-2 mb-5">
            <FileText className="w-5 h-5 text-gray-400" />
            <h2 className="text-base font-semibold text-gray-900">Report History</h2>
          </div>

          {loading && (
            <div className="flex justify-center py-12">
              <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {error && (
            <div className="flex items-center gap-2 text-red-600 text-sm py-4">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          )}

          {!loading && !error && reports.length === 0 && (
            <div className="text-center py-16">
              <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <TrendingUp className="w-8 h-8 text-blue-400" />
              </div>
              <h3 className="text-gray-700 font-medium mb-1">No reports yet</h3>
              <p className="text-gray-400 text-sm mb-6">Upload your first lab report to see your analysis here.</p>
              <Link to="/upload" className="btn-primary inline-flex items-center gap-2">
                <Upload className="w-4 h-4" />
                Upload Your First Report
              </Link>
            </div>
          )}

          {!loading && reports.length > 0 && (
            <div className="space-y-3">
              {reports.map((r) => (
                <Link
                  key={r.report_id}
                  to={`/report/${r.report_id}`}
                  className="flex items-center justify-between p-4 bg-gray-50 hover:bg-blue-50 rounded-xl border border-gray-100 hover:border-blue-200 transition-all group"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 bg-white border border-gray-200 rounded-xl flex items-center justify-center group-hover:border-blue-200">
                      <FileText className="w-5 h-5 text-gray-400 group-hover:text-blue-500" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-gray-900">
                        Lab Report — {formatDate(r.uploaded_at)}
                      </div>
                      <div className="text-xs text-gray-400 mt-0.5 flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {r.biomarkers_found} biomarkers found
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    {r.health_score !== null && <ScoreBadge score={r.health_score} />}
                    <ChevronRight className="w-4 h-4 text-gray-300 group-hover:text-blue-500 transition-colors" />
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}