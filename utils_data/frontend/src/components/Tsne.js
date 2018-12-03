import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import {select} from 'd3-selection';
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
      bus_dis: [],
      bus_index: []
    };
    this.idx = this.idy = -1;
    this.sampleColor = [];
    this.sampleLabel = [];
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
      let rateX = (gl.WIDTH - 10) / (xScale[1] - xScale[0]),
          rateY = (gl.HEIGHT - 10) / (yScale[1] - yScale[0]);
      const faults = [];
      data.pos.forEach((d, i) => {
        faults.push({
          'id': i,
          'label': null,
          'class': 'label-hide',
          'pos' : {
            'x': (d[0] - xScale[0]) * rateX + 5,
            'y': (d[1] - yScale[0]) * rateY + 5
          },
          'fault': data.fault[i]
        });
      });
      this.drawCircle(faults);
      this.setState({
        faults: faults,
        Number: faults.length,
        bus_dis: data.bus_dis.dis,
        bus_index: data.bus_index
      });
    });
  }

  componentDidMount() {
    this.tsne = select('.tsne-panel')
      .attr('width', gl.WIDTH)
      .attr('height', gl.HEIGHT);
  }

  UNSAFE_componentWillReceiveProps(nextProps) {
    console.log('next props!');
    if (nextProps.birchId != this.state.birch) {
      api.getBirch(nextProps.birchId).then(data => {
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
          birch: nextProps.birchId
        });
        this.drawCircle(faults);
      }); 
    }
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
    this.tsne.selectAll('.label-hide')
      .attr('fill', gl.NO_LABEL_COLOR);
    this.tsne.selectAll('.label-show')
        .attr('fill', gl.HIDEN_COLOR);
    const val = d.label;
    this.tsne.selectAll('.label-' + val)
        .attr('fill', gl.HIGHL_LIGHT_COLOR);
  }

  showDisMatrix(samples) {
    const sampleIds = [];
    const dis = [];
    const disSample = [];
    samples.each(v => {
      sampleIds.push(v.id);
    });
    const {bus_dis, bus_index} = this.state;
    const getMinDis = (a, b) => {
      const bus_a = [bus_index[a.i], bus_index[a.j]];
      const bus_b = [bus_index[b.i], bus_index[b.j]];
      return Math.min(...[bus_dis[bus_a[0]][bus_b[0]], bus_dis[bus_a[0]][bus_b[1]],
        bus_dis[bus_a[1]][bus_b[0]], bus_dis[bus_a[1]][bus_b[1]]]);
    };
    for (let i = 0; i < sampleIds.length; i++) {
      const tmp_dis = [];
      const fault_i = this.state.faults[sampleIds[i]].fault;
      for (let j = 0; j < sampleIds.length; j++) {
        const fault_j = this.state.faults[sampleIds[j]].fault;
        tmp_dis.push(getMinDis(fault_i, fault_j));
      }
      dis.push(tmp_dis);
      disSample.push({
        id: sampleIds[i],
        fault: this.state.faults[sampleIds[i]].fault
      });
    }
    this.props.ShowDisMatrix(dis, disSample);
  }

  drawCircle(faults) {
    console.log('draw Circle!');
    if (!this.tsne)
      return;
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

        this.showDisMatrix(lasso.selectedItems());
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

  addSample(d) {
    if (this.sampleId.includes(d.id)) {
      this.deleteSample(d);
      return;
    }
    const id = this.sampleId.length;
    this.sampleId.push(d.id);
    this.sampleColor.push(this.tsne.select('#sample-' + d.id).attr('fill'));
    this.sampleLabel.push(this.tsne.select('#sample-' + d.id).attr('class'));
    this.tsne.select('#sample-' + d.id)
        .attr('fill', gl.FAULT_CENTER_FILL[id])
        .attr('r', '7')
        .attr('class', 'sample-slect');
    this.props.AddSample([d.id], [d.fault]);
  }

  deleteSample(d) {
    const id = this.sampleId.indexOf(d.id);
    this.tsne.select('#sample-' + d.id)
        .attr('class', this.sampleLabel[id])
        .attr('fill', this.sampleColor[id])
        .attr('stroke', 'none')
        .attr('r', 4);
    this.sampleLabel.splice(id, 1);
    this.sampleColor.splice(id, 1);
    this.sampleId.splice(id, 1);
    this.props.DeleteSample([d.id]);
  }

  clear() {
    this.props.DeleteSample(this.sampleId);
    this.sampleColor = [];
    this.sampleId = [];
    this.sampleLabel = [];
    this.drawCircle(this.state.faults);
  }

  render() {
    console.log('render!');
    return (
      <div className='tsne-div'>
        <svg className='tsne-panel'>
        </svg>
        <button onClick={() => {this.clear();}}>Clear</button>
      </div>
    );
  }
}

Tsne.propTypes = {
  birchId: PropTypes.string.isRequired,
  idx: PropTypes.number.isRequired,
  idy: PropTypes.number.isRequired,
};
const mapStateToProps = (state) => ({
  birchId: state.control.birchId,
  idx: state.second.idx,
  idy: state.second.idy,
});
const TsnePanel = connect(mapStateToProps, actions)(Tsne);
export default TsnePanel;
