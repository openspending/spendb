

var loadDataset = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      url = '/api/3/datasets/' + $route.current.params.dataset;
  $http.get(url).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


var loadReferenceData = ['$q', 'data', function($q, wdata) {
  var dfd = $q.defer();
  data.get(function(rd) {
    dfd.resolve(rd);
  });
  return dfd.promise;
}];


spendb.controller('DatasetManageCtrl', ['$scope', '$http', '$window', '$routeParams', 'dataset',
  function($scope, $http, $window, $routeParams, dataset) {

  $scope.dataset = dataset;

}]);


spendb.controller('DatasetMetaCtrl', ['$scope', '$http', '$location', '$routeParams', 'reference', 'dataset', 'flash', 'validation',
  function($scope, $http, $location, $routeParams, reference, dataset, flash, validation) {

  $scope.reference = reference;
  $scope.dataset = dataset;

  $scope.save = function(form) {
    var dfd = $http.post(dataset.api_url, $scope.dataset);
    dfd.then(function(res) {
      $scope.dataset = res.data;
      flash.setMessage("Your changes have been saved!", "success");
    }, validation.handle(form));
  };

}]);


spendb.controller('DatasetModelCtrl', ['$scope', '$http', '$window', '$routeParams', 'dataset',
  function($scope, $http, $window, $routeParams, dataset) {
  var fieldsApi = dataset.api_url + '/fields',
      modelApi = dataset.api_url + '/model';
  
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

