import React from 'react';
import PropTypes from 'prop-types';
// import { connect } from 'react-redux';
import * as d3 from 'd3';
import * as gl from '../const';
import '../css/disMatrix.css';
import * as api from '../api';
// import * as actions from '../actions';

class DisMatrix extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      tooltip: <div className='dis-tooltip' hidden></div>
    };
    this.color = d3.scaleSequential(d3.interpolateBlues).domain([0, gl.DIS_MAX]);
  }

  highLight(idx, idy) {
    const x = d3.event.pageX;
    const y = d3.event.pageY;
    this.props.highLightSample(idx, idy);
    d3.select('.dis-row').selectAll('.dis-box')
        .classed('hightLight-y', false);
    d3.select('.dis-col').selectAll('.dis-box')
        .classed('hightLight-x', false);
    console.log(d3.select('.dis-col').selectAll('.dix-box'));
    d3.select('.dis-col').select('#dis-box-col-' + idx)
        .classed('hightLight-x', true);
    d3.select('.dis-row').select('#dis-box-row-' + idy)
        .classed('hightLight-y', true);
    api.getBusDistance(idx, idy).then(d => {
      const data = d.data;
      const tooltip = 
      <div className='dis-tooltip' style={{left: x - 1257, top:y - 10}}>
        <p>f1 in S2: {' ' + data[0]}</p>
        <p>f2 in S2: {' ' + data[1]}</p>
        <p>f1 in S1: {' ' + data[2]}</p>
        <p>f2 in S1: {' ' + data[3]}</p>
      </div>;
      this.setState({
        tooltip: tooltip
      });
    });
  }

  drawDisMatrix(bus_dis, sample) {
    const hiddenTooltip = () => {
      this.props.highLightSample(-1, -1);
      this.setState({
        tooltip: <div className='dis-tooltip' hidden></div>
      });
    };
    const length = sample.length;
    d3.select('.dis-svg-panel').selectAll('.disMatrix-svg').remove();
    const svg = d3.select('.dis-svg-panel')
        .append('svg')
      .attr('class', 'disMatrix-svg')
      .attr('width', length * gl.DIS_MATRIX_LENGTH)
      .attr('height', length * gl.DIS_MATRIX_LENGTH)
      .attr('transform', 'translate(50,40)')
      .on('mouseleave', () => {hiddenTooltip();});
    const row = svg.selectAll('g')
        .data(sample).enter()
        .append('g')
      .attr('class', d => 'dis-g-' + d.id)
      .attr('transform', (d, i) => `translate(0, ${i * 40})`);
    row.each((d,i) => {
      const g = svg.select('.dis-g-' + d.id);
      g.selectAll('rect')
        .data(bus_dis[i]).enter()
        .append('rect')
          .attr('fill', d => this.color(d))
          .attr('width', gl.DIS_MATRIX_LENGTH - 2)
          .attr('height', gl.DIS_MATRIX_LENGTH - 2)
          .attr('x', (d,_i) => _i*gl.DIS_MATRIX_LENGTH)
          .attr('y', 0)
          .on('mouseenter', (_d, _i) => this.highLight(d.id, sample[_i].id));
      const textd = [];
      bus_dis[i].forEach(d => {
        if (d == 10000) 
          textd.push('inf');
        else
          textd.push(('' + d).substr(0,4));
      });
      g.selectAll('text')
        .data(textd).enter()
        .append('text')
          .attr('x', (d,_i) => _i*gl.DIS_MATRIX_LENGTH + 17 - d.length * 2.5)
          .attr('font-size', '14px')
          .attr('y', 25)
          .text(d => d);
    });
  }

  componentDidMount() {
    this.drawDisMatrix(this.props.disMatrix, this.props.sample);
  }

  UNSAFE_componentWillReceiveProps(nextProps) {
    this.drawDisMatrix(nextProps.disMatrix, nextProps.sample);
  }

  render() {
    const { sample } = this.props;
    const rowList = [];
    const colList = [];
    sample.forEach((v, i) => {
      rowList.push(<p key={i} className='dis-box' id={'dis-box-row-' + v.id} style={{left: i * gl.DIS_MATRIX_LENGTH}}>{v.id}</p>);
      colList.push(<p key={i} className='dis-box' id={'dis-box-col-' + v.id}style={{top: i * gl.DIS_MATRIX_LENGTH}}>{v.id}</p>);
    });

    return (
      <div className='disMatrix-div'>
        <div className='dis-ul dis-row'>
          {rowList.map(li => li)}
        </div>
        <div className='dis-ul dis-col'>
          {colList.map(li => li)}
        </div>
        <div className='dis-svg-panel'>
          <svg className='disMatrix-svg'></svg>
        </div>
        {this.state.tooltip}
      </div>
    );
  }
}

DisMatrix.protoTypes = {
  disMatrix: PropTypes.array.isRequired,
  sample: PropTypes.array.isRequired,
  highLightSample: PropTypes.func.isRequired,
};
export default DisMatrix;