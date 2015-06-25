
spendb.controller('DatasetCtrl', ['$scope', '$rootScope', '$http', '$modal', 'config',
  function($scope, $rootScope, $http, $modal, config) {
  $scope.currentSection = 'home';

  $scope.dataset = config.dataset;

  $rootScope.setSection = function(section) {
    $scope.currentSection = section;
  };

  $scope.deleteDataset = function() {
    var d = $modal.open({
      templateUrl: 'admin/delete.html',
      controller: 'AdminDeleteCtrl',
      backdrop: true,
      resolve: {
        dataset: function() {
          return $scope.dataset;
        },
      }
    });
  };

  $scope.togglePrivate = function() {
    $scope.dataset.private = !$scope.dataset.private;
    $http.post($scope.dataset.api_url, $scope.dataset).then(function(res) {
      $scope.dataset = res.data;
    })
  };

}]);
