import * as d3 from 'd3';


export const WIDTH = 850, HEIGHT = 1150, TRANSLATE_X = 50, TRANSLATE_Y = 50,
             LABEL_THREHOLD = 3, HIGHL_LIGHT_COLOR= '#2196F3';
export const TSNE_R = 5, TSNE_LASSO_R = 7;

export const TOPO_WIDTH = 850, TOPO_HEIGHT = 800;
export const FIELD_COLOR = d3.interpolate(d3.color('#ff5722'), d3.color('#fff'));
export const FIELD_LINEAR = d3.scaleLinear().domain([0, 10]).range([0, 1]);
export const ORDERCLASS= ['first-order', 'second-order', 'third-order', 'fourth-order', 'fifth-order'];
export const SHOW_COLOR = '#1a1a1a1a', HIDEN_COLOR = '#80808060', NO_LABEL_COLOR = '#80808010';

export const DIS_MATRIX_LENGTH = 40, DIS_MAX = 1.4902337025193395, DIS_INF = 100000;
export const FAULT_CENTER_FILL = ['bisque', '#badfff', '#8bc34a', '#ffeb3b'];
export const FAULT_CENTER_STROKE = '#ff5722';

export const WAVELINE_WIDTH = 2300, WAVELINE_TRANS = 7, WAVELINE_HEIGHT = 250;
export const DST_FILE = 'file://G:/KDD-EEVIS/original_sample/data/';
export const HOSTNAME = window.location.origin + '/';