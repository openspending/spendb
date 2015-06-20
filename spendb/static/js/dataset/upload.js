
spendb.controller('DatasetUploadCtrl', ['$scope', '$document', '$http', '$location', 'Upload', 'config', 'validation', 'dataset',
  function($scope, $document, $http, $location, Upload, config, validation, dataset) {
  $scope.dataset = dataset;
  $scope.urlForm = {};
  $scope.uploadPercent = null;
  $scope.file = {};

  var uploadDone = function() {
    var next = $location.search().next || 'edit';
    $location.path('/datasets/' + dataset.name + '/' + next);
  };

  $scope.setFile = function(files) {
    for (var i in files) {
      $scope.file = files[i];
    }
  };

  $scope.uploadFile = function() {
    if (!$scope.hasFile()) return;
    $scope.uploadPercent = 1;

    Upload.upload({
      url: dataset.api_url + '/sources/upload',
      file: $scope.file
    }).progress(function (evt) {
      $scope.uploadPercent = Math.max(1, parseInt(95.0 * evt.loaded / evt.total));
    }).success(function (data, status, headers, config) {
      $scope.uploads = [];
      $scope.uploadPercent = null;
      uploadDone();
    });
  };

  $scope.submitUrl = function() {
    if (!scope.hasUrl()) return;
    var form = angular.copy($scope.urlForm);
    $scope.urlForm = {};

    $http.post(dataset.api_url + '/sources/submit', form).then(function(res) {
      uploadDone();
    });
  };

  $scope.hasUrl = function() {
    return $scope.urlForm.url && $scope.urlForm.url.length > 3;
  };

  $scope.hasFile = function() {
    return !$scope.uploadPercent && $scope.file && $scope.file.name;
  };

  $scope.continue = function() {
    if ($scope.hasUrl()) {
      $scope.submitUrl();
    } else {
      $scope.uploadFile();
    }
  };

  $scope.canContinue = function() {
    return $scope.hasUrl() || $scope.hasFile();
  };

}]);

