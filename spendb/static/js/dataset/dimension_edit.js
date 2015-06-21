
spendb.controller('DatasetDimensionEditCtrl', ['$scope', '$modalInstance', '$window', '$location', '$http', 'dimension',
  function($scope, $modalInstance, $window, $location, $http, dimension) {
  $scope.dimension = dimension;

  $scope.update = function() {
    $modalInstance.dismiss('ok');
  };
}]);
