
spendb.controller('DatasetDimensionsCtrl', ['$scope', '$modal', '$http', '$location', '$q', 'flash', 'validation', 'dataset', 'data',
  function($scope, $modal, $http, $location, $q, flash, validation, dataset, data) {
  $scope.dataset = dataset;
  $scope.selectedFields = {};
  $scope.dimensions = [];

  var load = function() {
    var model = data.model,
        measures = model.measures || {},
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
      var dim = $scope.dimensions[i],
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
        var field = data.structure.fields[n];
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
    var isNew = !angular.isDefined(dimension.name);
    dimension.label = dimension.label || longestCommonStart(labels);
    dimension.name = dimension.name || getSlug(dimension.label, '_');
    if (isNew) {
      dimension.slug_linked = true;
      dimension.label_attribute = dimension.attributes[0];
      dimension.key_attribute = dimension.attributes[0];  
    }
    // for (var i in dimension.attributes) {
    //   var attr = dimension.attributes[i];
    //   if (labels.indexOf(attr.label) != -1) {
    //     attr.label = attr.label.slice(dimension.label.length);
    //     attr.name = getSlug(attr.label);
    //   }
    // }
    if (isNew) {
      $scope.dimensions.push(dimension);
    }
    $scope.editDimension(dimension);
  };

  $scope.editDimension = function(dimension) {
    var d = $modal.open({
      templateUrl: 'dataset/dimension_edit.html',
      controller: 'DatasetDimensionEditCtrl',
      backdrop: true,
      resolve: {
        dimension: function () {
          return dimension;
        },
        dimensions: function () {
          return $scope.dimensions;
        }
      }
    });
  };

  $scope.deleteDimension = function(dimension) {
    var idx = $scope.dimensions.indexOf(dimension);
    $scope.dimensions.splice(idx, 1);
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
    $scope.errors = {};
    $http.post(dataset.api_url + '/model', data.model).then(function(res) {
      if ($scope.wizard) {
        $location.path('/datasets/' + dataset.name);
      } else {
        flash.setMessage("Your changes have been saved!", "success");
        $scope.resetScroll();  
      }
    }, function(res) {
      $scope.errors = res.data.errors;
      $scope.resetScroll();
    });
  };

  load();

}]);

