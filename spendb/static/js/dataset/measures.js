
spendb.controller('DatasetMeasuresCtrl', ['$scope', '$document', '$http', '$location', '$q', 'flash', 'validation', 'dataset', 'data',
  function($scope, $document, $http, $location, $q, flash, validation, dataset, data) {
  $scope.dataset = dataset;
  $scope.samples = data.structure.samples;
  $scope.columns = [];
  $scope.fields = [];
  $scope.errors = {};

  $scope.back = function() {
    $location.path('/datasets/' + dataset.name + '/sources');
  };

  var isNumeric = function(fld) {
    return fld.type == 'integer' || fld.type == 'float' || fld.type == 'decimal';
  };

  var load = function() {
    var model = data.model,
        measures = model.measures || {},
        fields = [];

    for (var name in data.structure.fields) {
      var field = data.structure.fields[name];
      field.numeric = isNumeric(field);
      field.slug_linked = true;
      for (var mn in measures) {
        var m = measures[mn];
        if (m.column == name) {
          m.name = mn;
          field.slug_linked = false;
          field.measure = m;  
        }
      }
      fields.push(field);
    }
    $scope.fields = fields.sort(function(a, b) { return a.title.localeCompare(b.title); });
  };

  var unload = function() {
    var measures = {};
    for (var i in $scope.fields) {
      var field = $scope.fields[i];
      if (field.measure) {
        measures[field.measure.name] = {
          label: field.measure.label,
          column: field.name,
          description: field.measure.description
        }
      }
    }
    data.model.dimensions = data.model.dimensions || {};
    data.model.measures = measures;
  };

  $scope.toggleIgnore = function(field) {
    field.ignore = !field.ignore;
  };

  $scope.toggleSamples = function(field) {
    field.show_samples = !field.show_samples;
  };

  $scope.toggleMeasure = function(field) {
    if (field.measure) {
      delete field.measure;
    } else {
      field.measure = {name: field.name, label: field.title};
    }
  };

  $scope.breakSlugLink = function(field) {
    field.slug_linked = false;
  };

  $scope.updateSlug = function(field) {
    if (field.slug_linked) {
      field.measure.name = getSlug(field.measure.label, '_');
    }
  };

  $scope.canSave = function() {
    for (var i in $scope.fields) {
      var field = $scope.fields[i];
      if (field.measure) {
        return true;
      }
    }
    return false;
  };

  $scope.save = function() {
    unload();
    $scope.errors = {};
    $http.post(dataset.api_url + '/model', data.model).then(function(res) {
      console.log(res.data);
    }, function(res) {
      $scope.errors = res.data.errors;
    });
  };

  load();

}]);

