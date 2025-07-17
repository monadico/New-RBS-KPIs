import { Home, Calendar, MessageCircle, HelpCircle, Settings, Upload } from "lucide-react"
import { cn } from "../lib/utils"
import type React from "react" // Added import for React

interface NavItemProps {
  icon: React.ReactNode
  label: string
  active?: boolean
}

function NavItem({ icon, label, active }: NavItemProps) {
  return (
    <div
      className={cn(
        "flex items-center gap-3 px-4 py-2 rounded-lg cursor-pointer",
        active ? "bg-[#6d08c3] text-white" : "text-gray-400 hover:bg-[#191919] hover:text-white",
      )}
    >
      {icon}
      <span className="text-sm font-medium">{label}</span>
    </div>
  )
}

export function SidebarNav() {
  return (
    <div className="w-[240px] bg-[#121212] h-screen p-4 flex flex-col">
      <div className="flex items-center gap-2 px-4 py-2">
        <div className="w-8 h-8 bg-[#6d08c3] rounded-lg" />
        <span className="text-white font-bold">KO</span>
      </div>
      <nav className="mt-8 space-y-2">
        <NavItem icon={<Home size={20} />} label="Home" active />
        <NavItem icon={<Calendar size={20} />} label="My events" />
        <NavItem icon={<MessageCircle size={20} />} label="Chat" />
      </nav>
      <div className="mt-auto space-y-2">
        <NavItem icon={<HelpCircle size={20} />} label="Help" />
        <NavItem icon={<Settings size={20} />} label="Settings" />
        <NavItem icon={<Upload size={20} />} label="Upgrade" />
      </div>
    </div>
  )
}
