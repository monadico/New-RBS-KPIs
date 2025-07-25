"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Lock, Eye } from "lucide-react"
import { useAuth } from "./auth-context"
import { LoginModal } from "./login-modal"

interface ProtectedComponentProps {
  children: React.ReactNode
  title?: string
  description?: string
}

export function ProtectedComponent({ children, title = "Private Content", description = "Login required to view this content" }: ProtectedComponentProps) {
  const { isAuthenticated } = useAuth()
  const [showLoginModal, setShowLoginModal] = useState(false)

  if (isAuthenticated) {
    return <>{children}</>
  }

  return (
    <>
      <div className="relative group">
        {/* Blurred content */}
        <div className="blur-sm pointer-events-none">
          {children}
        </div>
        
        {/* Overlay with login prompt */}
        <div className="absolute inset-0 flex items-center justify-center bg-black/20 rounded-lg">
          <div className="text-center p-6 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg border border-gray-200">
            <div className="flex items-center justify-center mb-3">
              <div className="p-2 bg-blue-500/10 rounded-lg border border-blue-500/20">
                <Lock className="w-5 h-5 text-blue-400" />
              </div>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              {title}
            </h3>
            <p className="text-gray-600 mb-4 text-sm">
              {description}
            </p>
            <Button
              onClick={() => setShowLoginModal(true)}
              className="bg-blue-500 hover:bg-blue-600 text-white"
            >
              <Eye className="w-4 h-4 mr-2" />
              Login to View
            </Button>
          </div>
        </div>
      </div>

      <LoginModal 
        isOpen={showLoginModal} 
        onClose={() => setShowLoginModal(false)} 
      />
    </>
  )
} 