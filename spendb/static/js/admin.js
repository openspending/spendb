
spendb.controller('AdminIndexCtrl', ['$scope', '$http', '$window', '$routeParams', 'dataset',
  function($scope, $http, $window, $routeParams, dataset, sources) {
  $scope.dataset = dataset;

}]);


spendb.controller('AdminMetadataCtrl', ['$scope', '$http', '$location', '$routeParams', 'reference', 'dataset', 'flash', 'validation',
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


spendb.controller('AdminModelCtrl', ['$scope', '$http', '$window', '$routeParams', 'dataset', 'data',
  function($scope, $http, $window, $routeParams, dataset, data) {
  var modelApi = dataset.api_url + '/model';
  
  $scope.dataset = dataset;
  $scope.structure = data.structure;
  $scope.model = data.model;

  // $scope.save = function(form) {
  //   var dfd = $http.post(modelApi, $scope.model);
  //   dfd.then(function(res) {
  //     $scope.model = res.data;
  //     flash.setMessage("Your changes have been saved!", "success");
  //   }, validation.handle(form));
  // };

}]);


spendb.controller('AdminRunCtrl', ['$scope', '$http', '$location', '$routeParams', 'dataset', 'run',
  function($scope, $http, $location, $routeParams, dataset, run) {

  $scope.dataset = dataset;
  $scope.run = run.data;

}]);
