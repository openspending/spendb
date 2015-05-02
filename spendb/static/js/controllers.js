

spendb.controller('NewCtrl', ['$scope', '$http', '$location', 'reference', 'validation', 'session',
  function($scope, $http, $location, reference, validation, session) {

  $scope.dataset = {'category': 'budget', 'territories': []};
  $scope.reference = reference;
  $scope.session = session;
  $scope.afterUpload = [];

  $scope.hasDataset = function() {
    return session.logged_in && angular.isDefined($scope.dataset.api_url);
  };

  $scope.hasUpload = function() {
    return $scope.hasDataset() && $scope.afterUpload.length > 0;
  };

  $scope.createDataset = function(form) {
    validation.clear(form);
    $http.post('/api/3/datasets', $scope.dataset).then(function(res) {
      $scope.dataset = res.data;
    }, validation.handle(form));
  };

  $scope.createUpload = function() {
    if (!$scope.hasDataset()) return;
    if ($scope.hasUpload()) return;
    $scope.afterUpload.push($scope.dataset);
  };

  $scope.saveDataset = function(form) {
    if (!$scope.hasDataset()) return;
    validation.clear(form);
    $http.post($scope.dataset.api_url, $scope.dataset).then(function(res) {
      $location.path('/datasets/' + $scope.dataset.name + '/manage')
    }, validation.handle(form));
  };

}]);


spendb.controller('DatasetManageCtrl', ['$scope', '$http', '$window', '$routeParams', 'dataset',
  function($scope, $http, $window, $routeParams, dataset, sources) {
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


spendb.controller('RunViewCtrl', ['$scope', '$http', '$location', '$routeParams', 'dataset', 'run',
  function($scope, $http, $location, $routeParams, dataset, run) {

  $scope.dataset = dataset;
  $scope.run = run.data;

}]);
