const config = {
  baseUrl: 'https://example.com',
  // 敏感信息测试：应被过滤
  JWT_SECRET=super-secret-key-abcdefgh,
};

export default function request(options) {
  return Promise.resolve({ code: 0, data: {} });
}
