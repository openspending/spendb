
spendb.controller('DatasetEditCtrl', ['$scope', '$document', '$http', '$location', '$q', 'flash', 'reference', 'validation', 'dataset', 'managers', 'session',
  function($scope, $document, $http, $location, $q, flash, reference, validation, dataset, managers, session) {
  $scope.dataset = dataset;
  $scope.reference = reference;
  $scope.managers = managers;
  $scope.forms = {};
  $scope.session = session;

  $scope.suggestAccounts = function(query) {
    var dfd = $q.defer(),
        params =  {q: query};
    $http.get('/api/3/accounts/_complete', {params: params}).then(function(es) {
      var accounts = []
      for (var i in es.data.results) {
        var account = es.data.results[i],
            seen = false;
        for (var j in $scope.managers.managers) {
          var other = $scope.managers.managers[j];
          if (other.name == account.name) {
            seen = true;
          }
        }
        if (!seen) {
          accounts.push(account);
        }
      }
      dfd.resolve(accounts);
    });
    return dfd.promise;
  };

  $scope.addAccount = function() {
    if ($scope.managers.fresh && $scope.managers.fresh.name) {
      $scope.managers.managers.push($scope.managers.fresh);
      $scope.managers.fresh = null;
    }
  };

  $scope.removeAccount = function(account) {
    var idx = $scope.managers.managers.indexOf(account);
    if (idx != -1) {
      $scope.managers.managers.splice(idx, 1);
    }
  };

  $scope.canSave = function() {
    return true;
  };

  $scope.upload = function() {
    $location.path('/datasets/' + dataset.name + '/upload');
  };

  $scope.save = function() {
    var dfd = $http.post(dataset.api_url, $scope.dataset);
    validation.clear($scope.forms.dataset);
    dfd.then(function(res) {
      $scope.dataset = res.data;
      $http.post(dataset.api_url + '/managers', $scope.managers).then(function(res) {
        $scope.managers = res.data;
        if ($scope.wizard) {
          $location.path('/datasets/' + dataset.name + '/sources');
        } else {
          flash.setMessage("Your changes have been saved!", "success");
        }
        $scope.resetScroll();
      });
    }, validation.handle($scope.forms.dataset));
  };

}]);

