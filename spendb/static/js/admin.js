
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


spendb.controller('AdminModelCtrl', ['$scope', '$http', '$window', '$timeout', '$rootScope', 'dataset', 'data',
  function($scope, $http, $window, $timeout, $rootScope, dataset, data) {
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

  var checkModel = function() {
    $scope.model.measures = $scope.model.measures || {};
    $scope.model.dimensions = $scope.model.dimensions || {};

    var fields = [];
    angular.forEach(data.structure.fields, function(v, k) {
      fields.push(k);
    });

    var usedFields = [];
    angular.forEach($scope.model.measures, function(v, k) {
      usedFields.push(k.column);
    });
    angular.forEach($scope.model.dimensions, function(v, k) {
      angular.forEach(k.attributes, function(v, k) {
        usedFields.push(k.column);
      });
    });

    //console.log(fields, usedFields);
  };

  checkModel();
  $scope.getCellClass = function(field, value) {
    var clazz = 'text';
    if (['integer', 'float', 'decimal'].indexOf(field.type) != -1) {
      clazz = 'numeric';
    }
    if (!value) { clazz += ' empty'; }
    return clazz;
  };

}]);


spendb.controller('AdminRunCtrl', ['$scope', '$http', '$location', '$routeParams', 'dataset', 'run',
  function($scope, $http, $location, $routeParams, dataset, run) {

  $scope.dataset = dataset;
  $scope.run = run.data;

}]);
