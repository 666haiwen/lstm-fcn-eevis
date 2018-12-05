import $ from 'jquery';
import * as Const from '../const';

const ajax = (options, func=$.ajax) => {
  return new Promise((resolve, reject) => {
    func(options).done(resolve).fail(reject);
  });
};

const getJson = (options) => ajax(options, $.getJson);

export const getFaultMark = () => {
  return getJson({
    url: Const.HOSTNAME+ 'api/faultmark',
  });
};

export const getTsne = () => {
  return getJson({
    url: Const.HOSTNAME + 'api/tsne',
  });
};

export const getBirch = (v) => {
  return getJson({
    url: Const.HOSTNAME + 'api/birch',
    data: {
      name: 'birch-' + v + '.json'
    }
  });
};

export const getForceInfo = () => {
  return getJson({
    url: Const.HOSTNAME + 'api/forceInfo'
  });
};

export const getBusData = (sampleId, busId) => {
  return getJson({
    url: Const.HOSTNAME + 'api/busData',
    data: {
      sampleId: sampleId,
      busId: busId
    }
  });
};

export const getSampleDis = (sampleId) => {
  return getJson({
    url: Const.HOSTNAME + 'api/sampleDis',
    data: {
      sampleId: sampleId,
    }
  });
};

export const getBusDistance = (idx, idy) => {
  return getJson({
    url: Const.HOSTNAME + 'api/busDistance',
    data: {
      idx: idx,
      idy: idy
    }
  });
};

export const getCorrcoef = (sampleId, busIds) => {
  return getJson({
    url: Const.HOSTNAME + 'api/corrcoef',
    data: {
      sampleId: sampleId,
      busIds: busIds
    }
  });
};
