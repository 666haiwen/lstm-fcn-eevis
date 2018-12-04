import React from 'react';
import PropTypes from 'prop-types';
import * as api from '../api';
import * as d3 from 'd3';
// import * as gl from '../const';

class Corrcoef extends React.Component {
  constructor(props) {
    super(props);
    console.log('construct!', props);
    this.div = null;
    this.sampleId = -1;
    this.data = [];
  }

  UNSAFE_componentWillReceiveProps(nextProps) {
    console.log(nextProps);
    if (nextProps.sampleId != this.sampleId) {
      this.sampleId = nextProps.sampleId;
      api.getCorrcoef(this.sampleId).then(data =>{
        this.showCorrcoef(data);
      });
    }
  }

  showCorrcoef(d) {
    const {data, max, min, busDistance} = d;
    d3.select('.corrcoef-div').selectAll('div').remove();
    const panel = d3.select('.corrcoef-div').append('div')
        .attr('class', 'corrcoef-panel');
    const svg = panel.append('svg')
        .attr('class', 'corrcoef-svg')
        .attr('transform', 'translate(50, 40)');
    const color = d3.scaleSequential(d3.interpolateRdBu).domain([min, max]);
    // const fault = {'i':busDistance[0], 'j':busDistance[1]};
    const sortBus = busDistance.slice();
    sortBus.sort();
    sortBus.forEach((busId, i) => {
      const index = busDistance.indexOf(busId);
      const g = svg.append('g')
        .attr('class', 'corrcoef-g-' + busId)
        .attr('transform', `translate(0, ${i})`);
      g.selectAll('circle')
        .data(data[index]).enter()
        .append('circle')
            .attr('fill', d=>color(d))
            .attr('x', (d,_i)=> _i)
            .attr('y', 0)
            .attr('r', 1);
    });
  }

  render() {
    return (<div className='corrcoef-div'>{this.div}</div>);
  }
}

Corrcoef.protoTypes = {
  sampleId: PropTypes.number.isRequired,
};

export default Corrcoef;
