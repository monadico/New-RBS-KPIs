import { Instagram } from "lucide-react"
import { Button } from "@/components/ui/button"

export function ProfileSection() {
  return (
    <div className="bg-[#191919] rounded-lg p-6">
      <div className="flex items-start gap-4">
        <div className="relative">
          <img
            src="/placeholder.svg?height=120&width=120"
            alt="Profile"
            className="w-[120px] h-[120px] rounded-lg object-cover"
          />
          <div className="absolute bottom-0 right-0 w-6 h-6 bg-green-500 rounded-full border-2 border-[#191919]" />
        </div>
        <div className="flex-1">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-white">Alex</h1>
            <Button variant="outline" size="sm">
              Add social link
            </Button>
          </div>
          <p className="mt-2 text-gray-400 text-sm">
            Hey! I'm Jacob, aka GamerLegend42. Passionate about everything gaming, from retro classics to the latest
            eSports. When not gaming, I'm probably streaming or exploring new tech. Join me for epic gaming adventures!
          </p>
          <div className="mt-4 flex items-center gap-2">
            <Instagram className="w-5 h-5 text-gray-400" />
            <span className="text-sm text-gray-400">@Username</span>
          </div>
        </div>
      </div>
    </div>
  )
}
