var loadSession = ['$q', 'session', function($q, session) {
  var dfd = $q.defer();
  session.get(function(s) {
    dfd.resolve(s);
  });
  return dfd.promise;
}];


var loadDataset = ['$route', '$http', '$q', function($route, $http, $q) {
  var dfd = $q.defer(),
      url = '/api/3/datasets/' + $route.current.params.dataset;
  $http.get(url).then(function(res) {
    dfd.resolve(res.data);
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


var loadRun = ['$route', '$q', '$http', function($route, $q, $http) {
  var p = $route.current.params,
      url = '/api/3/datasets/' + p.dataset + '/runs/' + p.run;
  return $http.get(url);
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

