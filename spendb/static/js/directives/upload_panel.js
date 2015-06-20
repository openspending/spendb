spendb.directive('uploadPanel', ['$http', '$location', '$route', 'Upload',
  function ($http, $location, $route, Upload) {
  return {
    restrict: 'AE',
    scope: {
      "dataset": "=",
      "notify": "&"
    },
    templateUrl: 'directives/upload_panel.html',
    link: function (scope, element, attrs, model) {
      scope.submitForm = {};
      scope.uploadPercent = null;
      scope.uploads = [];

      scope.uploadFile = function() {
        if (!scope.hasFile()) return;
        scope.uploadPercent = 1;

        Upload.upload({
          url: scope.dataset.api_url + '/sources/upload',
          file: scope.uploads[0]
        }).progress(function (evt) {
          scope.uploadPercent = Math.max(1, parseInt(95.0 * evt.loaded / evt.total));
        }).success(function (data, status, headers, config) {
          scope.uploads = [];
          scope.uploadPercent = null;
          if (scope.notify) scope.notify();
        });
      };

      scope.hasFile = function() {
        return !scope.uploadPercent && scope.uploads && scope.uploads.length;
      };

      scope.submitUrl = function() {
        if (!scope.hasUrl()) return;
        var form = angular.copy(scope.submitForm);
        scope.submitForm = {};

        $http.post(scope.dataset.api_url + '/sources/submit', form).then(function(res) {
          if (scope.notify) scope.notify();
        });
      };

      scope.hasUrl = function() {
        return scope.submitForm.url && scope.submitForm.url.length > 3;
      };

    }
  };
}]);
