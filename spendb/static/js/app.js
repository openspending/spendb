angular.module('spendb.config', [])
    .constant('config', SPENDB_CONFIG);

var spendb = angular.module('spendb', ['spendb.config', 'ngCookies', 'ngRoute', 'duScroll', 'ngFileUpload',
                                       'angularMoment', 'ui.bootstrap', 'localytics.directives']);


spendb.config(['$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {

  $routeProvider.when('/datasets/new', {
    templateUrl: 'new.html',
    controller: 'NewCtrl',
    resolve: {
      session: loadSession,
      reference: loadReferenceData
    }
  });

  $routeProvider.when('/datasets/:dataset/admin/data', {
    templateUrl: 'admin/data.html',
    controller: 'AdminDataCtrl',
    resolve: {
      dataset: loadDataset
    }
  });

  $routeProvider.when('/datasets/:dataset/admin/runs/:run', {
    templateUrl: 'admin/run.html',
    controller: 'AdminRunCtrl',
    resolve: {
      dataset: loadDataset,
      run: loadRun
    }
  });

  $routeProvider.when('/datasets/:dataset/admin/metadata', {
    templateUrl: 'admin/metadata.html',
    controller: 'AdminMetadataCtrl',
    resolve: {
      dataset: loadDataset,
      reference: loadReferenceData,
      managers: loadManagers
    }
  });

  $routeProvider.when('/datasets/:dataset/admin/model', {
    templateUrl: 'admin/model.html',
    controller: 'AdminModelCtrl',
    resolve: {
      dataset: loadDataset,
      data: loadModel
    }
  });

  // Router hack to enable plain old links. 
  angular.element("a").prop("target", "_self");
  $locationProvider.html5Mode(true);

}]);


spendb.controller('AppCtrl', ['$scope', '$location', '$http', '$cookies', '$window', '$document', '$sce', 'flash', 'session', 'config',
  function($scope, $location, $http, $cookies, $window, $document, $sce, flash, session, config) {
  
  $scope.flash = flash;
  $scope.session = {};

  // EU cookie warning
  $scope.showCookieWarning = !$cookies.neelieCookie;

  $scope.hideCookieWarning = function() {
    $cookies.neelieCookie = true;
    $scope.showCookieWarning = !$cookies.neelieCookie;
  };

  // Language selector
  $scope.setLocale = function(locale) {
    $http.post('/set-locale', {'locale': locale}).then(function(res) {
      $window.location.reload();
    });
    return false;
  };

  $scope.setTitle = function(title) {
    angular.element('#page-title').html(title);
    angular.element('title').html(title + ' - ' + config.site_title);
  };

  // reset the page.
  $scope.resetScroll = function() {
    var elem = angular.element(document.getElementsByTagName('body'));
    $document.scrollToElement(elem, 0, 300);
  };


  // Allow SCE escaping in the app
  $scope.trustAsHtml = function(text) {
    return $sce.trustAsHtml('' + text);
  };

  session.get(function(s) {
    $scope.session = s;
  });

}]);
