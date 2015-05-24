
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
  $scope.model = data.model;
  $scope.errors = {};

  $scope.save = function(form) {
    columnsToModel($scope.columns);
    var dfd = $http.post(dataset.api_url + '/model', data.model);
    dfd.then(function(res) {
      $scope.errors = {};
      data.model = res.data;
      $scope.columns = modelToColumns();
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

  var inferDimension = function(name, label) {
    if (!data.model.dimensions[name]) {
      data.model.dimensions[name] = {
        name: name,
        label: label
      }
    }
    return data.model.dimensions[name];
  };

  var generateColumn = function(name, spec) {
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
      c.dimension = inferDimension(parts[0], dim);
    } else if (spec.type == 'integer' || spec.type == 'float') {
      // treat most numbers as measures
      if (!isYearsColumn(name)) {
        c.concept = 'measure';
      }
    }

    // so it's a dimension
    if (!c.concept) {
      c.concept = 'attribute';
      c.dimension = inferDimension(name, c.label);
    }

    return c;
  };

  var modelToColumns = function() {
    var model = data.model, columns = [], usedFields = [];
    model.measures = model.measures || {};
    model.dimensions = model.dimensions || {};

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
    return columns;
  };

  var columnsToModel = function(columns) {
    var model = {dimensions: {}, measures: {}};
    for (var idx in columns) {
      var col = columns[idx];
      if (col.concept == 'measure') {
        model.measures[col.name] = {
          label: col.label,
          column: col.column
        };
      } else {
        var dim = col.dimension.name;
        if (!model.dimensions[dim]) {
          model.dimensions[dim] = {
            label: col.dimension.label,
            attributes: {}
          };
        }
        model.dimensions[dim].attributes[col.name] = {
          label: col.label,
          column: col.column
        };
      }
    }
    data.model = model;
    $scope.model = model;
  };

  $scope.columns = modelToColumns();

  $scope.changeConcept = function(col) {
    if (col.concept == 'attribute') {
      col.dimension = inferDimension(col.name, col.label);
    } else {
      delete col.dimension;
    }
  };

  $scope.getDimensions = function() {
    var dimensions = [], objects = [];
    for (var i in $scope.columns) {
      var col = $scope.columns[i];
      if (col.dimension && dimensions.indexOf(col.dimension.name) == -1) {
        dimensions.push(col.dimension.name);
        objects.push(col.dimension);
      }
    }
    return objects.sort(function(a, b) {
      if (a.label > b.label) return 1;
      if (a.label < b.label) return -1;
      return 0;
    });
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
