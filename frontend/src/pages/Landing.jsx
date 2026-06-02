import { Link } from 'react-router-dom'
import { Activity, FileText, Brain, TrendingUp, Shield, ChevronRight, CheckCircle } from 'lucide-react'
import Navbar from '../components/Navbar'

const features = [
  { icon: FileText, title: 'Smart PDF Parsing',    desc: 'Upload any lab report PDF. Our OCR engine extracts all biomarker values automatically — no manual entry needed.' },
  { icon: Brain,    title: 'AI Risk Analysis',     desc: 'Trained ML models assess liver and kidney disease risk. Rule-based diabetes detection using WHO clinical thresholds.' },
  { icon: TrendingUp, title: 'Trend Tracking',    desc: 'Upload multiple reports over time. MediScan tracks your biomarker trends and alerts you before values become dangerous.' },
]

const steps = [
  { step: '01', title: 'Create your account',    desc: 'Sign up with your name, age, and gender. Your profile personalises every analysis.' },
  { step: '02', title: 'Upload your lab report', desc: 'Upload any blood test PDF — SRL, Dr Lal, Metropolis, Apollo, or any other lab format.' },
  { step: '03', title: 'Get your analysis',      desc: 'Instantly see your results explained in plain language with risk flags and lifestyle recommendations.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar />

      <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-20 pb-24 text-center">
        <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
          <Activity className="w-4 h-4" />
          AI-powered medical report analysis
        </div>
        <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 leading-tight mb-6">
          Understand Your<br />
          <span className="text-blue-600">Lab Reports</span> Instantly
        </h1>
        <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-10">
          Upload any blood test PDF and get a plain-language explanation of your results, 
          risk assessments, and personalised health insights — in seconds.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link to="/signup" className="btn-primary flex items-center gap-2 text-base py-3 px-8">
            Analyse My Report Free
            <ChevronRight className="w-4 h-4" />
          </Link>
          <Link to="/login" className="btn-secondary text-base py-3 px-8">
            Sign In
          </Link>
        </div>
        <div className="flex items-center justify-center gap-6 mt-8 text-sm text-gray-400">
          {['No credit card needed', 'Results in seconds', '100% private & secure'].map(t => (
            <div key={t} className="flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4 text-green-500" />
              {t}
            </div>
          ))}
        </div>
      </section>

      <section className="bg-gray-50 py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Everything you need to understand your health</h2>
            <p className="text-gray-500 max-w-xl mx-auto">MediScan combines OCR, machine learning, and AI to give you the most comprehensive lab report analysis available.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map(({ icon: Icon, title, desc }) => (
              <div key={title} className="card hover:shadow-md transition-shadow">
                <div className="w-11 h-11 bg-blue-50 rounded-xl flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20">
        <div className="max-w-6xl mx-auto px-4 sm:px-6">
          <div className="text-center mb-14">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">How it works</h2>
            <p className="text-gray-500">Three simple steps to understand your health</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {steps.map(({ step, title, desc }) => (
              <div key={step} className="text-center">
                <div className="w-14 h-14 bg-blue-600 text-white rounded-2xl flex items-center justify-center text-xl font-bold mx-auto mb-4">{step}</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
                <p className="text-gray-500 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-blue-600 py-20">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to understand your lab reports?</h2>
          <p className="text-blue-100 mb-8">Join thousands of people who use MediScan to take charge of their health.</p>
          <Link to="/signup" className="inline-flex items-center gap-2 bg-white text-blue-600 font-semibold px-8 py-3 rounded-lg hover:bg-blue-50 transition-colors">
            Get Started Free <ChevronRight className="w-4 h-4" />
          </Link>
        </div>
      </section>

      <footer className="border-t border-gray-100 py-8">
        <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-blue-600 rounded flex items-center justify-center">
              <Activity className="w-4 h-4 text-white" />
            </div>
            <span className="text-sm font-medium text-gray-700">MediScan</span>
          </div>
          <p className="text-xs text-gray-400">MediScan is for awareness only. Always consult a qualified doctor for medical advice.</p>
          <div className="flex items-center gap-1.5 text-xs text-gray-400">
            <Shield className="w-3.5 h-3.5" />
            Your data is private and secure
          </div>
        </div>
      </footer>
    </div>
  )
}