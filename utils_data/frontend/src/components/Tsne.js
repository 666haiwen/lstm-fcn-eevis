import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import * as d3 from 'd3';
import '../css/tsne.css';
import * as gl from '../const';
import * as api from '../api';
import * as actions from '../actions';
import * as d3lasso from '../d3-lasso';

class Tsne extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      faults: {},
      Number: 0,
      birch: -1,
    };
    this.idx = this.idy = -1;
    this.sampleId = [];
    api.getTsne().then(data => {
      let xScale = [data.pos[0][0], data.pos[0][0]];
      let yScale = [data.pos[0][1], data.pos[0][1]];
      data.pos.forEach(d => {
        if (d[0] > xScale[1])
          xScale[1] = d[0];
        if (d[0] < xScale[0])
          xScale[0] = d[0];
        if (d[1] > yScale[1])
          yScale[1] = d[1];
        if (d[1] < yScale[0])
          yScale[0] = d[1];
      });
      let rateX = (gl.WIDTH - 50) / (xScale[1] - xScale[0]),
          rateY = (gl.HEIGHT - 50) / (yScale[1] - yScale[0]);
      const faults = [];
      data.pos.forEach((d, i) => {
        faults.push({
          'id': i,
          'label': null,
          'class': 'label-hide',
          'pos' : {
            'x': (d[0] - xScale[0]) * rateX + 10,
            'y': (d[1] - yScale[0]) * rateY + 10
          },
          'fault': data.fault[i]
        });
      });
      this.drawCircle(faults);
      this.setState({
        faults: faults,
        Number: faults.length,
      });
    });
  }

  componentDidMount() {
    this.tsne = d3.select('.tsne-panel')
      .attr('width', gl.WIDTH)
      .attr('height', gl.HEIGHT);
  }

  handleBirch(e) {
    const v = e.target.value;
    if (v != this.state.birch) {
      api.getBirch(v).then(data => {
        const birch = data['labels'].sort((a,b) => b.length - a.length);
        const faults = this.state.faults;
        const label = [];
        for (let i = 0; i < birch.length; i++) {
          for (let j = 0; j < birch[i].length; j++) 
            label[birch[i][j]] = i;
        }
        for (let i = 0; i < this.state.Number; i++) {
          faults[i]['label'] = label[i];
          faults[i]['class'] = birch[label[i]].length > gl.LABEL_THREHOLD ? 
            'label-show' : 'label-hide';
        }
        this.setState({
          faults: faults,
          birch: v
        });
        this.drawCircle(faults);
      }); 
    }
  }

  UNSAFE_componentWillReceiveProps(nextProps) {
    if (nextProps.idx != this.idx || nextProps.idy != this.idy) {
      this.tsne.select('#sample-' + this.idx)
        .classed('hightLight-x', false);
      this.tsne.select('#sample-' + this.idy)
        .classed('hightLight-y', false);
      this.idx = nextProps.idx;
      this.idy = nextProps.idy;
      this.tsne.select('#sample-' + this.idx)
        .classed('hightLight-x', true);
      this.tsne.select('#sample-' + this.idy)
        .classed('hightLight-y', true);
    }
  }

  showLabel(d) {
    if (d.class == 'label-hide') 
      return;
    this.tsne.selectAll('circle')
      .classed('label-selected', false);
    this.tsne.selectAll('.label-hide')
      .attr('fill', gl.NO_LABEL_COLOR);
    this.tsne.selectAll('.label-show')
        .attr('fill', gl.HIDEN_COLOR);
    const val = d.label;
    this.tsne.selectAll('.label-' + val)
        .classed('label-selected', true);
  }

  sampleSelected(d) {
    if (this.props.type == 'SAMPLE-TOPO') {
      this.showDisMatrix(d);
    }
    else {
      const samples = [];
      d.each(v => {
        samples.push(v.id);
      });
      this.sampleId = samples;
      this.props.TopoSample(this.sampleId, {});
    }
  }

  showDisMatrix(samples) {
    const sampleIds = [];
    const disSample = [];
    samples.each(v => {
      sampleIds.push(v.id);
      disSample.push({
        id: v.id,
        fault: this.state.faults[v.id].fault
      });
    });
    this.tsne.select('#sample-' + this.sampleId)
          .classed('sample-select', false);
    if (sampleIds.length == 1) {
      this.addSample(disSample[0]);
      return;
    }
    if (sampleIds.length > 0) 
      api.getSampleDis(sampleIds).then(d => {
        this.props.ShowDisMatrix(d.dis, disSample);
      });
    else {
      this.tsne.select('#sample-' + this.sampleId)
          .classed('sample-select', false);
      this.props.ShowNone();      
    }
  }

  addSample(d) {
    if (this.props.control == 'TOPO-SAMPLE') {
      if (this.sampleId.includes(d.id)) {
        const index = this.sampleId.index(d.id);
        this.sampleId.splice(index, 1);
      }
      else
        this.sampleId.push(d.id);
      this.props.TopoSample(this.sampleId, {});
    }
    else
    {
      if (this.sampleId.length == 0) {
        this.tsne.select('#sample-' + d.id)
          .classed('sample-select', true);
        this.sampleId = [d.id];
        this.props.TopoSample(this.sampleId, d.fault);
      }
      if (this.sampleId[0] != d.id) {
        this.tsne.select('#sample-' + this.sampleId)
            .classed('sample-select', false);
        this.tsne.select('#sample-' + d.id)
            .classed('sample-select', true);
        this.sampleId[0] = d.id;
        this.props.TopoSample(this.sampleId, d.fault);
      }
    }
  }

  drawCircle(faults) {
    if (!this.tsne)
      return;
    faults.forEach((v, i) => {
      faults[i].x = v.pos.x;
      faults[i].y = v.pos.y;
    });
    this.tsne.selectAll('g').remove();
    const circles = this.tsne.append('g')
        .selectAll('circle')
        .data(faults).enter()
        .append('circle')
        .classed('hover', true)
        .attr('id', d => 'sample-' + d.id)
        .attr('class', d => 'circle-sample ' + d.class + ' label-' + d.label)
        .attr('r', gl.TSNE_R)
        .attr('cx', d => d.pos.x)
        .attr('cy', d => d.pos.y)
        .on('dblclick', d => this.showLabel(d))
        .on('click', d => this.addSample(d));
    circles.append('title')
        .text(d => 'busId: ' + d.id);
    
    const simulation = d3.forceSimulation(faults)
      .force('collision', d3.forceCollide(gl.TSNE_R - 2).iterations(2));
    let counter = 0;
    function ticked(){
        counter++;
        if (counter > 20) {
          simulation.stop();
        }
        circles.attr('cx', d => d.x)
            .attr('cy', d => d.y);
      }
     
    simulation.on('tick',ticked);

    // Lasso functions
    const lasso_start = () => {
        lasso.items()
            .attr('r', gl.TSNE_R) // reset size
            .classed('not_possible',true)
            .classed('selected',false);
    };

    const lasso_draw = () => {
    
        // Style the possible dots
        lasso.possibleItems()
            .classed('not_possible',false)
            .classed('possible',true);

        // Style the not possible dot
        lasso.notPossibleItems()
            .classed('not_possible',true)
            .classed('possible',false);
    };

    const lasso_end = () => {
        // Reset the color of all dots
        lasso.items()
            .classed('not_possible',false)
            .classed('possible',false);

        // Style the selected dots
        lasso.selectedItems()
            .classed('selected',true)
            .attr('r', gl.TSNE_LASSO_R);

        // Reset the style of the not selected dots
        lasso.notSelectedItems()
            .attr('r', gl.TSNE_R);

        this.sampleSelected(lasso.selectedItems());
    };
    
    const lasso = d3lasso.lasso()
        .closePathSelect(true)
        .closePathDistance(100)
        .items(circles)
        .targetArea(this.tsne)
        .on('start',lasso_start)
        .on('draw',lasso_draw)
        .on('end',lasso_end);
    
    this.tsne.call(lasso);
  }

  render() {
    return (
      <div className='tsne-div'>
        <svg className='tsne-panel'>
        </svg>
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
      </div>
    );
  }
}

Tsne.propTypes = {
  idx: PropTypes.number.isRequired,
  idy: PropTypes.number.isRequired,
};
const mapStateToProps = (state) => ({
  idx: state.second.idx,
  idy: state.second.idy,
  type: state.control.type,
});
const TsnePanel = connect(mapStateToProps, actions)(Tsne);
export default TsnePanel;
