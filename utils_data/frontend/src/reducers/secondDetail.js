const second = (
  state = {
    showType: 'None',
    disMatrix: [],
    disSample: [],
    idx: -1,
    idy: -1
  }, action) => {
    switch (action.type) {
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
      default:
        return state;
    }
};

export default second;