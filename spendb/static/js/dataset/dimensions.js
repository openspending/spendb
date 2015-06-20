
spendb.controller('DatasetDimensionsCtrl', ['$scope', '$document', '$http', '$location', '$q', 'flash', 'validation', 'dataset', 'data',
  function($scope, $document, $http, $location, $q, flash, validation, dataset, data) {
  $scope.dataset = dataset;

  $scope.back = function() {
    $location.path('/datasets/' + dataset.name + '/model/measures');
  };

  $scope.canSave = function() {
    return true;
  };

  $scope.save = function() {
  };

}]);

