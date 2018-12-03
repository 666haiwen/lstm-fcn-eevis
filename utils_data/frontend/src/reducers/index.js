import { combineReducers } from 'redux';
import second from './secondDetail';
import control from './control';

export default combineReducers({
  control,
  second
});
