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
    this.svg = d3.select('.waveline-svg');
  }

  UNSAFE_componentWillReceiveProps(nextProps) {
    this.drawLine(nextProps);
  }

  drawLine(props) {
    this.svg.selectAll('g').remove();
    const {busId, data} = props;
    if (busId.length == 0) 
      return;
    const lineData = [];
    data.forEach((v) => {
      let tmp_data = [];
      v.forEach((_v, i) => tmp_data.push([_v, i/100]));
      lineData.push(tmp_data);
    });
    const x = lineData[0].length / 100;
    const max =d3.max(data, d => Math.max(...d));
    const min = d3.min(data, d => Math.min(...d));
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
    busId.forEach((id, i) => {
      this.svg.append('g')
      .append('path')
        .attr('class', 'line-path')
        .attr('id', 'line-busId-' + id)
        .attr('transform', 'translate(' + padding.left + ',' + padding.top + ')')
        .attr('d', linePath(lineData[i]))
        .attr('fill', 'none')
        .attr('stroke-width', 1)
        .attr('stroke', 'black');
    });
  }

  render() {
    return(
      <div className='waveline-div'>
        <div className='waveline-title'>
          <p>SampleId: {this.props.sampleId} BusId:{this.props.busId}  vBase:{this.props.vBase}</p>
        </div>
        <svg className='waveline-svg' width={gl.WAVELINE_WIDTH} height={gl.WAVELINE_HEIGHT}
        color='black'>
          {/* {this.drawLine(this.props.data)} */}
        </svg>
      </div>
    );
  }
}

WaveLine.protoTypes = {
  sampleId: PropTypes.number.isRequired,
  busId: PropTypes.array.isRequired,
  vBase: PropTypes.array.isRequired,
  data: PropTypes.array.isRequired,
};

export default WaveLine;
