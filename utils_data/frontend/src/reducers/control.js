const control = (
  state = {
    type: 'SAMPLE-TOPO',
    sampleId: -1
  }, action) => {
    switch (action.type) {
      case 'CHANGE-SAMPLE-TOPO':
        return {
          ...state,
          type: action.v
        };
      case 'DIS_MATRIX_SAMPLE':
        return {
          ...state,
          sampleId: action.sampleId
        };
      case 'TOPO_SAMPLE':
        return {
          ...state,
          sampleId: action.sampleId[0],
        };
      default:
        return state;
    }
};

export default control;
