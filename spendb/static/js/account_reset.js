
spendb.controller('AccountResetCtrl', ['$scope', '$modalInstance', '$window', '$location', '$http',
  function($scope, $modalInstance, $window, $location, $http) {

  $scope.data = {};
  $scope.res = {};
  $scope.sent = false;

  $scope.close = function() {
    $modalInstance.dismiss('ok');
  };

  $scope.send = function() {
    $scope.sent = true;
    $http.post('/api/3/reset', $scope.data).then(function(res) {
      $scope.res = res.data;
    }, function(res) {
      $scope.res = res.data;
      $scope.sent = false;
    });
  };

}]);
