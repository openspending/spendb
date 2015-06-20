
spendb.directive('sourcesTable', ['$http', '$timeout',
  function ($http, $timeout) {
  return {
    restrict: 'AE',
    scope: {
      "dataset": "="
    },
    templateUrl: 'directives/sources_table.html',
    link: function (scope, element, attrs, model) {
      var sourcesUrl = scope.dataset.api_url + '/sources',
          loadTimeout = null;
      scope.sources = {};

      scope.hasSources = function() {
        return angular.isDefined(scope.sources.total);
      };

      scope.canModelRun = function(run) {
        if (!run.status == 'complete') {
          return false;  
        }
        return run.operation.indexOf('to database') != -1;
      };

      scope.recheck = function() {
        $http.get(sourcesUrl).then(function(res) {
          var sources = res.data;
          if (sources.results.length) {
            var url = sources.results[0].runs_url;
            $http.get(url).then(function(res) {
              sources.results[0].runs = res.data.results;
              scope.sources = sources;
              loadTimeout = $timeout(scope.recheck, 2000);
            });
          } else {
            scope.sources = sources;
            loadTimeout = $timeout(scope.recheck, 2000);
          }
        });
      };

      scope.recheck();

      scope.$on('$destroy', function() {
        $timeout.cancel(loadTimeout);
      });

    }
  };
}]);
