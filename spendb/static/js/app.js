
var spendb = angular.module('spendb', ['ngCookies', 'ngRoute', 'ngFileUpload', 'angularMoment', 'ui.bootstrap', 'localytics.directives']);


spendb.config(['$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {

  $routeProvider.when('/datasets/new', {
    templateUrl: 'new.html',
    controller: 'DatasetNewCtrl',
    resolve: {
      session: loadSession
    }
  });

  $routeProvider.when('/datasets/:dataset/manage', {
    templateUrl: 'manage.html',
    controller: 'DatasetManageCtrl',
    resolve: {
      dataset: loadDataset
    }
  });

  $routeProvider.when('/datasets/:dataset/runs/:run', {
    templateUrl: 'run.html',
    controller: 'RunViewCtrl',
    resolve: {
      dataset: loadDataset,
      run: loadRun
    }
  });

  $routeProvider.when('/datasets/:dataset/manage/meta', {
    templateUrl: 'meta.html',
    controller: 'DatasetMetaCtrl',
    resolve: {
      dataset: loadDataset,
      reference: loadReferenceData
    }
  });

  $routeProvider.when('/datasets/:dataset/manage/model', {
    templateUrl: 'model.html',
    controller: 'DatasetModelCtrl',
    resolve: {
      dataset: loadDataset
    }
  });

  // Router hack to enable plain old links. 
  angular.element("a").prop("target", "_self");
  $locationProvider.html5Mode(true);

}]);


spendb.controller('AppCtrl', ['$scope', '$location', '$http', '$cookies', '$window', '$sce', 'flash', 'session',
  function($scope, $location, $http, $cookies, $window, $sce, flash, session) {
  
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

  // Allow SCE escaping in the app
  $scope.trustAsHtml = function(text) {
    return $sce.trustAsHtml('' + text);
  };

  session.get(function(s) {
    $scope.session = s;
  });

}]);
