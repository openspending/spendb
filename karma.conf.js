// Karma configuration
// Generated on Mon Jun 22 2015 10:34:42 GMT+0200 (CEST)

module.exports = function(config) {
  config.set({

    // base path that will be used to resolve all patterns (eg. files, exclude)
    basePath: '',


    // frameworks to use
    // available frameworks: https://npmjs.org/browse/keyword/karma-adapter
    frameworks: ['mocha','chai', 'sinon-chai'],


    // list of files / patterns to load in the browser
    files: [
      'spendb.ui/vendor/moment/moment.js',
      'spendb.ui/vendor/d3/d3.js',
      'spendb.ui/vendor/d3-plugins/sankey/sankey.js',
      'spendb.ui/vendor/vega-lite/lib/vega.js',
      'spendb.ui/vendor/vega-lite/vega-lite.js',
      'spendb.ui/vendor/angular/angular.js',
      'spendb.ui/vendor/angular-route/angular-route.js',
      'spendb.ui/vendor/angular-moment/angular-moment.js',
      'spendb.ui/vendor/angular-scroll/angular-scroll.js',
      'spendb.ui/vendor/angular-cookies/angular-cookies.js',
      'spendb.ui/vendor/angular-ui-select/dist/select.js',
      'spendb.ui/vendor/angular-filter/dist/angular-filter.js',
      'spendb.ui/vendor/ng-file-upload/ng-file-upload-shim.js',
      'spendb.ui/vendor/ng-file-upload/ng-file-upload.js',
      'spendb.ui/vendor/angular-bootstrap/ui-bootstrap-tpls.min.js',
      'spendb.ui/vendor/angular-cubes/dist/angular-cubes.js',
      'node_modules/angular-mocks/angular-mocks.js',
      'spendb.ui/tests/js/helper.js',
      'spendb.ui/js/app.js',
      'spendb.ui/js/**/*.js',
      'spendb.ui/tests/js/**/*Spec.js'
    ],


    // list of files to exclude
    exclude: [
      '**/*.swp'
    ],


    // preprocess matching files before serving them to the browser
    // available preprocessors: https://npmjs.org/browse/keyword/karma-preprocessor
    preprocessors: {
    },


    // test results reporter to use
    // possible values: 'dots', 'progress'
    // available reporters: https://npmjs.org/browse/keyword/karma-reporter
    reporters: ['progress'],


    // web server port
    port: 9876,


    // enable / disable colors in the output (reporters and logs)
    colors: true,


    // level of logging
    // possible values: config.LOG_DISABLE || config.LOG_ERROR || config.LOG_WARN || config.LOG_INFO || config.LOG_DEBUG
    logLevel: config.LOG_INFO,


    // enable / disable watching file and executing tests whenever any file changes
    autoWatch: true,


    // start these browsers
    // available browser launchers: https://npmjs.org/browse/keyword/karma-launcher
    browsers: ['PhantomJS'],


    // Continuous Integration mode
    // if true, Karma captures browsers, runs the tests and exits
    singleRun: false
  });
};
