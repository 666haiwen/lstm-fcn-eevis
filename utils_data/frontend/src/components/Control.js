import React from 'react';
import { connect } from 'react-redux';
// import * as d3 from 'd3';
import * as actions from '../actions';

class Control extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      birchId: -1,
      labels: [],
      labelId : -1
    };
  }

  showLabel() {

  }

  handleBirch(e) {
    const v = e.target.value;
    this.props.SetBirch(v);
    this.setState({
      birchId: v
    });
  }

  setLabel(event) {
    console.log(event);
  }

  render() {
    return (
      <div className="control-div">
        <select id='birch-select' onChange={e => this.handleBirch(e)} 
          value={this.state.birchId}>
          <option value="-1">Select the diffierent Birch</option>
          <option value="500">500 Labels of Birch</option>
          <option value="400">400 Labels of Birch</option>
          <option value="300">300 Labels of Birch</option>
          <option value="200">200 Labels of Birch</option>
          <option value="100">100 Labels of Birch</option>
          <option value="50">50 Labels of Birch</option>
        </select>
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  ...state.control
});
const ControlPanel = connect(mapStateToProps, actions)(Control);
export default ControlPanel;
