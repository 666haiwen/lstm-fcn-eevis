const control = (
  state = {
    type: 'SAMPLE-TOPO'
  }, action) => {
    switch (action.type) {
      case 'CHANGE-SAMPLE-TOPO':
        return {
          ...state,
          type: action.v
        };
      default:
        return state;
    }
};

export default control;
