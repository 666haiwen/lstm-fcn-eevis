const second = (
  state = {
    showType: 'None',
    disMatrix: [],
    disSample: [],
    topoSample: [],
    fault: {i:-1, j:-1},
  }, action) => {
    let sampleIds;
    switch (action.type) {
      case 'SHOW_NONE':
        return {
          ...state,
          showType: 'None'
        };
      case 'SHOW_DIS_MATRIX':
      sampleIds = [];
      action.sample.forEach(v => {
        sampleIds.push(v.id);
      });
        return {
          ...state,
          showType: 'DIS_MATRIX',
          disMatrix: action.disMatrix,
          disSample: action.sample,
          topoSample: sampleIds,
        };
      case 'TOPO_SAMPLE':
        return {
          ...state,
          showType: 'TOPO',
          topoSample: action.sampleId,
          fault: action.fault
        };
      case 'DIS_MATRIX_SAMPLE':
        return {
          ...state,
          showType: 'TOPO'
        };
      default:
        return state;
    }
};

export default second;