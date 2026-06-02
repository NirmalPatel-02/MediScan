import { useState, useEffect } from 'react'
import { useParams, useLocation, Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import API from '../api/client'
import { ArrowLeft, AlertTriangle, CheckCircle, TrendingUp, TrendingDown, Minus, Brain, Activity } from 'lucide-react'

function HealthGauge({ score }) {
  const r          = 54
  const circ       = 2 * Math.PI * r
  const progress   = ((100 - score) / 100) * circ
  const color      = score >= 75 ? '#16a34a' : score >= 50 ? '#d97706' : '#dc2626'
  const label      = score >= 75 ? 'Good' : score >= 50 ? 'Fair' : 'Needs Attention'

  return (
    <div className="flex flex-col items-center">
      <svg width="140" height="140" className="-rotate-90">
        <circle cx="70" cy="70" r={r} fill="none" stroke="#f1f5f9" strokeWidth="10" />
        <circle cx="70" cy="70" r={r} fill="none" stroke={color} strokeWidth="10"
          strokeDasharray={circ} strokeDashoffset={progress}
          strokeLinecap="round" style={{ transition: 'stroke-dashoffset 1s ease' }} />
      </svg>
      <div className="-mt-20 text-center">
        <div className="text-4xl font-bold" style={{ color }}>{score}</div>
        <div className="text-xs text-gray-500 mt-1">{label}</div>
      </div>
      <div className="mt-6 text-sm font-medium text-gray-600">Health Score</div>
    </div>
  )
}

function BiomarkerCard({ name, data }) {
  const status = data.status || 'UNKNOWN'

  const styles = {
    NORMAL:   { border: 'border-green-200',  bg: 'bg-green-50',   badge: 'bg-green-100 text-green-700',   icon: <CheckCircle className="w-4 h-4 text-green-500" /> },
    HIGH:     { border: 'border-amber-200',  bg: 'bg-amber-50',   badge: 'bg-amber-100 text-amber-700',   icon: <TrendingUp className="w-4 h-4 text-amber-500" /> },
    LOW:      { border: 'border-blue-200',   bg: 'bg-blue-50',    badge: 'bg-blue-100 text-blue-700',     icon: <TrendingDown className="w-4 h-4 text-blue-500" /> },
    CRITICAL: { border: 'border-red-300',    bg: 'bg-red-50',     badge: 'bg-red-100 text-red-700',       icon: <AlertTriangle className="w-4 h-4 text-red-500" /> },
    UNKNOWN:  { border: 'border-gray-200',   bg: 'bg-gray-50',    badge: 'bg-gray-100 text-gray-600',     icon: <Minus className="w-4 h-4 text-gray-400" /> },
  }[status] || { border: 'border-gray-200', bg: 'bg-gray-50', badge: 'bg-gray-100 text-gray-600', icon: <Minus className="w-4 h-4 text-gray-400" /> }

  const displayName = name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

  return (
    <div className={`border rounded-xl p-4 ${styles.border} ${styles.bg}`}>
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-1.5">
          {styles.icon}
          <span className="text-sm font-medium text-gray-900">{displayName}</span>
        </div>
        <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${styles.badge}`}>{status}</span>
      </div>
      <div className="text-2xl font-bold text-gray-900 mt-1">
        {data.value}
        <span className="text-sm font-normal text-gray-400 ml-1">{data.unit !== 'unknown' ? data.unit : ''}</span>
      </div>
      {data.ref_min !== undefined && (
        <div className="text-xs text-gray-400 mt-1">
          Normal: {data.ref_min} – {data.ref_max}
        </div>
      )}
    </div>
  )
}

function PredictionCard({ type, data }) {
  const titles = { liver: 'Liver Disease Risk', kidney: 'Kidney Disease Risk', diabetes: 'Diabetes Check' }
  const title  = titles[type] || type

  if (!data.ran) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-xl p-4">
        <div className="text-sm font-medium text-gray-700 mb-1">{title}</div>
        <div className="text-xs text-gray-400">{data.reason}</div>
      </div>
    )
  }

  if (type === 'diabetes') {
    const status = data.hba1c_status || data.glucose_status || 'NORMAL'
    const color  = status === 'NORMAL' ? 'text-green-600 bg-green-50 border-green-200'
                 : status === 'PRE_DIABETIC' ? 'text-amber-600 bg-amber-50 border-amber-200'
                 : 'text-red-600 bg-red-50 border-red-200'
    return (
      <div className={`border rounded-xl p-4 ${color}`}>
        <div className="text-sm font-semibold mb-1">{title}</div>
        {data.hba1c         && <div className="text-xs">HbA1c: {data.hba1c}% — {data.hba1c_status?.replace('_', ' ')}</div>}
        {data.fasting_glucose && <div className="text-xs">Fasting Glucose: {data.fasting_glucose} mg/dL — {data.glucose_status?.replace('_', ' ')}</div>}
      </div>
    )
  }

  const color = data.risk_level === 'LOW'      ? 'text-green-600 bg-green-50 border-green-200'
              : data.risk_level === 'MODERATE'  ? 'text-amber-600 bg-amber-50 border-amber-200'
              : 'text-red-600 bg-red-50 border-red-200'

  return (
    <div className={`border rounded-xl p-4 ${color}`}>
      <div className="flex items-center justify-between mb-1">
        <div className="text-sm font-semibold">{title}</div>
        <div className="text-2xl font-bold">{data.risk_pct}</div>
      </div>
      <div className="text-xs font-medium">{data.risk_level} RISK</div>
    </div>
  )
}

export default function Report() {
  const { id }                = useParams()
  const location              = useLocation()
  const [data, setData]       = useState(location.state?.result || null)
  const [loading, setLoading] = useState(!data)
  const [error, setError]     = useState('')

  useEffect(() => {
    if (!data) {
      API.get(`/reports/${id}`)
        .then(r => {
          const raw = r.data
          const biomarkers = {}
          raw.biomarkers?.forEach(b => {
            biomarkers[b.name] = {
              value: b.value, unit: b.unit, status: b.status,
              ref_min: b.ref_min, ref_max: b.ref_max
            }
          })
          const predictions = {}
          raw.predictions?.forEach(p => {
            predictions[p.model] = {
              ran: p.ran, probability: p.probability,
              risk_level: p.risk_level, risk_pct: p.risk_pct, reason: p.reason
            }
          })
          setData({
            report_id:     raw.report_id,
            health_score:  raw.health_score,
            biomarkers,
            predictions,
            analysis:      raw.analysis,
            biomarkers_found: raw.biomarkers?.length || 0
          })
        })
        .catch(() => setError('Report not found.'))
        .finally(() => setLoading(false))
    }
  }, [id])

  if (loading) return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="flex justify-center items-center py-32">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    </div>
  )

  if (error) return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-3xl mx-auto px-4 py-16 text-center">
        <p className="text-red-600 mb-4">{error}</p>
        <Link to="/dashboard" className="btn-primary">Back to Dashboard</Link>
      </div>
    </div>
  )

  const biomarkers  = data?.biomarkers  || {}
  const predictions = data?.predictions || {}

  const criticals = Object.entries(biomarkers).filter(([, d]) => d.status === 'CRITICAL').length
  const abnormals = Object.entries(biomarkers).filter(([, d]) => ['HIGH', 'LOW'].includes(d.status)).length

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-5xl mx-auto px-4 sm:px-6 py-10">

        <Link to="/dashboard" className="inline-flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-900 mb-6 transition-colors">
          <ArrowLeft className="w-4 h-4" /> Back to Dashboard
        </Link>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

          <div className="card flex flex-col items-center justify-center py-8">
            <HealthGauge score={data.health_score || 0} />
          </div>

          <div className="md:col-span-2 grid grid-cols-3 gap-4">
            <div className="card text-center">
              <div className="text-3xl font-bold text-gray-900">{data.biomarkers_found}</div>
              <div className="text-xs text-gray-400 mt-1">Biomarkers Found</div>
            </div>
            <div className={`card text-center ${criticals > 0 ? 'border-red-200 bg-red-50' : ''}`}>
              <div className={`text-3xl font-bold ${criticals > 0 ? 'text-red-600' : 'text-gray-900'}`}>{criticals}</div>
              <div className="text-xs text-gray-400 mt-1">Critical Values</div>
            </div>
            <div className={`card text-center ${abnormals > 0 ? 'border-amber-200 bg-amber-50' : ''}`}>
              <div className={`text-3xl font-bold ${abnormals > 0 ? 'text-amber-600' : 'text-gray-900'}`}>{abnormals}</div>
              <div className="text-xs text-gray-400 mt-1">Abnormal Values</div>
            </div>

            <div className="col-span-3 grid grid-cols-3 gap-3">
              {Object.entries(predictions).map(([type, pred]) => (
                <PredictionCard key={type} type={type} data={pred} />
              ))}
            </div>
          </div>
        </div>

        {Object.keys(biomarkers).length > 0 && (
          <div className="card mb-6">
            <div className="flex items-center gap-2 mb-5">
              <Activity className="w-5 h-5 text-gray-400" />
              <h2 className="text-base font-semibold text-gray-900">Biomarker Results</h2>
              <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full ml-auto">
                {Object.keys(biomarkers).length} values
              </span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {Object.entries(biomarkers)
                .sort((a, b) => {
                  const order = { CRITICAL: 0, HIGH: 1, LOW: 2, NORMAL: 3, UNKNOWN: 4 }
                  return (order[a[1].status] ?? 5) - (order[b[1].status] ?? 5)
                })
                .map(([name, d]) => (
                  <BiomarkerCard key={name} name={name} data={d} />
                ))}
            </div>
          </div>
        )}

        {data.analysis && (
          <div className="card">
            <div className="flex items-center gap-2 mb-5">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Brain className="w-4 h-4 text-white" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-gray-900">AI Health Analysis</h2>
                <p className="text-xs text-gray-400">Generated by MediScan AI · For awareness only</p>
              </div>
            </div>
            <div className="bg-gray-50 rounded-xl p-5 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap border border-gray-100">
              {data.analysis}
            </div>
            <div className="flex items-start gap-2 mt-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0 mt-0.5" />
              <p className="text-xs text-amber-700">
                <strong>Medical Disclaimer:</strong> MediScan is an AI awareness tool and is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified doctor.
              </p>
            </div>
          </div>
        )}

        <div className="text-center mt-8">
          <Link to="/upload" className="btn-secondary inline-flex items-center gap-2">
            Upload Another Report
          </Link>
        </div>
      </div>
    </div>
  )
}