export function Mark({ small = false }: { small?: boolean }) {
  return <svg className={small ? 'mark small' : 'mark'} viewBox="0 0 48 48" fill="none" aria-hidden="true">
    {[0, 60, 120].map(angle => <g key={angle} transform={`rotate(${angle} 24 24)`}>
      <ellipse cx="24" cy="14" rx="3.3" ry="9" fill="currentColor" />
      <ellipse cx="24" cy="34" rx="3.3" ry="9" fill="currentColor" />
    </g>)}
  </svg>;
}
