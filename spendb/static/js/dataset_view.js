
spendb.controller('DatasetViewCtrl', ['$scope', '$location', 'dataset', function($scope, $location, dataset) {
  $scope.setTitle(dataset.label);
  $scope.dataset = dataset;
  
}]);
