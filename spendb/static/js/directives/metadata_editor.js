
spendb.directive('metadataEditor', ['$http',
  function ($http, data) {
  return {
    restrict: 'AE',
    scope: {
      "dataset": "=",
      "reference": "=",
      "form": "="
    },
    transclude: true,
    templateUrl: 'directives/metadata_editor.html',
    link: function (scope, element, attrs, model) {
    }
  };
}]);
