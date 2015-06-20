
spendb.controller('DatasetMeasuresCtrl', ['$scope', '$document', '$http', '$location', '$q', 'flash', 'validation', 'dataset', 'data',
  function($scope, $document, $http, $location, $q, flash, validation, dataset, data) {
  $scope.dataset = dataset;

  $scope.save = function() {
    validation.clear($scope.forms.dataset);
    dfd.then(function(res) {
      
    }, validation.handle($scope.forms.dataset));
  };

  $scope.back = function() {
    $location.path('/datasets/' + dataset.name + '/sources');
  };

}]);

