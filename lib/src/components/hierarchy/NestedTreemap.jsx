import React, { useState, useMemo } from 'react';
import { Treemap, ResponsiveContainer } from 'recharts';
import Dialog from '../ui/Dialog';
import { getEnergyColor, getCategoryColor } from '../../utils/energyColors';
import './NestedTreemap.css';

const numberFormatter = (value) => {
  if (value == null || Number.isNaN(value)) return '-';
  const valInJoules = value / 1000;
  return new Intl.NumberFormat(undefined, { minimumFractionDigits: 1, maximumFractionDigits: 1 }).format(valInJoules);
};

// Custom Content for Level 1 (Top Modules)
function TopModuleContent(props) {
  const { x, y, width, height, name, actualEnergy, value, root, onClick, depth, originalData } = props;
  
  // Ignore depth 0 to prevent the "red treemap behind the main treemap" bug
  if (depth === 0) {
    return <rect x={x} y={y} width={width} height={height} fill="transparent" stroke="none" />;
  }
  
  const displayEnergy = actualEnergy !== undefined ? actualEnergy : (value || 0);
  const max = root?.value ?? value;
  const color = getEnergyColor(value, max);

  const formattedValue = numberFormatter(displayEnergy) + " mJ";
  
  // Dynamically calculate font sizes so text NEVER overflows
  const nameFontSize = Math.max(7, Math.min(15, (width - 12) / (0.55 * (name || '').length)));
  const valFontSize = Math.max(7, Math.min(12, (width - 12) / (0.55 * formattedValue.length)));
  
  // Only hide if the box is genuinely too tiny to draw even a 7px font
  const canFitText = width > 25 && height > 22;

  // For very tall and narrow boxes, it's sometimes better to hide text or adjust
  return (
    <g onClick={() => { if(originalData && onClick) onClick(props); }} style={{ cursor: 'pointer' }} className="treemap-node">
      <rect x={x} y={y} width={width} height={height} fill={color} stroke="#fff" strokeWidth={2} rx={8} ry={8} />
      {canFitText && (
        <>
          <text x={x + width / 2} y={y + height / 2 - 4} textAnchor="middle" fill="#000" fontSize={nameFontSize} fontWeight={700} style={{ pointerEvents: 'none' }}>
            {name}
          </text>
          <text x={x + width / 2} y={y + height / 2 + 12} textAnchor="middle" fill="#000" fontSize={valFontSize} fontWeight={700} style={{ pointerEvents: 'none' }}>
            {formattedValue}
          </text>
        </>
      )}
    </g>
  );
}

// Custom Content for Level 2 & 3 (Subgroups / Child Modules)
function SubgroupContent(props) {
  const { x, y, width, height, name, actualEnergy, value, category, onClick, depth } = props;
  
  if (depth === 0) {
    return <rect x={x} y={y} width={width} height={height} fill="transparent" stroke="none" />;
  }

  const color = category ? getCategoryColor(category) : '#9CA3AF';
  
  const displayEnergy = actualEnergy !== undefined ? actualEnergy : (value || 0);
  const formattedValue = numberFormatter(displayEnergy) + " mJ";
  
  const nameFontSize = Math.max(7, Math.min(15, (width - 12) / (0.55 * (name || '').length)));
  const valFontSize = Math.max(7, Math.min(12, (width - 12) / (0.55 * formattedValue.length)));
  
  const canFitText = width > 25 && height > 22;

  return (
    <g onClick={() => { if (onClick) onClick(props); }} style={{ cursor: onClick ? 'pointer' : 'default' }} className="treemap-node">
      <rect x={x} y={y} width={width} height={height} fill={color} stroke="#fff" strokeWidth={2} rx={8} ry={8} />
      {canFitText && (
        <>
          <text x={x + width / 2} y={y + height / 2 - 4} textAnchor="middle" fill="#fff" fontSize={nameFontSize} fontWeight={700} style={{ pointerEvents: 'none' }}>
            {name}
          </text>
          <text x={x + width / 2} y={y + height / 2 + 12} textAnchor="middle" fill="#fff" fontSize={valFontSize} fontWeight={700} style={{ pointerEvents: 'none' }}>
            {formattedValue}
          </text>
        </>
      )}
    </g>
  );
}

export default function NestedTreemap({ data }) {
  const [selectedModule, setSelectedModule] = useState(null);
  const [selectedSubgroup, setSelectedSubgroup] = useState(null);

  // Level 1 Data: Top modules
  const topLevelData = useMemo(() => {
    const validData = data.filter(mod => (mod.energy || 0) > 0);
    if (validData.length === 0) return [];
    
    // Find max energy to set a minimum visual threshold
    const maxEnergy = Math.max(...validData.map(mod => mod.energy));
    const minVisualSize = maxEnergy * 0.015; // 1.5% of max energy

    return validData.map(mod => ({
      name: mod.module,
      size: Math.max(mod.energy || 0, minVisualSize), // Visual size
      actualEnergy: mod.energy || 0,                  // True value for text display
      originalData: mod
    }));
  }, [data]);

  // Level 2 Data: 3 Subgroups (external, stdlib, self) for the selected module
  const subgroupData = useMemo(() => {
    if (!selectedModule) return [];
    
    const mod = selectedModule.originalData;
    const deps = mod.dependencies || [];
    
    let externalEnergy = 0;
    let stdlibEnergy = 0;
    
    deps.forEach(dep => {
      const e = dep.energy || 0;
      if (dep.category === 'external') {
        externalEnergy += e;
      } else if (dep.category === 'stdlib') {
        stdlibEnergy += e;
      }
    });
    
    // The remainder goes to 'self' to ensure sum of 3 equals total module energy
    const selfEnergy = Math.max(0, (mod.energy || 0) - externalEnergy - stdlibEnergy);
    
    const rawData = [
      { name: 'external', actualEnergy: externalEnergy, category: 'external' },
      { name: 'stdlib', actualEnergy: stdlibEnergy, category: 'stdlib' },
      { name: 'self', actualEnergy: selfEnergy, category: 'self' }
    ].filter(item => item.actualEnergy > 0); // Hide empty subgroups

    if (rawData.length === 0) return [];
    
    const maxEnergy = Math.max(...rawData.map(item => item.actualEnergy));
    const minVisualSize = maxEnergy * 0.03;

    return rawData.map(item => ({
      ...item,
      size: Math.max(item.actualEnergy, minVisualSize)
    }));
  }, [selectedModule]);

  // Level 3 Data: Children of the selected subgroup
  const childrenData = useMemo(() => {
    if (!selectedModule || !selectedSubgroup) return [];
    
    const mod = selectedModule.originalData;
    const deps = mod.dependencies || [];
    
    let rawData = [];

    if (selectedSubgroup.name === 'self') {
      // Gather any dependencies that aren't external or stdlib, and the module's own baseline self energy
      const selfDeps = deps.filter(dep => dep.category !== 'external' && dep.category !== 'stdlib')
        .map(dep => ({
          name: dep.module,
          actualEnergy: dep.energy || 0,
          category: dep.category || 'self'
        }));
      
      const externalEnergy = deps.filter(d => d.category === 'external').reduce((acc, d) => acc + (d.energy || 0), 0);
      const stdlibEnergy = deps.filter(d => d.category === 'stdlib').reduce((acc, d) => acc + (d.energy || 0), 0);
      const totalDepsEnergy = deps.reduce((acc, d) => acc + (d.energy || 0), 0);
      const pureSelfEnergy = Math.max(0, (mod.energy || 0) - totalDepsEnergy);
      
      if (pureSelfEnergy > 0) {
        selfDeps.unshift({
          name: mod.module + ' (base self)',
          actualEnergy: pureSelfEnergy,
          category: 'self'
        });
      }
      
      rawData = selfDeps.filter(item => item.actualEnergy > 0);
    } else {
      rawData = deps
        .filter(dep => dep.category === selectedSubgroup.name)
        .map(dep => ({
          name: dep.module,
          actualEnergy: dep.energy || 0,
          category: dep.category
        }))
        .filter(item => item.actualEnergy > 0);
    }

    if (rawData.length === 0) return [];
    
    const maxEnergy = Math.max(...rawData.map(item => item.actualEnergy));
    const minVisualSize = maxEnergy * 0.015;

    return rawData.map(item => ({
      ...item,
      size: Math.max(item.actualEnergy, minVisualSize)
    }));
  }, [selectedModule, selectedSubgroup]);

  const handleModuleClick = (nodeData) => {
    setSelectedModule(nodeData);
    setSelectedSubgroup(null);
  };

  const handleSubgroupClick = (nodeData) => {
    setSelectedSubgroup(nodeData);
  };

  const closeDialog = () => {
    setSelectedModule(null);
    setSelectedSubgroup(null);
  };

  const goBack = () => {
    if (selectedSubgroup) {
      setSelectedSubgroup(null);
    } else if (selectedModule) {
      setSelectedModule(null);
    }
  };

  return (
    <div className="nested-treemap-container">
      {topLevelData.length > 0 ? (
        <ResponsiveContainer width="100%" height={850}>
          <Treemap
            data={topLevelData}
            dataKey="size"
            aspectRatio={4 / 3}
            isAnimationActive={false}
            content={(props) => (
              <TopModuleContent 
                {...props} 
                onClick={() => handleModuleClick(props)} 
              />
            )}
          />
        </ResponsiveContainer>
      ) : (
        <div className="no-data">No energy data available for treemap.</div>
      )}

      {/* Dialog for Level 2 & 3 */}
      <Dialog 
        isOpen={!!selectedModule} 
        onClose={closeDialog}
        onBack={selectedSubgroup ? goBack : null}
        backText={selectedSubgroup ? "← Back to Subgroups" : undefined}
        title={
          selectedSubgroup 
            ? `${selectedModule?.name} / ${selectedSubgroup.name} Dependencies` 
            : `${selectedModule?.name} Subgroups`
        }
      >
        <div className="dialog-treemap-wrapper">
          {(!selectedSubgroup) ? (
            /* Level 2 Treemap */
            subgroupData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <Treemap
                  data={subgroupData}
                  dataKey="size"
                  aspectRatio={4 / 3}
                  isAnimationActive={false}
                  content={(props) => (
                    <SubgroupContent 
                      {...props} 
                      onClick={() => handleSubgroupClick(props)} 
                    />
                  )}
                />
              </ResponsiveContainer>
            ) : (
              <div className="no-data">No subgroup data available.</div>
            )
          ) : (
            /* Level 3 Treemap */
            childrenData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <Treemap
                  data={childrenData}
                  dataKey="size"
                  aspectRatio={4 / 3}
                  isAnimationActive={false}
                  content={(props) => (
                    <SubgroupContent 
                      {...props} 
                      // No click handler for leaves
                    />
                  )}
                />
              </ResponsiveContainer>
            ) : (
              <div className="no-data">No dependencies in this category.</div>
            )
          )}
        </div>
      </Dialog>
    </div>
  );
}
