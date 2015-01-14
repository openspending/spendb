
var openspending = angular.module('openspending', ['ngCookies', 'ui.bootstrap', 'localytics.directives']);

openspending.controller('AppCtrl', ['$scope', '$location', '$http', '$cookies', '$window', '$sce',
  function($scope, $location, $http, $cookies, $window, $sce) {

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

}]);


openspending.factory('referenceData', ['$http', function($http) {
  var referenceData = $http.get('/api/3/reference');

  var getData = function(cb) {
    referenceData.then(function(res) {
      cb(res.data);
    });
  };

  return {'get': getData}
}]);



openspending.controller('DatasetNewCtrl', ['$scope', '$http', 'referenceData',
  function($scope, $http, referenceData) {
  
  $scope.reference = {};
  $scope.dataset = {'category': 'budget', 'territories': [], 'category': null};

  referenceData.get(function(reference) {
    $scope.reference = reference;
  });

  $scope.save = function() {
    var dfd = $http.post('/api/3/datasets', $scope.dataset);
    dfd.then(function(res) {
      console.log('NEW DATASET', res);
    }, function(fail) {
      console.log('FAILURE', fail);
    });
  };

}]);
