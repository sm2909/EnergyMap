export const CATEGORY_COLORS = {
  internal: '#4F46E5', // Indigo
  stdlib: '#059669',   // Emerald
  external: '#DC2626', // Red
  self: '#7C3AED',     // Violet
};

export const getCategoryColor = (category) => {
  return CATEGORY_COLORS[category?.toLowerCase()] || '#9CA3AF';
};

// Generate a color on a scale from light blue to deep red based on value/max ratio
export const getEnergyColor = (value, max) => {
  if (!max || max === 0) return '#3B82F6';
  const ratio = Math.min(1, Math.max(0, value / max));
  
  // Simple gradient from Blue (#3B82F6) to Red (#EF4444)
  if (ratio < 0.2) return '#3B82F6'; // Blue
  if (ratio < 0.4) return '#8B5CF6'; // Light Blue/Purple
  if (ratio < 0.6) return '#A855F7'; // Purple
  if (ratio < 0.8) return '#D946EF'; // Fuchsia
  return '#EF4444'; // Red
};

export const energyPalette = {
  primary: '#3B82F6',
  secondary: '#8B5CF6',
  accent: '#EF4444'
};

