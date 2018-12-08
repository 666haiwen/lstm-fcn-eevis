const control = (
  state = {
    type: 'SAMPLE-TOPO'
  }, action) => {
    switch (action.type) {
      case 'TOPO-SAMPLE':
        return {
          ...state,
          type: action.type
        };
      default:
        return state;
    }
};

export default control;
