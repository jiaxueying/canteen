export const backendUrl = 'http://cal.hanlh.com:8000';

export const request = function(url, method, data) {
  return uni.request({
    url: backendUrl + url,
    method: method,
    data: data,
    header: {
      Authorization: 'Token ' + uni.getStorageSync('token'),
    },
  });
};

export default {
  backendUrl,
  request,
};
