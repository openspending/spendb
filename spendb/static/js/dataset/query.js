
spendb.controller('DatasetQueryCtrl', ['$scope', '$location', 'dataset', function($scope, $location, dataset) {
  $scope.setTitle(dataset.label);
  $scope.dataset = dataset;

  if (!dataset.has_model) {
    $location.path('/datasets/' + dataset.name + '/about');
    $location.search({});
  }
  
}]);
