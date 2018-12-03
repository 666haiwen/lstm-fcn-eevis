export const SetBirch = (v) => ({
  type: 'SET_BIRCH',
  birchId: v
});

export const AddSample = (id, fault) => ({
  type: 'ADD_SAMPLE',
  sampleId: id,
  fault: fault
});

export const DeleteSample = (id) => ({
  type: 'DELETE_SAMPLE',
  sampleId: id
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
