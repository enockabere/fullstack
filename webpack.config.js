const path = require("path");
const CopyWebpackPlugin = require("copy-webpack-plugin");

module.exports = {
  entry: "./frontend/src/index.js", // Entry point for your React code
  output: {
    path: path.resolve(__dirname, "frontend/static/frontend"), // Output directory for bundle.js
    filename: "bundle.js", // Name of the output file
  },
  watchOptions: {
    ignored: /node_modules/,
    aggregateTimeout: 300,
    poll: 1000,
  },
  module: {
    rules: [
      {
        test: /\.js$/, // Test for .js files
        exclude: /node_modules/, // Exclude node_modules
        use: {
          loader: "babel-loader",
          options: {
            presets: ["@babel/preset-env", "@babel/preset-react"], // Use these Babel presets
          },
        },
      },
      {
        test: /\.css$/, // For handling CSS
        use: ["style-loader", "css-loader"],
      },
      {
        test: /\.(png|jpe?g|gif|svg)$/i,
        type: "asset/resource",
        generator: {
          filename: "static/img/[name][ext]",
        },
      },
    ],
  },
  resolve: {
    extensions: [".js", ".jsx"], // Resolve these file types
  },
  mode: "development", // You can switch to 'production' for production builds
  plugins: [
    new CopyWebpackPlugin({
      patterns: [
        { from: path.resolve(__dirname, "frontend/static"), to: "static" },
      ],
    }),
  ],
};
