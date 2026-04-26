export const CATEGORY_COLORS = {
  internal: '#4F46E5', // Indigo
  stdlib: '#059669',   // Emerald
  external: '#DC2626', // Red
  self: '#7C3AED',     // Violet
};

export const getCategoryColor = (category) => {
  return CATEGORY_COLORS[category?.toLowerCase()] || '#9CA3AF';
};
