
spendb.controller('AdminDataCtrl', ['$scope', '$rootScope', '$http', '$window', '$routeParams', 'dataset',
  function($scope, $rootScope, $http, $window, $routeParams, dataset, sources) {
  $scope.dataset = dataset;

  $rootScope.setSection('data');

}]);


spendb.controller('AdminMetadataCtrl', ['$scope', '$rootScope', '$q', '$http', '$location', '$routeParams', 'reference', 'dataset', 'managers', 'flash', 'validation',
  function($scope, $rootScope, $q, $http, $location, $routeParams, reference, dataset, managers, flash, validation) {

  $scope.reference = reference;
  $scope.dataset = dataset;
  $scope.managers = managers;

  $rootScope.setSection('metadata');

  $scope.suggestAccounts = function(query) {
    var dfd = $q.defer(),
        params =  {q: query};
    $http.get('/accounts/_complete', {params: params}).then(function(es) {
      var accounts = []
      for (var i in es.data.results) {
        var account = es.data.results[i],
            seen = false;
        for (var j in $scope.managers.managers) {
          var other = $scope.managers.managers[j];
          if (other.name == account.name) {
            seen = true;
          }
        }
        if (!seen) {
          accounts.push(account);
        }
      }
      dfd.resolve(accounts);
    });
    return dfd.promise;
  };

  $scope.addAccount = function() {
    if ($scope.managers.fresh && $scope.managers.fresh.name) {
      $scope.managers.managers.push($scope.managers.fresh);
      $scope.managers.fresh = null;
    }
  };

  $scope.removeAccount = function(account) {
    if ($scope.managers.indexOf(account) != -1) {
      $scope.managers.splice($scope.managers.indexOf(account), 1);
    }
  };

  $scope.save = function(form) {
    var dfd = $http.post(dataset.api_url, $scope.dataset);
    dfd.then(function(res) {
      $scope.dataset = res.data;
      flash.setMessage("Your changes have been saved!", "success");
      $scope.resetScroll();
    }, validation.handle(form));
  };

}]);

spendb.controller('AdminConceptCtrl', ['$scope', '$modalInstance', 'concept', 'dimension', 'validation',
  function($scope, $modalInstance, concept, dimension, validation) {
  $scope.validSlug = validation.validSlug;
  $scope.concept = concept;
  $scope.dimension = dimension;

  $scope.close = function() {
    $modalInstance.dismiss('ok');
  };

}]);

spendb.controller('AdminModelCtrl', ['$scope', '$http', '$window', '$timeout', '$rootScope', '$modal', 'dataset', 'data', 'validation', 'flash',
  function($scope, $http, $window, $timeout, $rootScope, $modal, dataset, data, validation, flash) {
  $scope.validSlug = validation.validSlug;
  $scope.dataset = dataset;
  $scope.samples = data.structure.samples;
  $scope.model = data.model;
  $scope.errors = {};

  $rootScope.setSection('model');

  $scope.save = function(form) {
    columnsToModel($scope.columns);
    var dfd = $http.post(dataset.api_url + '/model', data.model);
    dfd.then(function(res) {
      $scope.errors = {};
      data.model = res.data;
      $scope.columns = modelToColumns();
      flash.setMessage("Your changes have been saved!", "success");
      $scope.resetScroll();
    }, function(res) {
      $scope.errors = res.data.errors;
      $scope.resetScroll();
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
    } else if ($scope.possibleMeasure(spec)) {
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

    var pushColumn = function(col, concept) {
      col.concept = concept;
      col.type = data.structure.fields[col.column].type;
      usedFields.push(col.column);
      columns.push(col);
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

  $scope.possibleMeasure = function(col) {
    return col.type == 'integer' || col.type == 'float';
  };

  $scope.updateConcept = function() {
    if (col.concept == 'attribute') {
      col.dimension = inferDimension(col.name, col.label);
    } else {
      delete col.dimension;
    }
  };

  $scope.editConcept = function(col){
    var d = $modal.open({
      templateUrl: 'admin/concept.html',
      controller: 'AdminConceptCtrl',
      backdrop: false,
      resolve: {
        concept: function() {
          return col.concept;
        },
        dimension: function () {
          return col.concept == 'attribute' ? col.dimension : col;
        }
      }
    });
  };

  $scope.getDimensions = function(col) {
    var dimensions = [], objects = [], colDim = false;
    for (var i in $scope.columns) {
      var coli = $scope.columns[i],
          dim = coli.dimension;
      if (dim && dimensions.indexOf(dim.name) == -1) {
        if (col.name == dim.name) colDim = true;
        dim.group = 'Currently in use';
        dimensions.push(dim.name);
        objects.push(dim);
      }
    }
    if (!colDim) {
      var dim = inferDimension(col.name, col.label)
      dim.group = 'Create a new dimension'
      objects.push(dim);
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

  $scope.columns = modelToColumns();

}]);


spendb.controller('AdminRunCtrl', ['$scope', '$http', '$location', '$routeParams', 'dataset', 'run',
  function($scope, $http, $location, $routeParams, dataset, run) {

  $scope.dataset = dataset;
  $scope.run = run.data;

  $rootScope.setSection('data');

}]);
