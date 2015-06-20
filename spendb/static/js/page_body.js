
spendb.directive('pageBody', ['$http', '$location',
  function ($http, $location) {
  return {
    restrict: 'E',
    transclude: true,
    templateUrl: 'directives/page_body.html',
    link: function (scope, element, attrs, model) {
    }
  };
}]);
