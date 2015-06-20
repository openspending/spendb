
spendb.controller('DatasetDimensionsCtrl', ['$scope', '$document', '$http', '$location', '$q', 'flash', 'validation', 'dataset', 'data',
  function($scope, $document, $http, $location, $q, flash, validation, dataset, data) {
  $scope.dataset = dataset;
  $scope.addFields = {};
  $scope.dimensions = [];

  var load = function() {
    var model = data.model,
        measures = model.measures || {},
        dimensions = model.dimensions || {},
        dims = [];
    for (var name in dimensions) {
      var dim = dimensions[name];
      dim.name = name;
      var attributes = dim.attributes || {},
          attrs = [];
      for (var an in attributes) {
        var attr = attributes[an];
        attr.name = an;
        attrs.push(attr);
      }
      dim.attributes = attrs;
      dims.push(dim);
    }
    $scope.dimensions = dims;
  };

  var unload = function() {
    var dimensions = {};
    for (var i in $scope.dimensions) {
      var dim = $scope.dimensions[i],
          attributes = {};
      for (var j in dim.attributes) {
        var attr = dim.attributes[j];
        attributes[attr.name] = attr;
      }
      dim.attributes = attributes;
      dimensions[dim.name] = dim;
    }
    data.model.dimensions = dimensions;
  };

  $scope.getAvailableFields = function() {
    var fields = [],
        measures = data.model.measures || {};
    for (var f in data.structure.fields) {
      var field = data.structure.fields[f],
          include = true;
      for (var i in measures) {
        var measure = measures[i];
        if (measure.column == field.name) {
          include = false
        }
      }
      if (include) {
        for (var i in $scope.dimensions) {
          var dim = $scope.dimensions[i];
          for (var j in dim.attributes) {
            var attr = dim.attributes[j];
            if (attr.column == field.name) {
              include = false;
            }
          }
        }
      }
      if (include) {
        fields.push(field);  
      }
    }
    return fields.sort(function(a, b) { return a.title.localeCompare(b.title); });
  };

  $scope.toggleSamples = function(field) {
    field.show_samples = !field.show_samples;
  };

  $scope.getSamples = function(field) {
    var samples = [];
    for (var i in data.structure.samples) {
      var row = data.structure.samples[i],
          val = row[field.name];
      if (samples.indexOf(val) == -1) {
        samples.push(val);
      } 
    }
    return samples.sort(function(a, b) { return a - b; });
  };

  $scope.back = function() {
    $location.path('/datasets/' + dataset.name + '/model/measures');
  };

  $scope.canSave = function() {
    return true;
  };

  $scope.save = function() {
    unload();
  };

  load();

}]);

