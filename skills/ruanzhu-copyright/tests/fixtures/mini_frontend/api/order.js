import request from '@/utils/request.js';

export function getOrderList(params) {
  return request.get('order/list', params);
}

export function createOrder(data) {
  return request.post('order/create', data);
}
