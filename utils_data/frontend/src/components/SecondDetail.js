import React from 'react';
// import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import DisMatrix from './DisMatrix';
import Topology from './Topology';
// import * as d3 from 'd3';
// import * as gl from '../const';
// import * as api from '../api';
import * as actions from '../actions';

class SecondDetail extends React.Component {
  constructor(props) {
    super(props);
    this.topo = <Topology></Topology>;
  }
  render() {
    let returnPanel;
    console.log(this.props);
    if (this.props.showType == 'DIS_MATRIX') {
      returnPanel = <DisMatrix disMatrix={this.props.disMatrix} sample={this.props.disSample}
      highLightSample={this.props.HighLightDisSample}
      ></DisMatrix>;
     }
     if (this.props.showType == 'TOPO') {
      returnPanel = this.topo;
     }
    return(
      <div>
        {returnPanel}
      </div>
    );
  }
}



SecondDetail.protoTypes = {
};
const mapStateToProps = (state) => ({
  showType: state.second.showType,
  disMatrix: state.second.disMatrix,
  disSample: state.second.disSample,
});
const SecondDetailContainer = connect(mapStateToProps, actions)(SecondDetail);
export default SecondDetailContainer;

