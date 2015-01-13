
var openspending = angular.module('openspending', ['ngCookies']);

openspending.controller('AppCtrl', ['$scope', '$location', '$http', '$cookies',
  function($scope, $location, $http, $cookies) {

    // EU cookie warning.
    $scope.showCookieWarning = !$cookies.kroesCookie;

    $scope.hideCookieWarning = function() {
      $cookies.kroesCookie = true;
      $scope.showCookieWarning = !$cookies.kroesCookie;
    }



}]);
