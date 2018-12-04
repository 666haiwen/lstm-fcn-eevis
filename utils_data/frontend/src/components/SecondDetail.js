import React from 'react';
// import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import DisMatrix from './DisMatrix';
import Topology from './Topology';
import * as d3 from 'd3';
// import * as gl from '../const';
// import * as api from '../api';
import * as actions from '../actions';

class SecondDetail extends React.Component {
  hidden() {
    const t=d3;
    console.log(t);
    d3.select('.topology-div').style('visibility', 'hidden');
    d3.select('.disMatrix-div').style('visibility', 'hidden');
  }
  componentDidMount() {
    this.hidden();
  }
  componentDidUpdate() {
    this.hidden();
    if (this.props.showType == 'TOPO')
      d3.select('.topology-div').style('visibility', 'visible');
    if (this.props.showType == 'DIS_MATRIX')
      d3.select('.disMatrix-div').style('visibility', 'visible');
  }
  render() {
    return(
      <div>
        <Topology sampleId={this.props.sampleId} fault={this.props.fault} type={this.props.showType}></Topology>
        <DisMatrix disMatrix={this.props.disMatrix} sample={this.props.disSample} type={this.props.showType}
          highLightSample={this.props.HighLightDisSample}>
        </DisMatrix>
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
  sampleId: state.second.topoSample,
  fault: state.second.fault
});
const SecondDetailContainer = connect(mapStateToProps, actions)(SecondDetail);
export default SecondDetailContainer;

