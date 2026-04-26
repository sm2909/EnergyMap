export const formatEnergy = (value) => {
  if (value == null || Number.isNaN(value)) return '-';
  const valInJoules = value / 1000;
  return new Intl.NumberFormat(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(valInJoules);
};

export const compactEnergy = (value) => {
  if (value == null || Number.isNaN(value)) return '-';
  const valInJoules = value / 1000;
  return new Intl.NumberFormat('en-US', { 
    notation: 'compact', 
    minimumFractionDigits: 1,
    maximumFractionDigits: 1 
  }).format(valInJoules);
};
