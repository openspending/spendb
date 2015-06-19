angular.module('spendb.config', []).constant('config', SPENDB_CONFIG);

var spendb = angular.module('spendb', ['spendb.config', 'ngCookies', 'ngRoute', 'duScroll', 'ngFileUpload',
                                       'angularMoment', 'ui.bootstrap', 'localytics.directives', 'truncate']);


spendb.config(['$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {

  $routeProvider.when('/', {
    templateUrl: 'home.html',
    controller: 'HomeCtrl',
    reloadOnSearch: true,
    resolve: {
      page: loadIndex,
      datasets: loadIndexDatasets
    }
  });

  $routeProvider.when('/login', {
    templateUrl: 'account_login.html',
    controller: 'AccountLoginCtrl',
    resolve: {}
  });

  $routeProvider.when('/settings', {
    templateUrl: 'account_settings.html',
    controller: 'AccountSettingsCtrl',
    resolve: {
      account: loadSessionAccount
    }
  });

  $routeProvider.when('/docs/:path', {
    templateUrl: 'docs.html',
    controller: 'DocsCtrl',
    resolve: {
      page: loadPage
    }
  });

  $routeProvider.when('/accounts/:account', {
    templateUrl: 'account_profile.html',
    controller: 'AccountProfileCtrl',
    reloadOnSearch: true,
    resolve: {
      profile: loadProfile
    }
  });

  $routeProvider.when('/datasets', {
    templateUrl: 'dataset_index.html',
    controller: 'DatasetIndexCtrl',
    reloadOnSearch: true,
    resolve: {
      datasets: loadIndexDatasets
    }
  });

  $routeProvider.when('/datasets/new', {
    templateUrl: 'new.html',
    controller: 'NewCtrl',
    resolve: {
      session: loadSession,
      reference: loadReferenceData
    }
  });

  $routeProvider.when('/datasets/:dataset', {
    templateUrl: 'dataset_view.html',
    controller: 'DatasetViewCtrl',
    reloadOnSearch: false,
    resolve: {
      dataset: loadDataset
    }
  });

  $routeProvider.when('/datasets/:dataset/admin/data', {
    templateUrl: 'admin/data.html',
    controller: 'AdminDataCtrl',
    resolve: {
      dataset: loadDataset
    }
  });

  $routeProvider.when('/datasets/:dataset/admin/runs/:run', {
    templateUrl: 'admin/run.html',
    controller: 'AdminRunCtrl',
    resolve: {
      dataset: loadDataset,
      run: loadRun
    }
  });

  $routeProvider.when('/datasets/:dataset/admin/metadata', {
    templateUrl: 'admin/metadata.html',
    controller: 'AdminMetadataCtrl',
    resolve: {
      dataset: loadDataset,
      reference: loadReferenceData,
      managers: loadManagers
    }
  });

  $routeProvider.when('/datasets/:dataset/admin/model', {
    templateUrl: 'admin/model.html',
    controller: 'AdminModelCtrl',
    resolve: {
      dataset: loadDataset,
      data: loadModel
    }
  });

  $locationProvider.html5Mode(true);
}]);


spendb.controller('AppCtrl', ['$scope', '$location', '$http', '$cookies', '$window', '$document', '$sce', 'flash', 'session', 'config',
  function($scope, $location, $http, $cookies, $window, $document, $sce, flash, session, config) {
  
  $scope.flash = flash;
  $scope.session = {};

  // EU cookie warning
  $scope.showCookieWarning = !$cookies.neelieCookie;

  $scope.hideCookieWarning = function() {
    $cookies.neelieCookie = true;
    $scope.showCookieWarning = !$cookies.neelieCookie;
  };

  // Language selector
  $scope.setLocale = function(locale) {
    $http.post('/set-locale', {'locale': locale}).then(function(res) {
      $window.location.reload();
    });
    return false;
  };

  $scope.setTitle = function(title) {
    angular.element('#page-title').html(title);
    angular.element('title').html(title + ' - ' + config.site_title);
  };

  // reset the page.
  $scope.resetScroll = function() {
    var elem = angular.element(document.getElementsByTagName('body'));
    $document.scrollToElement(elem, 0, 300);
  };

  // Allow SCE escaping in the app
  $scope.trustAsHtml = function(text) {
    return $sce.trustAsHtml('' + text);
  };

  // Logout
  $scope.logout = function() {
    session.logout(function(s) {
      $scope.session = s;
      $location.path('/');
    });
  };

  session.get(function(s) {
    if (s.logged_in) {
      $scope.hideCookieWarning();
    }
    $scope.session = s;
  });

}]);


var loadPage = ['$q', '$route', '$http', function($q, $route, $http) {
  var dfd = $q.defer();
  $http.get('/api/3/pages/' + $route.current.params.path).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


spendb.controller('DocsCtrl', ['$scope', '$sce', 'page', function($scope, $sce, page) {
  $scope.setTitle(page.title);
  $scope.page = page;
  $scope.page_html = $sce.trustAsHtml('' + page.html);
}]);


var loadIndex = ['$q', '$route', '$http', function($q, $route, $http) {
  var dfd = $q.defer();
  // yes that's what baby jesus made APIs for.
  $http.get('/api/3/pages/index.html').then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


var loadIndexDatasets = ['$q', '$http', '$location', '$route', function($q, $http, $location, $route) {
  var dfd = $q.defer();
  $http.get('/api/3/datasets', {params: $location.search()}).then(function(res) {
    dfd.resolve(res.data);
  });
  return dfd.promise;
}];


spendb.controller('HomeCtrl', ['$scope', '$sce', 'page', 'datasets', function($scope, $sce, page, datasets) {
  $scope.setTitle(page.title);
  $scope.page = page;
  $scope.datasets = datasets;
  $scope.page_html = $sce.trustAsHtml('' + page.html);
}]);
