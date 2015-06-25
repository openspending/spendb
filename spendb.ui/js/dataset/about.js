
spendb.controller('DatasetAboutCtrl', ['$scope', '$location', '$http', 'dataset', 'model', 'managers', 'config', 'reference',
    function($scope, $location, $http, dataset, model, managers, config, reference) {
  $scope.setTitle(dataset.label);
  $scope.dataset = dataset;
  $scope.managers = managers;
  $scope.model = model.model;
  $scope.config = config;
  $scope.sources = {};

  $http.get(dataset.api_url + '/sources').then(function(res) {
    $scope.sources = res.data;
  });

  $scope.getReferenceLabel = function(list, code) {
    for (var i in reference[list]) {
      var val = reference[list][i];
      if (val.code == code) {
        return val.label;
      }
    }
    return code;
  };
  
}]);
