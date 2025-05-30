/**
 * one-pass Damerau/Levenshtein for the “1 mistake = 1/3 point” rule
 * Returns 0 when exactly correct, 1 when 1 edit away, >1 otherwise.
 */
export function distanceOne(g, s) {
  const n = g.length, m = s.length;
  if (Math.abs(n - m) > 1) return 2;

  let i = 0, j = 0, mismatch = false;
  while (i < n && j < m) {
    if (g[i] === s[j]) { i++; j++; continue; }
    if (mismatch) return 2;          // already saw one edit
    mismatch = true;

    // substitution
    if (n === m) { i++; j++; continue; }
    // deletion in s
    if (n > m)  { i++; continue; }
    // insertion in s
    if (m > n)  { j++; continue; }
  }
  if (!mismatch) return (Math.abs(n - m) === 1) ? 1 : 0;
  return 1;
}
