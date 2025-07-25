"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { 
  validateCredentials, 
  createSession, 
  clearSession, 
  isSessionValid,
  checkRateLimit,
  recordLoginAttempt
} from "@/lib/auth"

interface AuthContextType {
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<{ success: boolean; error?: string }>
  logout: () => void
  sessionInfo: any
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [sessionInfo, setSessionInfo] = useState(null)

  // Check session validity on mount
  useEffect(() => {
    if (isSessionValid()) {
      setIsAuthenticated(true)
      const session = JSON.parse(localStorage.getItem('rbs-session') || '{}')
      setSessionInfo(session)
    } else {
      // Clear invalid session
      clearSession()
    }
  }, [])

  const login = async (username: string, password: string): Promise<{ success: boolean; error?: string }> => {
    // Simple IP-based rate limiting (in production, use real IP)
    const clientId = 'default' // In production, get real client IP
    const rateLimit = checkRateLimit(clientId)
    
    if (!rateLimit.allowed) {
      const minutes = Math.ceil((rateLimit.remainingTime || 0) / 60000)
      return { 
        success: false, 
        error: `Too many login attempts. Please try again in ${minutes} minutes.` 
      }
    }

    const isValid = validateCredentials(username, password)
    
    if (isValid) {
      createSession()
      setIsAuthenticated(true)
      const session = JSON.parse(localStorage.getItem('rbs-session') || '{}')
      setSessionInfo(session)
      recordLoginAttempt(clientId, true)
      return { success: true }
    } else {
      recordLoginAttempt(clientId, false)
      return { 
        success: false, 
        error: 'Invalid username or password' 
      }
    }
  }

  const logout = () => {
    clearSession()
    setIsAuthenticated(false)
    setSessionInfo(null)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout, sessionInfo }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 