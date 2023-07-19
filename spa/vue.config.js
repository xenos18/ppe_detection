const {defineConfig} = require('@vue/cli-service')
const path = require("path");


module.exports = defineConfig({
    transpileDependencies: true,
    configureWebpack: {
        resolve: {
            alias: {
                '@': path.resolve(__dirname, './src'),
                'module': path.resolve(__dirname, './src/modules'),
            },
        },
    },
    pages: {
        index: {
            // entry for the page
            entry: 'src/main.js',
            // the source template
            template: 'public/index.html',
            // output as dist/index.html
            filename: 'index.html',
            // template title tag needs to be <title><%= htmlWebpackPlugin.options.title %></title>
            title: 'Платформа кастомизации вещей IDICLO',
            // chunks to include on this page, by default includes
            // extracted common chunks and vendor chunks.
            chunks: ['chunk-vendors', 'chunk-common', 'index']
        },


    }
})