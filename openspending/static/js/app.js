
var openspending = angular.module('openspending', ['ngCookies', 'ui.bootstrap']);

openspending.controller('AppCtrl', ['$scope', '$location', '$http', '$cookies', '$window',
  function($scope, $location, $http, $cookies, $window) {

    // EU cookie warning
    $scope.showCookieWarning = !$cookies.neelieCookie;

    $scope.hideCookieWarning = function() {
      $cookies.neelieCookie = true;
      $scope.showCookieWarning = !$cookies.neelieCookie;
    }

    // Language selector
    $scope.setLocale = function(locale) {
      $http.post('/set-locale', {'locale': locale}).then(function(res) {
        $window.location.reload();
      });
      return false;
    }

}]);


openspending.controller('DatasetNewCtrl', ['$scope', '$http',
  function($scope, $http) {


}]);
