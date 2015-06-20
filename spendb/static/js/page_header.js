
spendb.directive('pageHeader', ['$http', '$rootScope', '$location',
  function ($http, $rootScope, $location) {
  return {
    restrict: 'E',
    transclude: true,
    scope: {
    },
    templateUrl: 'directives/page_header.html',
    link: function (scope, element, attrs, model) {
      scope.title = $rootScope.currentTitle;
    }
  };
}]);
