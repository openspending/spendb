
spendb.controller('DatasetDimensionEditCtrl', ['$scope', '$modalInstance', '$window', '$location', '$http', 'dimension', 'dimensions',
  function($scope, $modalInstance, $window, $location, $http, dimension, dimensions) {
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

  var validSlug = function(obj) {
    if (!obj || !obj.name || obj.name.length < 2) {
      return false;
    }
    if (obj.name != getSlug(obj.name, '_')) {
      return false;
    }
    return true;
  };

  $scope.validAttributeSlug = function(obj) {
    if (!validSlug(obj)) {
      return false;
    }
    for (var i in $scope.dimension.attributes) {
      var attr = $scope.dimension.attributes[i];
      if (attr != obj && attr.name == obj.name) {
        return false;
      }
    }
    return true;
  };

  $scope.validDimensionSlug = function(obj) {
    obj.$invalidName = null;
    if (!validSlug(obj)) {
      return false;
    }
    for (var i in dimensions) {
      var dim = dimensions[i];
      if (dim != obj && dim.name == obj.name) {
        obj.$invalidName = 'A dimension with this name already exists.';
        return false;
      }
    }
    return true;
  };

  $scope.canUpdate = function() {
    if (!$scope.validDimensionSlug($scope.dimension)) {
      return false;
    }
    if (!$scope.validLabel($scope.dimension)) {
      return false;
    }
    for (var i in $scope.dimension.attributes) {
      var attr = $scope.dimension.attributes[i];
      if (!$scope.validAttributeSlug(attr)) {
        return false;
      }
      if (!$scope.validLabel(attr)) {
        return false;
      }
    }
    return true;
  };

  $scope.update = function() {
    if ($scope.canUpdate) {
      $modalInstance.close($scope.dimension);  
    }
  };

  $scope.close = function() {
    $modalInstance.dismiss('ok');
  };
}]);
