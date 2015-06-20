
spendb.directive('pageHeader', ['$http', '$rootScope', '$location', 'flash',
  function ($http, $rootScope, $location, flash) {
  return {
    restrict: 'E',
    transclude: true,
    scope: {
    },
    templateUrl: 'directives/page_header.html',
    link: function (scope, element, attrs, model) {
      scope.flash = flash;
      scope.title = $rootScope.currentTitle;
    }
  };
}]);
