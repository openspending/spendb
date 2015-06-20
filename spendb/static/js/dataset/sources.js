
var loadRun = ['$route', '$q', '$http', function($route, $q, $http) {
  var p = $route.current.params,
      url = '/api/3/datasets/' + p.dataset + '/runs/' + p.run;
  return $http.get(url);
}];


spendb.controller('DatasetSourcesCtrl', ['$scope', '$document', '$http', '$location', '$timeout', 'flash', 'dataset',
  function($scope, $document, $http, $location, $timeout, flash, dataset) {
  var sourcesUrl = dataset.api_url + '/sources',
      loadTimeout = null;
  
  $scope.LOGLEVELS = {'WARNING': 'warning', 'ERROR': 'danger'};
  $scope.dataset = dataset;
  $scope.source = {};
  $scope.errors = {};

  $scope.hasSource = function() {
    return angular.isDefined($scope.source.api_url);
  };

  $scope.canContinue = function() {
    if (!$scope.source.runs || $scope.source.runs.length == 0) {
      return false;
    }
    var run = $scope.source.runs[$scope.source.runs.length - 1];
    if (run.status != 'complete') {
      return false;  
    }
    return run.operation.indexOf('to database') != -1;
  };

  $scope.continue = function() {
    $location.path('/datasets/' + dataset.name + '/model/measures');
  };

  $scope.back = function() {
    $location.path('/datasets/' + dataset.name + '/edit');
  };

  $scope.upload = function() {
    $location.search(angular.extend({}, $location.search(), {next: 'sources'}));
    $location.path('/datasets/' + dataset.name + '/upload');
  };

  var loadRunLog = function(run) {
    var url = dataset.api_url + '/runs/' + run.id;
    $http.get(url).then(function(res) {
      res.data.messages.reverse();
      $scope.errors = res.data;
    });
  };

  $scope.recheck = function() {
    $http.get(sourcesUrl).then(function(res) {
      var sources = res.data;
      if (sources.results.length) {
        var url = sources.results[0].runs_url;
        $http.get(url).then(function(res) {
          sources.results[0].runs = res.data.results;
          $scope.source = sources.results[0];
          var run = res.data.results[res.data.results.length - 1];
          if (run.status == 'failed') {
            loadRunLog(run);
          } else {
            loadTimeout = $timeout($scope.recheck, 2000);  
          }
        });
      } else {
        $scope.source = {};
        loadTimeout = $timeout($scope.recheck, 2000);
      }
    });
  };

  $scope.recheck();

  $scope.$on('$destroy', function() {
    $timeout.cancel(loadTimeout);
  });

}]);

