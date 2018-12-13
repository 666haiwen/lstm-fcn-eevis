export const ChangeType = (v) => ({
  type: 'CHANGE-SAMPLE-TOPO',
  v: v
});

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

export const ShowNone = () => ({
  type: 'SHOW_NONE'
});

export const DisMatrixSample = (sampleId) => ({
  type: 'DIS_MATRIX_SAMPLE',
  sampleId: sampleId
});
