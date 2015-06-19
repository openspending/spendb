
spendb.controller('AccountSettingsCtrl', ['$scope', '$http', '$location', 'validation', 'account', 'flash',
  function($scope, $http, $location, validation, account, flash) {
  $scope.setTitle("Account Settings");
  $scope.account = account;

  $scope.save = function(form) {
    $http.post(account.api_url, $scope.account).then(function(res) {
      flash.setMessage("Your changes have been saved!", "success");
      validation.clear(form);
    }, validation.handle(form));
  };

}]);
