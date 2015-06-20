
spendb.directive('datasetSettings', ['$rootScope', '$http', '$location',
  function ($rootScope, $http, $location) {
  return {
    restrict: 'AE',
    transclude: true,
    scope: {
      "dataset": "=",
      "nextLabel": "@",
      "prevLabel": "@",
      "next": "&",
      "prev": "&"
    },
    templateUrl: 'directives/dataset_settings.html',
    link: function (scope, element, attrs, model) {
      var title = scope.dataset ? scope.dataset.label : "Create a new dataset";
      $rootScope.setTitle(title);
    }
  };
}]);
