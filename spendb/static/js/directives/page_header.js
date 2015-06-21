
spendb.directive('pageHeader', ['$http', '$rootScope', '$location', 'flash', 'config', 'session',
  function ($http, $rootScope, $location, flash, config, session) {
  return {
    restrict: 'E',
    transclude: true,
    scope: {
    },
    templateUrl: 'directives/page_header.html',
    link: function (scope, element, attrs, model) {
      scope.site_title = config.site_title;
      scope.session = scope.$parent.session;
      scope.flash = flash;
      scope.title = $rootScope.currentTitle;

      // Logout
      scope.logout = function() {
        session.logout(function(s) {
          scope.$parent.reloadSession();
        });
      };


    }
  };
}]);
