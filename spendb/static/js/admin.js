
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


spendb.controller('AdminModelCtrl', ['$scope', '$http', '$window', '$timeout', '$rootScope', 'dataset', 'data', 'validation',
  function($scope, $http, $window, $timeout, $rootScope, dataset, data, validation) {
  $scope.dataset = dataset;
  $scope.samples = data.structure.samples;
  $scope.errors = {};

  $scope.save = function(form) {
    var model = columnsToModel($scope.columns);
    var dfd = $http.post(dataset.api_url + '/model', model);
    dfd.then(function(res) {
      $scope.errors = {};
      $scope.columns = modelToColumns(res.data);
      flash.setMessage("Your changes have been saved!", "success");
    }, function(res) {
      $scope.errors = res.data.errors;
    });
  };

  var isYearsColumn = function(column) {
    // just kidding
    for (var row in data.structure.samples) {
      var val = row[column];
      if (!angular.isUndefined(val) && val != null) {
        if (val > 2100 && val < 1900) return false;
      }
    }
    return true;
  };

  var inferDimension = function(name, label, model) {
    if (!model.dimensions[name]) {
      model.dimensions[name] = {
        name: name,
        label: label
      }
    }
    return model.dimensions[name];
  };

  var generateColumn = function(name, spec, model) {
    var c = {
      name: name, 
      label: spec.title,
      column: name
    };

    // extra handling for auto-split dates from ETL
    var parts = name.split('__');
    if (parts.length > 1) {
      c.name = parts[1];
      c.concept = 'attribute';
      // column titles are: "Foo (Year)"
      var dim = c.label.split(' (')[0];
      c.dimension = inferDimension(parts[0], dim, model);
    } else if (spec.type == 'integer' || spec.type == 'float') {
      // treat most numbers as measures
      if (!isYearsColumn(name)) {
        c.concept = 'measure';
      }
    }

    // so it's a dimension
    if (!c.concept) {
      c.concept = 'attribute';
      c.dimension = inferDimension(name, c.label, model);
    }

    return c;
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
        var fdata = data.structure.fields[field],
            col = generateColumn(field, fdata, model);
        pushColumn(col, col.concept);
      }
    }

    console.log(columns);
    return columns;
  };

  var columnsToModel = function(columns) {
    var model = {dimensions: {}, measures: {}};

    console.log(model);
    return model;
  };

  $scope.columns = modelToColumns(data.model);

  $scope.changeConcept = function(col) {
    if (col.concept == 'attribute') {
      var model = {dimensions: {}};
      col.dimension = inferDimension(col.name, col.label, model);
    } else {
      delete col.dimension;
    }
  };

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
