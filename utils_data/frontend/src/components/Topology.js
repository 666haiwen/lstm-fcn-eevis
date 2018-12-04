import React from 'react';
import PropTypes from 'prop-types';
import WaveLine from './Wavelines';
import * as d3 from 'd3';
import * as gl from '../const';
import * as api from '../api';
import '../css/topology.css';
// import * as actions from '../actions';

class Topology extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      nodes: [],
      links: [],
      bus_ids: [],
      showLines: {
        busId: [],
        data: [],
        vBase: [],
      }
    };
    this.begin = false;
    this.sampleId = -1;
    api.getForceInfo().then(d => {
      this.begin = true;
      this.setState({
        'nodes': d['busInfo'],
        'links': d['edgeInfo'],
        'bus_ids': d['bus_vaild'],
      });
    });
  }

  componentDidMount() {
    this.topologySvg = d3.select('.topology-svg');
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
    const {fault} = nextProps;
    this.sampleId = nextProps.sampleId;
    this.topologySvg.selectAll('circle')
        .classed('faultcenter', false);
    d3.select('#busId-' + fault['i'])
        .classed('faultcenter', true);
    d3.select('#busId-' + fault['j'])
        .classed('faultcenter', true);
  }

  addWaveLine(d) {
    const showLines = this.state.showLines;
    if (showLines.busId.includes(d.id))
      return;
    
    this.topologySvg.selectAll('circle')
      .classed('topo-bus-selected', false); 
    api.getBusData(this.props.sampleId, d.id).then(data => {
      showLines.data.push(data.data);
      showLines.vBase.push(d.vBase);
      showLines.busId.push(d.id);
      showLines.busId.forEach(id => {
        this.topologySvg.select('#busId-' + id)
          .classed('topo-bus-selected', true);
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
      res.lines.push({
        x: busId.indexOf(d.source),
        y: busId.indexOf(d.target)
      });
    });
    
  }

  render() {
    const showLines = this.state.showLines;
    return (
      <div className='topology-div'>
        <div className='topology-panel'>
          <svg className='topology-svg' width={gl.TOPO_WIDTH} height={gl.TOPO_HEIGHT}>
            {this.drawTopology(this.state)}
          </svg>
        </div>
        <WaveLine
          sampleId={this.sampleId}
          busId={showLines.busId}
          vBase={showLines.vBase}
          data={showLines.data}
          onClick = {(i) => {console.log(i);}}
        />
      </div>
    );
  }
}

Topology.protoTypes = {
  sampleId: PropTypes.number.isRequired,
  fault: PropTypes.object.isRequired,
};
// const TopologyPanel = connect(mapStateToProps, actions)(Topology);
export default Topology;
