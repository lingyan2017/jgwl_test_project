import request from '@/utils/request'

export const testPayment = (data: any) => {
  return request({
    url: '/payment-test/test-payment',
    method: 'post',
    data
  });
};