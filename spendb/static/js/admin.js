
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
  $scope.samples = data.structure.samples;

  $scope.save = function(form) {
    var model = columnsToModel($scope.columns);
    var dfd = $http.post(modelApi, model);
    dfd.then(function(res) {
      $scope.columns = modelToColumns(res.data);
      flash.setMessage("Your changes have been saved!", "success");
    }, validation.handle(form));
  };

  var modelToColumns = function(model) {
    var columns = [], usedFields = [];
    model.measures = model.measures || {};
    model.dimensions = model.dimensions || {};

    console.log(model);

    var pushColumn = function(data, concept) {
      data.concept = concept;
      usedFields.push(data.column);
      columns.push(data);
    };

    for (var measure in model.measures) {
      var m = model.measures[measure];
      m.name = measure;
      pushColumn(m, 'measure');
    }

    for (var dim in model.dimensions) {
      var dimdata = model.dimensions[dim];
      dimdata.name = dim;
      for (var attr in dimdata.attributes) {
        var a = dimdata.attributes[attr];
        a.name = attr;
        a.dimension = dimdata;
        pushColumn(a, 'attribute');
      }
    }

    for (var field in data.structure.fields) {
      if (usedFields.indexOf(field) == -1) {
        var fdata = data.structure.fields[field];
        console.log(field);
        var c = {
          name: field, 
          label: fdata.title,
          column: field
        };
        pushColumn(c, 'attribute');
      }
    }

    console.log(columns);
    return columns;
  };

  var columnsToModel = function(columns) {
    var model = {};
    return model;
  };

  $scope.columns = modelToColumns(data.model);

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
