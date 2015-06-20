
spendb.directive('datasetSettings', ['$rootScope', '$http', '$location',
  function ($rootScope, $http, $location) {
  return {
    restrict: 'AE',
    transclude: true,
    scope: {
      "dataset": "=",
      "nextLabel": "@",
      "prevLabel": "@",
      "prevActive": "=",
      "nextActive": "&",
      "next": "&",
      "prev": "&"
    },
    templateUrl: 'directives/dataset_settings.html',
    link: function (scope, element, attrs, model) {
      var title = scope.dataset ? scope.dataset.label : "Create a new dataset",
          mode = $location.search().mode,
          wizard = mode == 'wizard' || !scope.dataset || !scope.dataset.api_url;
      $rootScope.setTitle(title);
      scope.wizard = scope.$parent.wizard = wizard;
      console.log(scope.wizard ? "Wizard mode" : "Edit mode");
    }
  };
}]);
