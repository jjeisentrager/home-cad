interface Props {
  width: number
  height: number
  hasCycleError?: boolean
}

export default function SelectionBox({ width, height, hasCycleError }: Props) {
  return (
    <>
      <rect
        x={-3}
        y={-3}
        width={width + 6}
        height={height + 6}
        fill="none"
        stroke={hasCycleError ? '#ff4444' : '#4a9eff'}
        strokeWidth={1.5}
        strokeDasharray="4 3"
        pointerEvents="none"
      />
      {hasCycleError && (
        <text x={width / 2} y={-8} textAnchor="middle" fill="#ff4444" fontSize={10}>
          cycle!
        </text>
      )}
    </>
  )
}
