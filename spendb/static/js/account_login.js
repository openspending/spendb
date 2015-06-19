
spendb.controller('AccountLoginCtrl', ['$scope', '$document', '$http', '$location', 'validation', 'session',
  function($scope, $document, $http, $location, validation, session) {
  $scope.setTitle("Login and registration");

  $scope.credentials = {};
  $scope.account = {};

  $scope.login = function(form) {
    $http.post('/api/3/sessions/login', $scope.credentials).then(function(res) {
      $location.path('/');
    }, validation.handle(form));
  };

  $scope.register = function(form) {
    $http.post('/api/3/account', $scope.account).then(function(res) {
      // session.
      $location.path('/');
    }, validation.handle(form));
  };

}]);
