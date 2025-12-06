const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  app.use(
    '/api',
    createProxyMiddleware({
      // Always use the backend service name inside Docker
      target: 'http://backend:3500',
      changeOrigin: true,
    })
  );
};
