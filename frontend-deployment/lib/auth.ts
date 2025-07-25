// lib/auth.ts
import { createHash } from 'crypto'

// Rate limiting
interface LoginAttempt {
  timestamp: number
  count: number
}

const loginAttempts = new Map<string, LoginAttempt>()
const MAX_ATTEMPTS = 5
const LOCKOUT_DURATION = 15 * 60 * 1000 // 15 minutes
const SESSION_DURATION = 24 * 60 * 60 * 1000 // 24 hours

// Get credentials from environment variables ONLY
const getCredentials = () => {
  const username = process.env.NEXT_PUBLIC_AUTH_USERNAME
  const passwordHash = process.env.NEXT_PUBLIC_AUTH_PASSWORD_HASH
  return { username, passwordHash }
}

// Hash password for comparison
export const hashPassword = (password: string): string => {
  return createHash('sha256').update(password).digest('hex')
}

// Check rate limiting
export const checkRateLimit = (ip: string): { allowed: boolean; remainingTime?: number } => {
  const now = Date.now()
  const attempt = loginAttempts.get(ip)
  
  if (!attempt) {
    return { allowed: true }
  }
  
  // Check if lockout period has expired
  if (now - attempt.timestamp > LOCKOUT_DURATION) {
    loginAttempts.delete(ip)
    return { allowed: true }
  }
  
  // Check if max attempts exceeded
  if (attempt.count >= MAX_ATTEMPTS) {
    const remainingTime = LOCKOUT_DURATION - (now - attempt.timestamp)
    return { allowed: false, remainingTime }
  }
  
  return { allowed: true }
}

// Record login attempt
export const recordLoginAttempt = (ip: string, success: boolean) => {
  const now = Date.now()
  const attempt = loginAttempts.get(ip)
  
  if (success) {
    // Reset on successful login
    loginAttempts.delete(ip)
    return
  }
  
  if (!attempt) {
    loginAttempts.set(ip, { timestamp: now, count: 1 })
  } else {
    attempt.count += 1
    attempt.timestamp = now
  }
}

// Validate credentials
export const validateCredentials = (username: string, password: string): boolean => {
  const { username: validUsername, passwordHash: validPasswordHash } = getCredentials()
  if (!validUsername || !validPasswordHash) return false
  const hashedPassword = hashPassword(password)
  
  return username === validUsername && hashedPassword === validPasswordHash
}

// Check if session is still valid
export const isSessionValid = (): boolean => {
  const sessionData = localStorage.getItem('rbs-session')
  if (!sessionData) return false
  
  try {
    const session = JSON.parse(sessionData)
    const now = Date.now()
    
    return session.expiresAt > now
  } catch {
    return false
  }
}

// Create session
export const createSession = () => {
  const expiresAt = Date.now() + SESSION_DURATION
  const session = {
    authenticated: true,
    expiresAt,
    createdAt: Date.now()
  }
  
  localStorage.setItem('rbs-session', JSON.stringify(session))
  localStorage.setItem('rbs-auth', 'true')
}

// Clear session
export const clearSession = () => {
  localStorage.removeItem('rbs-session')
  localStorage.removeItem('rbs-auth')
}

// Get session info
export const getSessionInfo = () => {
  const sessionData = localStorage.getItem('rbs-session')
  if (!sessionData) return null
  
  try {
    return JSON.parse(sessionData)
  } catch {
    return null
  }
} 