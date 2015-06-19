
spendb.directive('datasetList', ['$http', '$timeout',
  function ($http, $timeout) {
  return {
    restrict: 'AE',
    scope: {
      "datasets": "="
    },
    templateUrl: 'directives/dataset_list.html',
    link: function (scope, element, attrs, model) {
      scope.load = function(url) {
        $http.get(url).then(function(res) {
          scope.datasets = res.data;
        });
      };
    }
  };
}]);
