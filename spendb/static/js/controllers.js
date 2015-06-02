

spendb.controller('NewCtrl', ['$scope', '$document', '$http', '$location', 'reference', 'validation', 'session',
  function($scope, $document, $http, $location, reference, validation, session) {

  $scope.validSlug = validation.validSlug;
  $scope.dataset = {'category': 'budget', 'territories': []};
  $scope.reference = reference;
  $scope.session = session;
  $scope.afterUpload = [];

  var scrollSection = function(el) {
    var elem = angular.element(document.getElementById(el));
    $document.scrollToElement(elem, 0, 500);
  };

  $scope.hasDataset = function() {
    return session.logged_in && angular.isDefined($scope.dataset.api_url);
  };

  $scope.hasUpload = function() {
    return $scope.hasDataset() && $scope.afterUpload.length > 0;
  };

  $scope.createDataset = function(form) {
    validation.clear(form);
    $http.post('/api/3/datasets', $scope.dataset).then(function(res) {
      $scope.dataset = res.data;
      scrollSection('upload');
    }, validation.handle(form));
  };

  $scope.createUpload = function() {
    if (!$scope.hasDataset()) return;
    if ($scope.hasUpload()) return;
    $scope.afterUpload.push($scope.dataset);
    scrollSection('metadata');
  };

  $scope.saveDataset = function(form) {
    if (!$scope.hasDataset()) return;
    validation.clear(form);
    $http.post($scope.dataset.api_url, $scope.dataset).then(function(res) {
      $location.path('/datasets/' + $scope.dataset.name + '/admin')
    }, validation.handle(form));
  };

}]);


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
      backdrop: false,
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
