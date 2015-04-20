
spendb.controller('DatasetManageCtrl', ['$scope', '$http', '$window', '$routeParams',
  function($scope, $http, $window, $routeParams) {
  var datasetApi = '/api/3/datasets/' + $routeParams.name;
  
  $scope.dataset = {};

  $http.get(datasetApi).then(function(res) {
      $scope.dataset = res.data;
  });

}]);


spendb.controller('DatasetMetaCtrl', ['$scope', '$http', '$location', '$routeParams', 'referenceData', 'flash', 'validation',
  function($scope, $http, $location, $routeParams, referenceData, flash, validation) {
  var datasetApi = '/api/3/datasets/' + $routeParams.name;

  $scope.reference = {};
  $scope.dataset = {};

  referenceData.get(function(reference) {
    $scope.reference = reference;
    // delay loading the dataset so that the selects are populated.
    $http.get(datasetApi).then(function(res) {
      $scope.dataset = res.data;

    });
  });

  $scope.save = function(form) {
    var dfd = $http.post(datasetApi, $scope.dataset);
    dfd.then(function(res) {
      $scope.dataset = res.data;
      flash.setMessage("Your changes have been saved!", "success");
    }, validation.handle(form));
  };

}]);


spendb.controller('DatasetModelCtrl', ['$scope', '$http', '$window', '$routeParams',
  function($scope, $http, $window, $routeParams) {
  var datasetApi = '/api/3/datasets/' + $routeParams.name,
      fieldsApi = '/api/3/datasets/' + $routeParams.name + '/fields',
      modelApi = '/api/3/datasets/' + $routeParams.name + '/model';
  
  $scope.dataset = {};
  $scope.fields = {};
  $scope.model = {};

  $scope.save = function(form) {
    var dfd = $http.post(modelApi, $scope.model);
    dfd.then(function(res) {
      $scope.model = res.data;
      flash.setMessage("Your changes have been saved!", "success");
    }, validation.handle(form));
  };

  $http.get(datasetApi).then(function(res) {
      $scope.dataset = res.data;
  });

  $http.get(fieldsApi).then(function(res) {
      $scope.fields = res.data;
  });

  $http.get(modelApi).then(function(res) {
      $scope.model = res.data;
  });

}]);

