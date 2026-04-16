import request from '@/utils/request'

// 试算计算
export const trialCalculate = (data: any) => {
  return request({
    url: '/test-trial/trial-calculate',
    method: 'post',
    data
  });
};