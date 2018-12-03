import React from 'react';
import PropTypes from 'prop-types';
import * as d3 from 'd3';
import * as gl from '../const';
// import * as api from '../api';
// import * as actions from '../actions';

class WaveLine extends React.Component {
  constructor(props) {
    super(props);
  }

  componentDidMount() {
    console.log('did mount!');
    this.drawLine(this.props.data);
  }
  drawLine(d) {
    // this.svg = d3.select('#waveline-' + this.props.number)
    //   .append('svg')
    //     .attr('width', gl.WAVELINE_WIDTH)
    //     .attr('height', gl.WAVELINE_HEIGHT);
    this.svg = d3.select('#waveline-svg-' + this.props.number);
    const data = [];
    d.forEach((v,i) => {
      data.push([v, i/100]);
    });
    const x = data.length / 100;
    const max = Math.max(...d);
    const min = Math.min(...d);
    const width = gl.WAVELINE_WIDTH;
    const height = gl.WAVELINE_HEIGHT;
    const padding = {top: 0, right:20, bottom: 80, left: 50};
    const xScale = d3.scaleLinear()
        .domain([0, x])
        .range([0, width - padding.left - padding.right]);
    const yScale = d3.scaleLinear()
        .domain([min, max])
        .range([height - padding.top - padding.bottom, 0]);
    const xAxis = d3.axisBottom()
              .scale(xScale);
    const yAxis = d3.axisLeft()
              .scale(yScale);
    this.svg.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(' + padding.left + ',' + (height - padding.bottom) + ')')
      .call(xAxis);
    this.svg.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(' + padding.left + ',' + padding.top + ')')
      .call(yAxis);
    const linePath = d3.line()
      .x(d => xScale(d[1]))
      .y(d => yScale(d[0]));
    this.svg.append('g')
      .append('path')
        .attr('class', 'line-path')
        .attr('transform', 'translate(' + padding.left + ',' + padding.top + ')')
        .attr('d', linePath(data))
        .attr('fill', 'none')
        .attr('stroke-width', 1)
        .attr('stroke', 'black');

  }
  render() {
    console.log('!!!!!!', this.props);
    return(
      <div className='waveline-div' id={'waveline-' + this.props.number} style={{left: (gl.WAVELINE_WIDTH + gl.WAVELINE_TRANS) * this.props.number }}>
        <div className='waveline-title'>
          <p>SampleId: {this.props.sampleId} BusId:{this.props.busId}  vBase:{this.props.vBase}</p>
        </div>
        <svg id={'waveline-svg-' + this.props.number} width={gl.WAVELINE_WIDTH} height={gl.WAVELINE_HEIGHT}
        color='black'>
          {/* {this.drawLine(this.props.data)} */}
        </svg>
      </div>
    );
  }
}

WaveLine.protoTypes = {
  number: PropTypes.number.isRequired,
  sampleId: PropTypes.number.isRequired,
  busId: PropTypes.number.isRequired,
  vBase: PropTypes.number.isRequired,
  data: PropTypes.array.isRequired,
};

export default WaveLine;
