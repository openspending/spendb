
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

  $scope.breakSlugLink = function(obj) {
    obj.slug_linked = false;
  };

  $scope.updateSlug = function(obj) {
    if (obj.slug_linked) {
      obj.name = getSlug(obj.label, '_');
    }
  };

  $scope.validLabel = function(obj) {
    if (!obj || !obj.label || obj.label.length < 2) {
      return false;
    }
    return true;
  };

  $scope.update = function() {
    $modalInstance.dismiss('ok');
  };
}]);
