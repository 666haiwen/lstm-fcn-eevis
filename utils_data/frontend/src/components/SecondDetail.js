import React from 'react';
import { connect } from 'react-redux';
import DisMatrix from './DisMatrix';
import TopologyPanel from './Topology';
import CorrcoefPanel from './Corrcoef';
import * as d3 from 'd3';
import * as actions from '../actions';

class SecondDetail extends React.Component {
  hidden() {
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
        <TopologyPanel sampleId={this.props.sampleId} fault={this.props.fault} />
        <DisMatrix disMatrix={this.props.disMatrix} sample={this.props.disSample}
          highLightSample={this.props.HighLightDisSample} />
        <CorrcoefPanel sampleId={this.props.sampleId} type={this.props.showType} />
      </div>
    );
  }
}


const mapStateToProps = (state) => ({
  showType: state.second.showType,
  disMatrix: state.second.disMatrix,
  disSample: state.second.disSample,
  sampleId: state.second.topoSample,
  fault: state.second.fault
});
const SecondDetailContainer = connect(mapStateToProps, actions)(SecondDetail);
export default SecondDetailContainer;

