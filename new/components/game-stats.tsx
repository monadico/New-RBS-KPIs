interface StatCardProps {
  value: number
  label: string
  color: string
}

function StatCard({ value, label, color }: StatCardProps) {
  return (
    <div className="bg-[#191919] rounded-lg p-4 flex flex-col items-center">
      <div className="relative w-24 h-24">
        <svg className="w-full h-full" viewBox="0 0 36 36">
          <path
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
            fill="none"
            stroke={color}
            strokeWidth="2"
            strokeDasharray={`${value}, 100`}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-2xl font-bold text-white">{value}</span>
        </div>
      </div>
      <span className="mt-2 text-sm text-gray-400">{label}</span>
    </div>
  )
}

export function GameStats() {
  return (
    <div className="grid grid-cols-5 gap-4">
      <StatCard value={152} label="Played Games" color="#4ba8eb" />
      <StatCard value={29} label="Organised" color="#6d08c3" />
      <StatCard value={77} label="Challenged" color="#233dff" />
      <StatCard value={77} label="Games Lost" color="#af0707" />
      <StatCard value={29} label="Games Won" color="#51af07" />
    </div>
  )
}
