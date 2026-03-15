export const energyPalette = {
  primary: '#2C7A7B',
  secondary: '#0F3D3E',
  low: '#2ECC71',
  moderate: '#F1C40F',
  high: '#E67E22',
  critical: '#E74C3C',
};

export function getEnergyColor(value, maxValue) {
  if (value == null || maxValue == null || maxValue === 0) return energyPalette.moderate;
  const ratio = value / maxValue;
  if (ratio <= 0.25) return energyPalette.low;
  if (ratio <= 0.55) return energyPalette.moderate;
  if (ratio <= 0.8) return energyPalette.high;
  return energyPalette.critical;
}
