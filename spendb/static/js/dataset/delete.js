
spendb.controller('DatasetDeleteCtrl', ['$scope', '$modalInstance', '$window', '$location', '$http', 'dataset',
  function($scope, $modalInstance, $window, $location, $http, dataset) {
  $scope.dataset = dataset;

  $scope.close = function() {
    $modalInstance.dismiss('cancel');
  };

  $scope.delete = function() {
    $http.delete($scope.dataset.api_url).error(function(res) {
      $location.path('/datasets');
      $modalInstance.dismiss('ok');
      $window.location.reload();
    });
  };
}]);
