
var loadSessionAccount = ['$q', '$http', 'session', function($q, $http, session) {
  var dfd = $q.defer();
  session.get(function(s) {
    $http.get('/api/3/accounts/' + s.user.name).then(function(res) {
      dfd.resolve(res.data);
    });
  });
  return dfd.promise;
}];


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
