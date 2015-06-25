
spendb.directive('pageHeader', ['$http', '$rootScope', '$route', '$location', '$modal', 'flash', 'config', 'session',
  function ($http, $rootScope, $route, $location, $modal, flash, config, session) {
  return {
    restrict: 'E',
    //transclude: true,
    scope: {
      dataset: '=',
      section: '@'
    },
    templateUrl: 'directives/page_header.html',
    link: function (scope, element, attrs, model) {
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

      scope.deleteDataset = function() {
        var d = $modal.open({
          templateUrl: 'dataset/delete.html',
          controller: 'DatasetDeleteCtrl',
          backdrop: true,
          resolve: {
            dataset: function () {
              return scope.dataset;
            }
          }
        });
      };

      scope.togglePrivate = function() {
        scope.dataset.private = !scope.dataset.private;
        $http.post(scope.dataset.api_url, scope.dataset).then(function(res) {
          if (res.data.private) {
            flash.setMessage("The dataset has been made private.", "danger");
          } else {
            flash.setMessage("The dataset is now public!", "success");
          }
        });
      };

    }
  };
}]);
