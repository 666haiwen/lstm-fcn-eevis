const control = (
  state = {
    birchId: '-1',
    sampleId: [],
    sampleType: 'NONE',
    newSample: [],
    fault: {},
   }, action) => {
    let sampleId = state.sampleId;
    let newSample = [];
    switch (action.type) {
      case 'SET_BIRCH':
        return {
          ...state,
          birchId: action.birchId
        };
      case 'ADD_SAMPLE':
        action.sampleId.forEach(v => {
          if (!sampleId.includes(v))
            newSample.push(v);
        });
        if (newSample.length == 0)
          return state;
        sampleId = sampleId.concat(newSample);
        return {
          ...state,
          sampleId: sampleId,
          sampleType: 'ADD',
          newSample: action.sampleId,
          fault: action.fault
        };
      case 'DELETE_SAMPLE':
        action.sampleId.forEach(v => {
          if (sampleId.includes(v))
            newSample.push(v);
        });
        if (newSample.length == 0)
          return state;
        newSample.forEach(v => {
          sampleId.splice(sampleId.indexOf(v), 1);
        });
        return {
          ...state,
          sampleId: sampleId,
          newSample: action.sampleId,
          sampleType: 'DELETE',
        };
      default:
        return state;
    }
  };

export default control;