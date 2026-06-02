import { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import API from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser]       = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem('mediscan_user')
    const token  = localStorage.getItem('mediscan_token')
    if (stored && token) {
      setUser(JSON.parse(stored))
    }
    setLoading(false)
  }, [])

  const signup = async (data) => {
    const res = await API.post('/auth/signup', data)
    localStorage.setItem('mediscan_token', res.data.access_token)
    localStorage.setItem('mediscan_user',  JSON.stringify(res.data.user))
    setUser(res.data.user)
    return res.data
  }

  const login = async (data) => {
    const res = await API.post('/auth/login', data)
    localStorage.setItem('mediscan_token', res.data.access_token)
    localStorage.setItem('mediscan_user',  JSON.stringify(res.data.user))
    setUser(res.data.user)
    return res.data
  }

  const logout = () => {
    localStorage.removeItem('mediscan_token')
    localStorage.removeItem('mediscan_user')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, signup, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)