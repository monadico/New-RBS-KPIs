import { Button } from "@/components/ui/button"

interface BeltProps {
  type: "Bronze" | "Silver" | "Gold" | "Platinum"
  credit: number
  count: number
}

function Belt({ type, credit, count }: BeltProps) {
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="w-16 h-16 rounded-full bg-[#191919] flex items-center justify-center">
        <img src={`/placeholder.svg?height=40&width=40`} alt={`${type} belt`} />
      </div>
      <div className="text-center">
        <div className="text-gray-400 text-sm">Credit: {credit}</div>
        <div className="text-white font-bold">{count}</div>
      </div>
      <Button variant="outline" size="sm" className="w-full">
        Convert
      </Button>
    </div>
  )
}

export function BeltSystem() {
  return (
    <div className="bg-[#191919] rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-white">My Belts</h2>
        <Button variant="outline" size="sm">
          View transaction history
        </Button>
      </div>
      <div className="grid grid-cols-4 gap-4">
        <Belt type="Bronze" credit={400} count={2} />
        <Belt type="Silver" credit={400} count={1} />
        <Belt type="Gold" credit={0} count={0} />
        <Belt type="Platinum" credit={0} count={0} />
      </div>
    </div>
  )
}
