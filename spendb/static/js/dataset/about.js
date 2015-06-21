
spendb.controller('DatasetAboutCtrl', ['$scope', '$location', 'dataset', 'model', 'managers', 'config',
    function($scope, $location, dataset, model, managers, config) {
  $scope.setTitle(dataset.label);
  $scope.dataset = dataset;
  $scope.managers = managers;
  $scope.model = model.model;
  $scope.config = config;
  
}]);
