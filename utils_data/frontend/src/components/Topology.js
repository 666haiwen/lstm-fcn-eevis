import React from 'react';
import * as $ from 'jquery';
import PropTypes from 'prop-types';
import WaveLine from './Wavelines';
import { connect } from 'react-redux';
import * as d3 from 'd3';
import * as gl from '../const';
import * as api from '../api';
import * as actions from '../actions';

class Topology extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      nodes: [],
      links: [],
      bus_ids: [],
      showLines: []
    };
    this.begin = false;
    this.sampleId = [];
    this.faults = []; 
    this.selectSample = -1;
    api.getForceInfo().then(d => {
      // console.log(d['data'][0][3]);
      this.begin = true;
      this.setState({
        'nodes': d['busInfo'],
        'links': d['edgeInfo'],
        'bus_ids': d['bus_vaild'],
      });
    });
  }

  componentDidMount() {
    this.topologySvg = d3.select('.topology-panel');
    this.sampleSelector = d3.select('.sample-selector');
    this.sampleValue = () => $('.sample-selector').val();
  }

  drawTopology(graph) {
    if (!this.begin)
      return;
    this.begin = false;
    let simulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id))
        .force('charge', d3.forceManyBody().strength(-30))
        .force('center', d3.forceCenter(gl.TOPO_WIDTH / 2, gl.TOPO_HEIGHT / 2))
        .force('x', d3.forceX(gl.TOPO_WIDTH / 2).strength(1))
        .force('y', d3.forceY(gl.TOPO_HEIGHT / 2).strength(1));
    let link = this.topologySvg.append('g')
        .attr('class', 'links-line')
      .selectAll('line')
      .data(graph.links)
      .enter().append('line');
    let node = this.topologySvg.append('g')
        .attr('class', 'nodes-circle')
      .selectAll('circle')
      .data(graph.nodes)
      .enter().append('circle')
        .attr('r', 2.5)
        .attr('id', d => 'busId-' + d.id)
        .on('click', d => this.addWaveLine(d))
        .call(d3.drag()
            .on('start', dragstarted)
            .on('drag', dragged)
            .on('end', dragended));
    node.append('title')
        .text(d => 'busId: ' + d.id + ' vBase: ' + d.vBase);
    simulation.nodes(graph.nodes)
        .on('tick', ticked);
    const forceLink = d3.forceLink()
      .id(d => d.id)
      .links(graph.links)
      .distance(2);
      // .strength(1);
    simulation.force('link', forceLink);

    this.topologySvg.call(
        d3.zoom()
            .scaleExtent([.1, 4])
            .on('zoom', () => { 
              link.attr('transform', d3.event.transform); 
              node.attr('transform', d3.event.transform);
            })
    );

    function ticked() {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('cx', d => d.x)
        .attr('cy', d => d.y);
    }
    function dragstarted(d) {
      if (!d3.event.active) simulation.alphaTarget(0.03).restart();
      d.fx = d.x;
      d.fy = d.y;
    }
    function dragged(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
    }    
    function dragended(d) {
      if (!d3.event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }
  }

  UNSAFE_componentWillReceiveProps(nextProps) {
    if (nextProps.type == 'ADD') 
      this.addSample(nextProps);
    else if (nextProps.type == 'DELETE')
      this.deleteSample(nextProps);
  }

  addSample(nextProps) {
    if (this.sampleId.includes(nextProps.newSample[0]))
      return;
    nextProps.newSample.forEach((v, i) => {
      const id = Math.min(this.sampleId.length, gl.FAULT_CENTER_FILL.length);
      this.sampleSelector.append('option')
        .attr('value', v)
        .style('background', gl.FAULT_CENTER_FILL[id])
        .text('Sample-' + v);
      this.sampleId.push(v);
      this.faults.push(nextProps.fault[i]);
      d3.select('#busId-' + nextProps.fault[i]['i'])
          .attr('fill', gl.FAULT_CENTER_FILL[id])
          .attr('class', 'faultcenter');
      d3.select('#busId-' + nextProps.fault[i]['j'])
          .attr('fill', gl.FAULT_CENTER_FILL[id])
          .attr('class', 'faultcenter');
    });
  }

  deleteSample(nextProps) {
    if (!this.sampleId.includes(nextProps.newSample[0]))
      return;

    for (let i = 0; i < nextProps.newSample.length; i++) {
      const v = nextProps.newSample[i];
      const id = this.sampleId.indexOf(v);
      d3.select('#busId-' + this.faults[id]['i'])
          .attr('class', 'nodes-circle');
      d3.select('#busId-' + this.faults[id]['j'])
          .attr('class', 'nodes-circle');
      this.faults.splice(id, 1);
      this.sampleId.splice(id, 1);
    }
  }

  addWaveLine(d) {
    console.log(d);
    const showLines = this.state.showLines;

    api.getBusData(this.sampleValue(), d.id).then(data => {
      showLines.push({
        sampleId: this.sampleValue(),
        busId: d.id,
        vBase: d.vBase,
        data: data.data
      });
      this.setState({
        showLines: showLines
      });
    });
  }
  // getFau
  saveTopo() {
    const res = {
      circle: [],
      lines: []
    };
    const busId = [];
    this.topologySvg.selectAll('circle').each(d => {
      res.circle.push({
        id: d.id,
        rx: d.rx,
        ry: d.ry,
        vBase: d.vBase
      });
      busId.push(d.id);
    });
    this.topologySvg.selectAll('line').each(d => {
      console.log(d);
      res.lines.push({
        x: busId.indexOf(d.source),
        y: busId.indexOf(d.target)
      });
    });
    
  }

  render() {
    return (
      <div>
        <div id='topology-div'>
          <svg className='topology-panel' width={gl.TOPO_WIDTH} height={gl.TOPO_HEIGHT}>
            {this.drawTopology(this.state)}
          </svg>
          <select className='sample-selector'>
            <option value="-1">Select diffierent Sample</option>
          </select>
          <button onClick={() => this.saveTopo()}>Save</button>
        </div>
        <div className='wavelines-div'>
          {this.state.showLines.map((d, i) => 
            <WaveLine
              key={i}
              number={i}
              sampleId={d.sampleId}
              busId={d.busId}
              vBase={d.vBase}
              data={d.data}
              onClick = {(i) => {console.log(i);}}
            />
          )}
        </div>
      </div>
    );
  }
}

Topology.protoTypes = {
  newSample: PropTypes.array.isRequired,
};
const mapStateToProps = (state) => ({
  newSample: state.control.newSample,
  fault: state.control.fault,
  type: state.control.sampleType
});
const TopologyPanel = connect(mapStateToProps, actions)(Topology);
export default TopologyPanel;
