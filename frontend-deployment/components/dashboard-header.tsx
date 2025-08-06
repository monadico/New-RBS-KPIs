// components/dashboard-header.tsx
"use client"

import { useState, useEffect } from "react"
import { cn } from "@/lib/utils"
import { useAuth } from "@/components/auth/auth-context"
import { Button } from "@/components/ui/button"
import { LogOut, User, Trophy } from "lucide-react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { LoginModal } from "@/components/auth/login-modal"

type DashboardHeaderProps = {}

export function DashboardHeader() {
  const [activeNav, setActiveNav] = useState("Overview") // State for active navigation item
  const [isVisible, setIsVisible] = useState(true) // State to control header visibility
  const [lastScrollY, setLastScrollY] = useState(0) // State to store last scroll position
  const [showLoginModal, setShowLoginModal] = useState(false) // State for login modal
  const { isAuthenticated, logout, sessionInfo } = useAuth()
  const pathname = usePathname()

  // Effect to handle scroll behavior
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY

      if (currentScrollY > lastScrollY && currentScrollY > 100) {
        // Scrolling down and past an initial threshold
        setIsVisible(false)
      } else if (currentScrollY < lastScrollY) {
        // Scrolling up
        setIsVisible(true)
      }
      // If scrolling down but not past threshold, or at the very top, keep visible.
      // If scrolling down and past threshold, keep hidden until scroll up.

      setLastScrollY(currentScrollY)

      // Scroll spy functionality
      const sections = navItems.map(item => ({
        id: item.href.substring(1),
        label: item.label
      }))

      let currentSection = "Overview"
      for (const section of sections) {
        const element = document.getElementById(section.id)
        if (element) {
          const rect = element.getBoundingClientRect()
          if (rect.top <= 100 && rect.bottom >= 100) {
            currentSection = section.label
            break
          }
        }
      }
      setActiveNav(currentSection)
    }

    window.addEventListener("scroll", handleScroll)

    return () => {
      window.removeEventListener("scroll", handleScroll)
    }
  }, [lastScrollY]) // Re-run effect when lastScrollY changes

  const navItems = [
    { label: "Overview", href: "#overview", isLink: false, icon: undefined },
    { label: "Stats and Retention", href: "#stats-retention", isLink: false, icon: undefined },
    { label: "Heatmaps", href: "#heatmaps", isLink: false, icon: undefined },
  ]

  // Add raffle tab for admin users
  const adminNavItems = isAuthenticated ? [
    ...navItems,
    { label: "Raffle", href: "/raffle", isLink: true, icon: Trophy }
  ] : navItems

  const handleNavClick = (href: string, label: string) => {
    setActiveNav(label)
    const element = document.querySelector(href)
    if (element) {
      element.scrollIntoView({ 
        behavior: 'smooth',
        block: 'start'
      })
    }
  }

  return (
    <>
      <header
        className={cn(
          "sticky top-0 z-20 bg-rbs-washed-black/85 backdrop-blur-xl border-b border-border-subtle shadow-lg transition-transform duration-300 ease-in-out",
          isVisible ? "translate-y-0" : "-translate-y-full", // Apply transform based on visibility
        )}
      >
        <div className="container mx-auto px-6 py-2">
          <div className="flex items-center justify-between">
            {/* Main Navigation */}
            <nav className="flex flex-wrap justify-center gap-x-6 gap-y-2">
              {adminNavItems.map((item) => {
                const isActive = item.isLink 
                  ? pathname === item.href 
                  : activeNav === item.label
                
                const baseClassName = cn(
                  "relative text-sm font-medium py-2 px-3 rounded-lg transition-all duration-300 flex items-center gap-2",
                  "before:absolute before:bottom-0 before:left-1/2 before:-translate-x-1/2 before:w-0 before:h-0.5 before:bg-rbs-lime before:rounded-full before:transition-all before:duration-300",
                  isActive
                    ? "text-text-primary before:w-full before:opacity-100"
                    : "text-text-secondary hover:text-text-primary hover:before:w-2/3 hover:before:opacity-70",
                )
                
                if (item.isLink) {
                  return (
                    <Link
                      key={item.label}
                      href={item.href}
                      className={baseClassName}
                    >
                      {item.icon && <item.icon className="w-4 h-4" />}
                      {item.label}
                    </Link>
                  )
                } else {
                  return (
                    <button
                      key={item.label}
                      onClick={() => handleNavClick(item.href, item.label)}
                      className={baseClassName}
                    >
                      {item.icon && <item.icon className="w-4 h-4" />}
                      {item.label}
                    </button>
                  )
                }
              })}
            </nav>

            {/* Auth Section */}
            {isAuthenticated ? (
              <div className="flex items-center gap-2">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <User className="w-4 h-4" />
                  <span>Admin</span>
                  {sessionInfo && (
                    <span className="text-xs">
                      (expires {new Date(sessionInfo.expiresAt).toLocaleTimeString()})
                    </span>
                  )}
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={logout}
                  className="text-text-secondary hover:text-text-primary"
                >
                  <LogOut className="w-4 h-4" />
                </Button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowLoginModal(true)}
                  className="text-text-secondary hover:text-text-primary border-border-subtle hover:border-rbs-lime"
                >
                  <User className="w-4 h-4 mr-2" />
                  Admin Login
                </Button>
              </div>
            )}
          </div>
        </div>
      </header>
      
      {/* Login Modal */}
      <LoginModal 
        isOpen={showLoginModal} 
        onClose={() => setShowLoginModal(false)} 
             />
     </>
   )
 }
