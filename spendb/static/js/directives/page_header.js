
spendb.directive('pageHeader', ['$http', '$rootScope', '$route', '$location', 'flash', 'config', 'session',
  function ($http, $rootScope, $route, $location, flash, config, session) {
  return {
    restrict: 'E',
    //transclude: true,
    scope: {
      dataset: '=',
      section: '@'
    },
    templateUrl: 'directives/page_header.html',
    link: function (scope, element, attrs, model) {
      //scope.site_title = config.site_title;
      scope.session = {};
      scope.flash = flash;
      scope.home_page = $route.current.loadedTemplateUrl == 'home.html';
      scope.title = scope.dataset ? scope.dataset.label : $rootScope.currentTitle;

      session.get(function(s) {
        scope.session = s;
      });

      // Logout
      scope.logout = function() {
        session.logout(function(s) {
          scope.session = s;
          $location.path('/');
        });
      };

      

    }
  };
}]);
