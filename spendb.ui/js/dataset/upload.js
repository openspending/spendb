
spendb.controller('DatasetUploadCtrl', ['$scope', '$document', '$http', '$location', 'Upload', 'config', 'flash', 'validation', 'dataset',
  function($scope, $document, $http, $location, Upload, config, flash, validation, dataset) {
  $scope.dataset = dataset;
  $scope.urlForm = {};
  $scope.uploadPercent = null;
  $scope.file = {};

  var uploadDone = function() {
    var nextDefault = $scope.wizard ? 'edit' : 'sources',
        next = $location.search().next || nextDefault;
    $location.path('/datasets/' + dataset.name + '/' + next);
  };

  $scope.setFile = function(files) {
    for (var i in files) {
      $scope.file = files[i];
    }
  };

  $scope.uploadServer = function() {
    Upload.upload({
      url: dataset.api_url + '/sources/upload',
      file: $scope.file
    }).progress(function (evt) {
      $scope.uploadPercent = Math.max(1, parseInt(95.0 * evt.loaded / evt.total));
    }).success(function (data, status, headers, config) {
      uploadDone();
    }).error(function (data, status, headers, conf) {
      $scope.uploads = [];
      $scope.uploadPercent = null;
      flash.setMessage("There was an error uploading your file. Please try again.", "danger");
    });
  };

  $scope.uploadBucket = function(config) {
    Upload.upload({
        url: config.url,
        method: 'POST',
        fields : {
          key: config.key,
          AWSAccessKeyId: config.aws_key_id, 
          acl: config.acl,
          policy: config.policy,
          signature: config.signature,
          //"Content-Type": config.mime_type,
          //filename: $scope.file.name
        },
        file: $scope.file,
      }).progress(function (evt) {
        $scope.uploadPercent = Math.max(1, parseInt(95.0 * evt.loaded / evt.total));
      }).success(function (data, status, headers, conf) {
        // trigger a load by telling the backend there's now a file.
        $http.post(dataset.api_url + '/sources/load/' + config.source_name).then(function() {
          uploadDone();
        });  
      }).error(function (data, status, headers, conf) {
        $scope.uploads = [];
        $scope.uploadPercent = null;
        flash.setMessage("There was an error uploading your file. Please try again.", "danger");
      });
  };

  $scope.uploadFile = function() {
    if (!$scope.hasFile()) return;
    $scope.uploadPercent = 1;

    var sign = {file_name: $scope.file.name, mime_type: $scope.file.type};
    $http.post(dataset.api_url + '/sources/sign', sign).then(function(res) {
      if (res.data.status == 'ok') {
        $scope.uploadBucket(res.data);
      } else {
        $scope.uploadServer();
      }
    });
  };

  $scope.submitUrl = function() {
    if (!$scope.hasUrl()) return;
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

