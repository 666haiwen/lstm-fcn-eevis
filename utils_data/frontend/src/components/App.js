import React from 'react';
import TsnePanel from './Tsne';
import SecondDetail from './SecondDetail';
import ControlPanel from './Control';
// import TopologyPanel from './Topology';
import '../css/index.css';

class App extends React.Component {
  render() {
    return (
      <div id="app">
        <TsnePanel></TsnePanel>
        <ControlPanel></ControlPanel>
        <SecondDetail></SecondDetail>
      </div>
    );
  }
}

export default App;
