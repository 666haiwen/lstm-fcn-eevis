import React from 'react';
import PropTypes from 'prop-types';
import WaveLine from './Wavelines';
import { connect } from 'react-redux';
import * as d3 from 'd3';
import * as d3lasso from '../d3-lasso';
import * as gl from '../const';
import * as api from '../api';
import '../css/topology.css';
import * as actions from '../actions';

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
    this.busIds = [];
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

  mouseOver(d) {
    d3.select('#line-busId-' + d.id).attr('stroke', '#f44336');
    if (this.busIds.includes(d.id)) {
      d3.select('.corrcoef-svg').selectAll('g').classed('corrcoef-g-hidden', true);
      d3.select('.corrcoef-g-' + d.id).classed('corrcoef-g-hidden', false); 
    }
  }

  mouseOut(d) {
    d3.select('#line-busId-' + d.id).attr('stroke', 'black');
    d3.select('.corrcoef-svg').selectAll('g').classed('corrcoef-g-hidden', false);
  }

  drawCorrcoef(busIds) {
    const ids = [];
    busIds.each(v => ids.push(v.id));
    this.busIds = ids;
    this.props.ShowCorrcoef(ids);
  }

  drawTopology(graph) {
    if (!this.begin)
      return;
    this.begin = false;
    let simulation = d3.forceSimulation()
        .force('link', d3.forceLink().id(d => d.id))
        .force('charge', d3.forceManyBody().strength(-8))
        .force('center', d3.forceCenter(gl.TOPO_WIDTH / 2, gl.TOPO_HEIGHT / 2))
        .force('x', d3.forceX(gl.TOPO_WIDTH/2))
        .force('y', d3.forceY(gl.TOPO_HEIGHT/2));
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
        .attr('r', 3)
        .attr('id', d => 'busId-' + d.id)
        .on('click', d => this.addWaveLine(d))
        .on('mouseover', d => this.mouseOver(d))
        .on('mouseout', d => this.mouseOut(d))
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

    // this.topologySvg.call(
    //     d3.zoom()
    //         .scaleExtent([.1, 4])
    //         .on('zoom', () => { 
    //           link.attr('transform', d3.event.transform); 
    //           node.attr('transform', d3.event.transform);
    //         })
    // );
    
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
        
        this.drawCorrcoef(lasso.selectedItems());
    };
    
    const lasso = d3lasso.lasso()
        .closePathSelect(true)
        .closePathDistance(100)
        .items(node)
        .targetArea(this.topologySvg)
        .on('start',lasso_start)
        .on('draw',lasso_draw)
        .on('end',lasso_end);
    
    this.topologySvg.call(lasso);
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
    if (showLines.busId.includes(d.id)) {
      this.topologySvg.select('#busId-' + d.id)
        .classed('topo-bus-selected', false);
      const index = showLines.busId.indexOf(d.id);
      showLines.busId.splice(index, 1);
      showLines.vBase.splice(index, 1);
      showLines.data.splice(index, 1);
      this.setState({
        showLines: showLines
      });
      return;
    }
    
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
        />
      </div>
    );
  }
}

Topology.protoTypes = {
  sampleId: PropTypes.number.isRequired,
  fault: PropTypes.object.isRequired,
};
const TopologyPanel = connect(null, actions)(Topology);
export default TopologyPanel;
