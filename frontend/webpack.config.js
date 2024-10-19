const path = require('path');

module.exports = {
    entry: './src/index.js',  // Entry point
    output: {
        path: path.resolve(__dirname, 'static/frontend'),  // Output path
        filename: 'bundle.js',  // Output filename
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,  // Handle .js and .jsx files
                exclude: /node_modules/,
                use: {
                    loader: 'babel-loader',
                    options: {
                        presets: ['@babel/preset-env', '@babel/preset-react'],
                    },
                },
            },
            {
                test: /\.css$/,  // Handle CSS imports
                use: ['style-loader', 'css-loader'],
            },
        ],
    },
    resolve: {
        extensions: ['.js', '.jsx'],  // Resolve .js and .jsx files
    },
    devtool: 'source-map',  // Helpful for debugging
    mode: 'development',  // Set to 'production' for production
};
