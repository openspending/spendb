
spendb.controller('DatasetDimensionEditCtrl', ['$scope', '$modalInstance', '$window', '$location', '$http', 'dimension',
  function($scope, $modalInstance, $window, $location, $http, dimension) {
  $scope.dimension = dimension;

  $scope.removeAttribute = function(attribute) {
    var idx = $scope.dimension.attributes.indexOf(attribute);
    if (idx != -1 || $scope.dimension.attributes.length > 1) {
      $scope.dimension.attributes.splice(idx, 1);
      if ($scope.dimension.label_attribute == attribute) {
        $scope.dimension.label_attribute = $scope.dimension.attributes[0];
      }
      if ($scope.dimension.key_attribute == attribute) {
        $scope.dimension.key_attribute = $scope.dimension.attributes[0];
      }
    }
  };

  $scope.update = function() {
    $modalInstance.dismiss('ok');
  };
}]);
