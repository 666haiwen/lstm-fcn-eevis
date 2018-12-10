import React from 'react';
import PropTypes from 'prop-types';
import WaveLine from './Wavelines';
import Corrcoef from './Corrcoef';
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
      busIds: [],//selected busIds
      showLines: {
        busId: [],
        data: [],
        vBase: [],
      },
      order: [],
      disOrder: -1,
      type: 'SAMPLE-TOPO'
    };
    this.begin = false;
    this.selectedIds = [];
    this.sampleId = [];
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
    this.checkbox = d3.select('#select-sample-checkbox');
    this.filed = [
      d3.select('#first-field-checkbox'),
      d3.select('#second-field-checkbox'),
      d3.select('#third-field-checkbox'),
      d3.select('#fourth-field-checkbox'),
      d3.select('#fifth-field-checkbox'),
    ];
  }

  mouseOver(d) {
    d3.select('#line-busId-' + d.id).classed('high-light-path', true);
    if (this.state.busIds.includes(d.id)) {
      d3.select('.corrcoef-svg').selectAll('g').selectAll('g').classed('corrcoef-g-hidden', true);
      d3.select('.corrcoef-svg').selectAll('.corrcoef-g-' + d.id).classed('corrcoef-g-hidden', false); 
    }
  }

  mouseOut(d) {
    d3.select('#line-busId-' + d.id).classed('high-light-path', false);
    d3.select('.corrcoef-svg').selectAll('g').classed('corrcoef-g-hidden', false);
  }

  drawCorrcoef(selected) {
    const ids = [];
    const busIds = this.state.busIds;
    this.selectedIds.forEach(v => {
      const index = busIds.indexOf(v);
      busIds.splice(index, 1);
    });
    selected.each(v => {
      ids.push(v.id);
      if (!busIds.includes(v.id)) {
        busIds.push(v.id);
      }
    });
    this.selectedIds = ids;
    this.setState({
      busIds: busIds
    });
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
    this.setState({
      // busIds: [],
      showLines: {
        busId: [],
        data: [],
        vBase: [],
      },
    });
  }

  addWaveLine(d) {
    if (this.state.type == 'TOPO-SAMPLE') {
      return;
    }
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

  selectingSample() {
    if (this.checkbox.node().checked) {
      this.setState({
        type: 'TOPO-SAMPLE'
      });
      this.props.ChangeType('TOPO-SAMPLE');
    }
    else {
      this.setState({
        type: 'SAMPLE-TOPO'
      });
      this.props.ChangeType('SAMPLE-TOPO');
    }
  }

  getFieldData(id) {
    const showLines = this.state.showLines;
    // clean
    for (let i = 0; i <= this.state.disOrder; i++) {
      this.state.order[i].forEach(v => {
        this.topologySvg.select('#busId-' + v)
            // .classed('topo-bus-selected', false)
            .attr('fill', '#4157f580');
            // .classed(gl.ORDERCLASS[id] + '-node', false);
        const index = showLines.busId.indexOf(v);
        const i = this.state.busIds.indexOf(v);
        showLines.busId.splice(index, 1);
        showLines.vBase.splice(index, 1);
        showLines.data.splice(index, 1);
        this.state.busIds.splice(i, 1);
      });
    }
    // re-get value
    api.getBusField(this.sampleId, id).then(data => {
      data.busId.forEach((v, i)=> {
        if (!showLines.busId.includes(v)) {
          showLines.data.push(data.data[i]);
          showLines.busId.push(v);
          showLines.vBase.push(data.vBase[i]);
        }
        if (!this.state.busIds.includes(v)) {
          this.state.busIds.push(v);
        }
      });
      for (let _i = 0; _i < data.field.length; _i++) {
        data.field[_i].forEach(v => {
          this.topologySvg.select('#busId-' + v)
            .attr('fill', gl.FIELD_COLOR(gl.FIELD_LINEAR(_i)));
        });
      }
      this.setState({
        order: data.field,
        showLines: showLines,
        disOrder: data.field.length - 1
      });
    });
  }

  orderChange(v) {
    const disOrder = this.state.disOrder + v;
    if (disOrder < 0 || disOrder > 10)
      return;
    this.getFieldData(disOrder);
  }

  render() {
    const showLines = this.state.showLines;
    let waveLines = <div></div>;
    if (this.sampleId.length == 1 && this.state.type == 'SAMPLE-TOPO') {
      waveLines = <WaveLine
                    sampleId={this.sampleId[0]}
                    busId={showLines.busId}
                    vBase={showLines.vBase}
                    data={showLines.data}
                    order={this.state.order}
                  />;
    }
    const corrcoef = <Corrcoef sampleId={this.props.sampleId} busIds={this.state.busIds} />;      

    return (
      <div className='topology-div'>
        <div className='topology-panel'>
          <svg className='topology-svg' width={gl.TOPO_WIDTH} height={gl.TOPO_HEIGHT}>
            {this.drawTopology(this.state)}
          </svg>
          <label>
            <input id='select-sample-checkbox' type='checkbox' onChange={() => this.selectingSample()} />
              <span>Enable Selecting Samples</span>
          </label>
          <div>
            <p>The order distance: {this.state.disOrder}</p>
            <button className='up-btn' onClick={()=>this.orderChange(1)}>up</button>
            <button className='down-btn' onClick={()=>this.orderChange(-1)}>down</button>
          </div>
        </div>
        {waveLines}
        {corrcoef}
      </div>
    );
  }
}

Topology.protoTypes = {
  sampleId: PropTypes.array.isRequired,
  fault: PropTypes.object.isRequired,
};
const TopologyPanel = connect(null, actions)(Topology);
export default TopologyPanel;
