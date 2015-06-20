
spendb.controller('DatasetNewCtrl', ['$scope', '$document', '$http', '$location', 'config', 'validation',
  function($scope, $document, $http, $location, config, validation) {
  var bindSlug = true;

  $scope.baseUrl = config.site_url + '/datasets/';
  $scope.forms = {};

  $scope.editSlug = function() {
    bindSlug = false;
  }

  $scope.$watch('dataset.label', function(e) {
    if (bindSlug && e) {
      $scope.dataset.name = getSlug(e, '-');
    }
  });

  $scope.dataset = {'category': 'budget', 'territories': [], 'private': true};

  $scope.createDataset = function() {
    validation.clear($scope.forms.dataset);
    $http.post('/api/3/datasets', $scope.dataset).then(function(res) {
      $scope.dataset = res.data;
      //scrollSection('upload');
    }, validation.handle($scope.forms.dataset));
  };

}]);

