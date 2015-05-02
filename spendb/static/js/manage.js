

var loadDataset = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      url = '/api/3/datasets/' + $route.current.params.dataset;
  $http.get(url).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


var loadReferenceData = ['$q', 'data', function($q, wdata) {
  var dfd = $q.defer();
  data.get(function(rd) {
    dfd.resolve(rd);
  });
  return dfd.promise;
}];


spendb.directive('uploadPanel', ['$http', '$location', '$route', 'Upload',
  function ($http, $location, $route, Upload) {
  return {
    restrict: 'AE',
    scope: {
      "dataset": "="
    },
    templateUrl: '/static/templates/dataset/upload.html',
    link: function (scope, element, attrs, model) {
      scope.submitForm = {};
      scope.uploadPercent = null;
      scope.uploads = [];

      scope.uploadFile = function() {
        if (!scope.hasFile()) return;
        scope.uploadPercent = 1;

        Upload.upload({
          url: scope.dataset.api_url + '/sources/upload',
          file: scope.uploads[0]
        }).progress(function (evt) {
          scope.uploadPercent = Math.max(1, parseInt(70.0 * evt.loaded / evt.total));
        }).success(function (data, status, headers, config) {
          scope.uploads = [];
          scope.uploadPercent = null;
          //$location.path('/datasets/' + scope.dataset.name + '/manage');
          //$route.reload();
        });
      };

      scope.hasFile = function() {
        return !scope.uploadPercent && scope.uploads && scope.uploads.length;
      };

      scope.submitUrl = function() {
        if (!scope.hasUrl()) return;
        var form = angular.copy(scope.submitForm);
        scope.submitForm = {};

        $http.post(scope.dataset.api_url + '/sources/submit', form).then(function(res) {
          //$location.path('/datasets/' + scope.dataset.name + '/manage');
          //$route.reload();
        });
      };

      scope.hasUrl = function() {
        return scope.submitForm.url && scope.submitForm.url.length > 3;
      };

    }
  };
}]);


spendb.directive('sourcesTable', ['$http', '$timeout',
  function ($http, $timeout) {
  return {
    restrict: 'AE',
    scope: {
      "dataset": "="
    },
    templateUrl: '/static/templates/dataset/sources.html',
    link: function (scope, element, attrs, model) {
      var sourcesUrl = scope.dataset.api_url + '/sources',
          runsUrl = scope.dataset.api_url + '/runs',
          loadTimeout = null;
      scope.sources = {};

      scope.hasSources = function() {
        return angular.isDefined(scope.sources.total);
      };

      var recheck = function() {
        $http.get(sourcesUrl).then(function(res) {
          var sources = res.data;
          if (sources.results.length) {
            var params = {source: sources.results[0].path};
            $http.get(runsUrl, {params: params}).then(function(res) {
              sources.results[0].runs = res.data.results;
              scope.sources = sources;
              loadTimeout = $timeout(recheck, 2000);
            });
          } else {
            scope.sources = sources;
            loadTimeout = $timeout(recheck, 2000);
          }
        });
      };

      recheck();

      scope.$on('$destroy', function() {
        $timeout.cancel(loadTimeout);
      });

    }
  };
}]);


spendb.controller('DatasetManageCtrl', ['$scope', '$http', '$window', '$routeParams', 'dataset',
  function($scope, $http, $window, $routeParams, dataset, sources) {
  $scope.dataset = dataset;

}]);


spendb.controller('DatasetMetaCtrl', ['$scope', '$http', '$location', '$routeParams', 'reference', 'dataset', 'flash', 'validation',
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


spendb.controller('DatasetModelCtrl', ['$scope', '$http', '$window', '$routeParams', 'dataset',
  function($scope, $http, $window, $routeParams, dataset) {
  var fieldsApi = dataset.api_url + '/fields',
      modelApi = dataset.api_url + '/model';
  
  $scope.dataset = dataset;
  $scope.fields = {};
  $scope.model = {};

  $scope.save = function(form) {
    var dfd = $http.post(modelApi, $scope.model);
    dfd.then(function(res) {
      $scope.model = res.data;
      flash.setMessage("Your changes have been saved!", "success");
    }, validation.handle(form));
  };

  $http.get(fieldsApi).then(function(res) {
      $scope.fields = res.data;
  });

  $http.get(modelApi).then(function(res) {
      $scope.model = res.data;
  });

}]);

