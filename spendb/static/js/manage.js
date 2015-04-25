

var loadDataset = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      url = '/api/3/datasets/' + $route.current.params.dataset;
  $http.get(url).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


spendb.controller('DatasetManageCtrl', ['$scope', '$http', '$window', '$routeParams', 'dataset',
  function($scope, $http, $window, $routeParams, dataset) {

  $scope.dataset = dataset;

}]);


spendb.controller('DatasetMetaCtrl', ['$scope', '$http', '$location', '$routeParams', 'data', 'dataset', 'flash', 'validation',
  function($scope, $http, $location, $routeParams, data, dataset, flash, validation) {

  $scope.reference = {};
  $scope.dataset = dataset;

  data.get(function(reference) {
    $scope.reference = reference;
  });

  $scope.save = function(form) {
    var dfd = $http.post(datasetApi, $scope.dataset);
    dfd.then(function(res) {
      $scope.dataset = res.data;
      flash.setMessage("Your changes have been saved!", "success");
    }, validation.handle(form));
  };

}]);


spendb.controller('DatasetModelCtrl', ['$scope', '$http', '$window', '$routeParams', 'dataset',
  function($scope, $http, $window, $routeParams, dataset) {
  var fieldsApi = '/api/3/datasets/' + $routeParams.dataset + '/fields',
      modelApi = '/api/3/datasets/' + $routeParams.dataset + '/model';
  
  $scope.dataset = dataset;
  $scope.fields = {};
  $scope.model = {};

  $scope.save = function(form) {
    var dfd = $http.post(modelApi, $scope.model);
    dfd.then(function(res) {
      $scope.model = res.data;
      flash.setMessage("Your changes have been saved!", "success");
    }, validation.handle(form));
  };

  $http.get(fieldsApi).then(function(res) {
      $scope.fields = res.data;
  });

  $http.get(modelApi).then(function(res) {
      $scope.model = res.data;
  });

}]);

