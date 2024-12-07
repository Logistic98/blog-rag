const { defineConfig } = require('@vue/cli-service')
module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 28888,            // 指定端口号
    host: '0.0.0.0',        // 监听所有地址
    hot: false,             // 禁用热重载
    liveReload: false,      // 禁用实时重载
    allowedHosts: 'all',    // 允许所有主机访问
  }
})