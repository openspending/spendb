

spendb.controller('DatasetIndexCtrl', ['$scope', '$sce', 'datasets', function($scope, $sce, datasets) {
  $scope.setTitle('Datasets in our store');
  $scope.datasets = datasets;
}]);
