

spendb.controller('DatasetIndexCtrl', ['$scope', '$location', 'datasets', function($scope, $location, datasets) {
  $scope.setTitle('Datasets in our store');
  $scope.datasets = datasets;

  $scope.hasFacet = function(name, value) {
    var query = $location.search();
    if (angular.isArray(query[name])) {
      return query[name].indexOf(value) != -1;
    }
    return query[name] == value;
  };

  $scope.toggleFacet = function(name, value) {
    var query = $location.search(),
        isArray = angular.isArray(query[name]);
    if ($scope.hasFacet(name, value)) {
      if (isArray) {
        query[name].splice(query[name].indexOf(value), 1);
      } else {
        delete query[name];
      }
    } else {
      if (isArray) {
        query[name].push(value);
      } else if (query[name]) {
        query[name] = [query[name], value]; 
      } else {
        query[name] = value;
      }
    }
    if (query.offset) {
      delete query['offset'];
    }
    $location.search(query);
  };

}]);
