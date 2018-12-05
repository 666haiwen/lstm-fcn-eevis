import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import * as api from '../api';
import * as d3 from 'd3';

class Corrcoef extends React.Component {
  constructor(props) {
    super(props);
    this.sampleId = -1;
    this.busIds = [];
  }

  notSame(sampleId, busIds) {
    if (busIds.length == 0)
      return false;
    if (this.sampleId != sampleId || busIds.length != this.busIds.length)
      return true;
    busIds.forEach(v => {
      if (!this.busIds.includes(v))
        return true;
    });
    return false;
  }

  UNSAFE_componentWillReceiveProps(nextProps) {
    if (nextProps.type != 'TOPO' || nextProps.busIds.length == 0) {
      d3.select('.corrcoef-div').selectAll('div').remove();
      return;
    }
    const {sampleId, busIds} = nextProps;
    if (this.notSame(sampleId, busIds)) {
      this.sampleId = sampleId;
      this.busIds = busIds;
      api.getCorrcoef(sampleId, busIds).then(data =>{
        this.showCorrcoef(data);
      }); 
    }
  }

  showCorrcoef(d) {
    const {data, /*max, min,*/ vaild_bus} = d;
    d3.select('.corrcoef-div').selectAll('div').remove();
    const panel = d3.select('.corrcoef-div').append('div')
        .attr('class', 'corrcoef-panel');
    const svg = panel.append('svg')
        .attr('class', 'corrcoef-svg')
        .attr('transform', 'translate(25, 5)');
    const color = d3.scaleSequential(d3.interpolateRdBu).domain([-1, 1]);
    vaild_bus.forEach((busId, i) => {
      const g = svg.append('g')
        .attr('class', 'corrcoef-g-' + busId)
        .attr('transform', `translate(0, ${i * 12})`);
      g.selectAll('rect')
        .data(data[i]).enter()
        .append('rect')
            .attr('fill', d=>color(d))
            .attr('width', 10)
            .attr('height', 10)
            .attr('x', (d,_i)=> _i * 12)
            .attr('y', 0);
    });
    const svgDefs = svg.append('defs');
    const colorGradient = svgDefs.append('linearGradient')
      .attr('id', 'colorGradient');
    colorGradient.append('stop')
        .attr('offset', '0')
        .style('stop-color', color(-1));
    colorGradient.append('stop')
        .attr('offset', '1')
        .style('stop-color', color(1));
    colorGradient.append('stop')
        .attr('offset', '0.5')
        .style('stop-color', color(0));
    svg.append('rect')    
        .style('fill', 'url(#colorGradient)')
        .attr('x', 600)
        .attr('y', 600)
        .attr('width', 200)
        .attr('height', 20);

  }

  render() {
    return (<div className='corrcoef-div'></div>);
  }
}

Corrcoef.protoTypes = {
  sampleId: PropTypes.number.isRequired,
  busIds: PropTypes.array.isRequired,
};
const mapStateToProps = (state) => ({
  busIds: state.second.corrcoefIds,
});
const CorrcoefPanel = connect(mapStateToProps)(Corrcoef);

export default CorrcoefPanel;
