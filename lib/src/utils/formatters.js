export const formatEnergy = (value) => {
  if (value == null || Number.isNaN(value)) return '-';
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 4 }).format(value);
};

export const compactEnergy = (value) => {
  if (value == null || Number.isNaN(value)) return '-';
  return new Intl.NumberFormat('en-US', { 
    notation: 'compact', 
    maximumFractionDigits: 2 
  }).format(value);
};
