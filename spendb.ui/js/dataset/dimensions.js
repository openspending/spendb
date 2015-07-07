
spendb.controller('DatasetDimensionsCtrl', ['$scope', '$modal', '$http', '$location', '$q', 'slugifyFilter', 'flash', 'validation', 'dataset', 'data',
  function($scope, $modal, $http, $location, $q, slugifyFilter, flash, validation, dataset, data) {
  $scope.dataset = dataset;
  $scope.selectedFields = {};
  $scope.dimensions = [];

  var load = function(model) {
    var measures = model.measures || {},
        dimensions = model.dimensions || {},
        dims = [];
    for (var name in dimensions) {
      var dim = dimensions[name];
      dim.name = name;
      dim.slug_linked = false;
      var attributes = dim.attributes || {},
          attrs = [];
      for (var an in attributes) {
        var attr = attributes[an];
        attr.name = an;
        attr.slug_linked = false;
        if (an == dim.label_attribute) {
          dim.label_attribute = attr;
        }
        if (an == dim.key_attribute) {
          dim.key_attribute = attr;
        }
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
      var dim = angular.copy($scope.dimensions[i]),
          attributes = {};
      for (var j in dim.attributes) {
        var attr = dim.attributes[j];
        attributes[attr.name] = attr;
      }
      dim.attributes = attributes;
      dim.label_attribute = dim.label_attribute.name;
      dim.key_attribute = dim.key_attribute.name;
      dimensions[dim.name] = dim;
    }
    var model = angular.copy(data.model);
    model.dimensions = dimensions;
    return model;
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

  $scope.canAdd = function() {
    for (var n in $scope.selectedFields) {
      if($scope.selectedFields[n]) {
        return true;
      }
    }
    return false;
  };

  $scope.addFields = function(dimension) {
    dimension = dimension || {};
    dimension.attributes = dimension.attributes || [];

    var labels = [];
    for (var n in $scope.selectedFields) {
      if ($scope.selectedFields[n]) {
        for (var i in data.structure.fields) {
          var field = data.structure.fields[i];
          if (field.name == n) {
            dimension.attributes.push({
            name: field.name,
            column: field.name,
            label: field.title,
            slug_linked: true
          });
          labels.push(field.title);
          delete $scope.selectedFields[n];
          }
        }
      }
    }

    var isNew = !angular.isDefined(dimension.name);
    if (isNew) {
      dimension.slug_linked = true;

      // try and cleverly generate labels and names for
      // attributes and dimensions.
      // this will cause a headache, but it might just be worth it.
      var common = longestCommonStart(labels),
          lastChar = common.length ? common.charAt(common.length - 1) : ' ',
          atBoundary = new RegExp(/[\W_]/g).test(lastChar);
      dimension.label = cleanLabel(atBoundary || labels.length == 1 ? common : '');
      dimension.name = slugifyFilter(dimension.label, '_');

      if (atBoundary) {
        for (var i in dimension.attributes) {
          var attr = dimension.attributes[i];
          if (labels.indexOf(attr.label) != -1 && common.length < attr.label.length) {
            attr.label = cleanLabel(attr.label.slice(common.length));
            attr.name = slugifyFilter(attr.label, '_');
          }
        }
      }
    }
    $scope.editDimension(dimension);
  };

  $scope.editDimension = function(dimension) {
    var dim = angular.copy(dimension)

    dim.attributes = dim.attributes.sort(function(a, b) {
      return a.label.localeCompare(b.label);
    });

    if (!dim.label_attribute) {
      dim.label_attribute = dim.attributes[0];
    }
    if (!dim.key_attribute) {
      dim.key_attribute = dim.attributes[0];
    }

    var d = $modal.open({
      templateUrl: 'dataset/dimension_edit.html',
      controller: 'DatasetDimensionEditCtrl',
      backdrop: true,
      resolve: {
        dimension: function () {
          return dim;
        },
        dimensions: function () {
          var dimensions = [];
          for (var i in $scope.dimensions) {
            var d = $scope.dimensions[i];
            if (d != dimension) {
              dimensions.push(d);
            }
          }
          return dimensions;
        }
      }
    });

    d.result.then(function(changed) {
      $scope.deleteDimension(dimension);
      $scope.dimensions.push(changed);
    });
  };

  $scope.deleteDimension = function(dimension) {
    var idx = $scope.dimensions.indexOf(dimension);
    if (idx != -1) {
      $scope.dimensions.splice(idx, 1);
    }
  };

  $scope.getDimensions = function() {
    return $scope.dimensions.sort(function(a, b) {
      return a.label.localeCompare(b.label);
    });
  };

  $scope.getAttributes = function(dim) {
    return dim.attributes.sort(function(a, b) {
      return a.label.localeCompare(b.label);
    });
  };

  $scope.getSamples = function(field) {
    return field.samples.sort(function(a, b) { return a - b; });
  };

  $scope.back = function() {
    $location.path('/datasets/' + dataset.name + '/model/measures');
  };

  $scope.canSave = function() {
    return true;
  };

  $scope.save = function() {
    var model = unload();
    $scope.errors = {};
    $http.post(dataset.api_url + '/model', model).then(function(res) {
      load(res.data);
      if ($scope.wizard) {

        // final step: publish the dataset
        var ds = angular.copy(dataset);
        ds['private'] = false;
        $http.post(dataset.api_url, ds).then(function() {
          $location.search({});
          $location.path('/datasets/' + dataset.name);
          flash.setMessage("That's it! Your dataset is now ready for use.", "success");
        });
      } else {
        flash.setMessage("Your changes have been saved!", "success");
      }
      $scope.resetScroll();
    }, function(res) {
      $scope.errors = res.data.errors;
      $scope.resetScroll();
    });
  };

  load(data.model);

}]);
