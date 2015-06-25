
var loadProfile = ['$q', '$http', '$location', '$route', function($q, $http, $location, $route) {
  var url = '/api/3/accounts/' + $route.current.params.account,
      dfd = $q.defer(),
      account = $route.current.params.account,
      params = angular.extend({}, $location.search(), {account: account});
  $q.all([
    $http.get('/api/3/accounts/' + account),
    $http.get('/api/3/datasets', {params: params})
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
