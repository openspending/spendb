
spendb.directive('datasetList', ['$http', '$location',
  function ($http, $location) {
  return {
    restrict: 'AE',
    scope: {
      "datasets": "="
    },
    templateUrl: 'directives/dataset_list.html',
    link: function (scope, element, attrs, model) {
      scope.load = function(offset) {
        var state = angular.extend({}, $location.search(), {offset: offset});
        $location.search(state);
      };

      scope.getDatasetLink = function(dataset) {
        var link = '/datasets/' + dataset.name;
        if (!dataset.has_model) {
          link = link + '/about';
        }
        return link;
      };
    }
  };
}]);
