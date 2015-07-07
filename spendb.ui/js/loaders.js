var loadSession = ['$q', 'session', function($q, session) {
  var dfd = $q.defer();
  session.get(function(s) {
    dfd.resolve(s);
  });
  return dfd.promise;
}];


var loadDataset = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      url = '/api/3/datasets/' + $route.current.params.dataset,
      authzUrl = '/api/3/sessions/authz',
      authzParams = {'dataset': $route.current.params.dataset};
  $q.all([
    $http.get(url),
    $http.get(authzUrl, {params: authzParams})
  ]).then(function(data) {
    var dataset = data[0].data,
        authz = data[1].data;
    dataset.can_read = authz.read;
    dataset.can_update = authz.update;
    dfd.resolve(dataset);
  });
  return dfd.promise;
}];


var loadManagers = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      url = '/api/3/datasets/' + $route.current.params.dataset + '/managers';
  $http.get(url).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


var loadReferenceData = ['$q', 'data', function($q, data) {
  var dfd = $q.defer();
  data.get(function(rd) {
    dfd.resolve(rd);
  });
  return dfd.promise;
}];


var loadModel = ['$route', '$q', '$http', function($route, $q, $http) {
  var url = '/api/3/datasets/' + $route.current.params.dataset,
      dfd = $q.defer();
  $q.all([
    $http.get(url + '/structure'),
    $http.get(url + '/model')
  ]).then(function(data) {
    dfd.resolve({
      structure: data[0].data,
      model: data[1].data
    });
  });
  return dfd.promise;
}];
