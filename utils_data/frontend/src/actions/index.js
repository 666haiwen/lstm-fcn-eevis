export const SetBirch = (v) => ({
  type: 'SET_BIRCH',
  birchId: v
});

export const TopoSample = (id, fault) => ({
  type: 'TOPO_SAMPLE',
  sampleId: id,
  fault: fault
});

export const ShowDisMatrix = (disMatrix, sample) => ({
  type: 'SHOW_DIS_MATRIX',
  disMatrix: disMatrix,
  sample: sample
});

export const HighLightDisSample = (idx, idy) => ({
  type: 'HIGH_LIGHT_DIS',
  idx: idx,
  idy: idy
});

export const ShowNone = () => ({
  type: 'SHOW_NONE'
});