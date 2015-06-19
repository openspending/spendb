
var loadProfile = ['$q', '$http', '$route', function($q, $http, $route) {
  var url = '/api/3/accounts/' + $route.current.params.account,
      dfd = $q.defer();
  $q.all([
    $http.get('/api/3/accounts/' + $route.current.params.account),
    $http.get('/api/3/datasets', {params: {account: $route.current.params.account}})
  ]).then(function(data) {
    dfd.resolve({
      account: data[0].data,
      datasets: data[1].data
    });
  });
  return dfd.promise;
}];


spendb.controller('AccountProfileCtrl', ['$scope', '$http', '$location', 'session', 'profile',
  function($scope, $http, $location, session, profile) {
  $scope.setTitle(profile.account.display_name);
  $scope.account = profile.account;
  $scope.own_profile = false;
  $scope.datasets = profile.datasets;

  session.get(function(sess) {
    $scope.own_profile = sess.logged_in && sess.user.name == profile.account.name;
  });

}]);
