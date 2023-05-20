//const path = require('path');

const entries = require('react-app-rewire-multiple-entry')([
    {
        entry: 'src/accounts/accounts.js',
        template: 'public/accounts.html',
        outPath: '/accounts.html',
        library: 'accounts'
    },
    {
        entry: 'src/laozy/laozy.js',
        template: 'public/laozy.html',
        outPath: '/laozy.html'
    },
    {
        entry: 'src/index.js',
    },
])

module.exports = {
    webpack: function(config, env) {
        
        config.output.library = 'laozy';
        config.output.libraryExport = 'default';
        config.output.libraryTarget = 'umd';
        config.output.filename = 'laozy-[chunkhash].js';
        
        entries.addMultiEntry(config);
        return config;
    },
    
    devServer: function (configFunction) {
        return function(proxy, allowedHost) {
            const config = configFunction(proxy, allowedHost);
            //https://github.com/chimurai/http-proxy-middleware/issues/371
            config.compress = false;
            return config;
        }
    }
}