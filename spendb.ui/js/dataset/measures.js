
spendb.controller('DatasetMeasuresCtrl', ['$scope', '$rootScope', '$http', '$location', '$q', 'slugifyFilter', 'flash', 'validation', 'dataset', 'data',
  function($scope, $rootScope, $http, $location, $q, slugifyFilter, flash, validation, dataset, data) {
  $scope.dataset = dataset;
  $scope.columns = [];
  $scope.fields = [];
  $scope.errors = {};

  $scope.back = function() {
    $location.path('/datasets/' + dataset.name + '/sources');
  };

  var isNumeric = function(fld) {
    return fld.type == 'integer' || fld.type == 'number';
  };

  var load = function() {
    var model = data.model,
        measures = model.measures || {},
        fields = [];

    for (var i in data.structure.fields) {
      var field = data.structure.fields[i];
      field.numeric = isNumeric(field);
      field.slug_linked = true;
      for (var mn in measures) {
        var m = measures[mn];
        if (m.column == field.name) {
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
    var model = angular.copy(data.model);
    model.dimensions = model.dimensions || {};
    model.measures = measures;
    return model;
  };

  $scope.toggleIgnore = function(field) {
    field.ignore = !field.ignore;
  };

  $scope.toggleSamples = function(field) {
    field.show_samples = !field.show_samples;
  };

  $scope.getSamples = function(field) {
    return field.samples.sort(function(a, b) { return a - b; });
  };

  $scope.toggleMeasure = function(field) {
    if (field.measure) {
      delete field.measure;
    } else {
      var label = cleanLabel(field.title);
      field.measure = {name: slugifyFilter(label, '_'), label: label};
    }
  };

  $scope.breakSlugLink = function(field) {
    field.slug_linked = false;
  };

  $scope.updateSlug = function(field) {
    if (field.slug_linked) {
      field.measure.name = slugifyFilter(field.measure.label, '_');
    }
  };

  $scope.validLabel = function(field) {
    if (!field.measure || !field.measure.label ||
        field.measure.label.length < 2) {
      return false;
    }
    return true;
  };

  $scope.validSlug = function(field) {
    if (!field.measure || !field.measure.name ||
        field.measure.name.length < 2) {
      return false;
    }
    if (field.measure.name != slugifyFilter(field.measure.name, '_')) {
      return false;
    }
    for (var i in $scope.fields) {
      var f = $scope.fields[i];
      if (f.measure && field.name != f.name &&
          f.measure.name == field.measure.name) {
        return false;
      }
    }
    return true;
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
    var model = unload();
    $scope.errors = {};
    $http.post(dataset.api_url + '/model', model).then(function(res) {
      if ($scope.wizard) {
        $location.path('/datasets/' + dataset.name + '/model/dimensions');
      } else {
        flash.setMessage("Your changes have been saved!", "success");
      }
      $scope.resetScroll();
    }, function(res) {
      $scope.errors = res.data.errors;
      $scope.resetScroll();
    });
  };

  load();

}]);
