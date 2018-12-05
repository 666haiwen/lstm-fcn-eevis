import React from 'react';
import TsnePanel from './Tsne';
import SecondDetail from './SecondDetail';
import '../css/index.css';

class App extends React.Component {
  render() {
    return (
      <div id="app">
        <TsnePanel></TsnePanel>
        <SecondDetail></SecondDetail>
      </div>
    );
  }
}

export default App;
