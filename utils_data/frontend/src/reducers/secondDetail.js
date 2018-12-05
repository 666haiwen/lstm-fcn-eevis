const second = (
  state = {
    showType: 'None',
    disMatrix: [],
    disSample: [],
    idx: -1,
    idy: -1,
    topoSample: -1,
    fault: {i:-1, j:-1},
    corrcoefIds: [],
  }, action) => {
    switch (action.type) {
      case 'SHOW_NONE':
        return {
          ...state,
          showType: 'None'
        };
      case 'SHOW_DIS_MATRIX':
        return {
          ...state,
          showType: 'DIS_MATRIX',
          disMatrix: action.disMatrix,
          disSample: action.sample,
        };
      case 'HIGH_LIGHT_DIS':
        return {
          ...state,
          idx: action.idx,
          idy: action.idy
        };
      case 'TOPO_SAMPLE':
        return {
          ...state,
          showType: 'TOPO',
          topoSample: action.sampleId,
          fault: action.fault
        };
      case 'CORRCOEF_IDS':
        return {
          ...state,
          corrcoefIds: action.corrcoefIds
        };
      default:
        return state;
    }
};

export default second;