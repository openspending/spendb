
var openspending = angular.module('openspending', ['ngCookies', 'ngRoute', 'ui.bootstrap', 'localytics.directives']);

openspending.handleValidation = function(form) {
  return function(res) {
    if (res.status == 400) {
        var errors = [];
        console.log(res.data.errors);
        for (var field in res.data.errors) {
            form[field].$setValidity('value', false);
            form[field].$message = res.data.errors[field];
            errors.push(field);
        }
        if (angular.isDefined(form._errors)) {
            angular.forEach(form._errors, function(field) {
                if (errors.indexOf(field) == -1) {
                    form[field].$setValidity('value', true);
                }
            });
        }
        form._errors = errors;
    } else {
      console.log(res)
    }
  };
};


openspending.controller('AppCtrl', ['$scope', '$location', '$http', '$cookies', '$window', '$sce',
  function($scope, $location, $http, $cookies, $window, $sce) {
  
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

  // Allow SCE escaping in the app
  $scope.trustAsHtml = function(text) {
    return $sce.trustAsHtml('' + text);
  };

}]);


openspending.factory('referenceData', ['$http', function($http) {
  /* This is used to cache reference data once it has been retrieved from the 
  server. Reference data includes the canonical lists of country names,
  currencies, etc. */
  var referenceData = $http.get('/api/3/reference');

  var getData = function(cb) {
    referenceData.then(function(res) {
      cb(res.data);
    });
  };

  return {'get': getData}
}]);


openspending.controller('DatasetNewCtrl', ['$scope', '$http', '$window', 'referenceData',
  function($scope, $http, $window, referenceData) {
  /* This controller is not activated via routing, but explicitly through the 
  dataset.new flask route. */
  
  $scope.reference = {};
  $scope.canCreate = false;
  $scope.dataset = {'category': 'budget', 'territories': []};

  referenceData.get(function(reference) {
    $scope.reference = reference;
  });

  $scope.save = function(form) {
    var dfd = $http.post('/api/3/datasets', $scope.dataset);
    dfd.then(function(res) {
      $window.location.href = '/' + res.data.name + '/meta';
    }, openspending.handleValidation(form));
  };

  $http.get('/api/2/permissions?dataset=new').then(function(res) {
    $scope.canCreate = res.data.create;
  });

}]);


openspending.controller('DatasetManageCtrl', ['$scope', '$http', '$window',
  function($scope, $http, $window, referenceData) {
  
  $scope.dataset = {};

}]);


openspending.controller('DatasetMetaCtrl', ['$scope', '$http', '$window', 'referenceData',
  function($scope, $http, $window, referenceData) {
  
  $scope.reference = {};
  $scope.dataset = {};

  referenceData.get(function(reference) {
    $scope.reference = reference;
  });

  $scope.save = function(form) {
  };

}]);


openspending.controller('DatasetModelCtrl', ['$scope', '$http', '$window',
  function($scope, $http, $window, referenceData) {
  
  $scope.dataset = {};

  $scope.save = function(form) {
  };

}]);


openspending.config(['$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {

  $routeProvider.when('/:name/manage', {
    templateUrl: '/static/templates/dataset_manage.html',
    controller: 'DatasetManageCtrl'
  });

  $routeProvider.when('/:name/manage/meta', {
    templateUrl: '/static/templates/dataset_meta.html',
    controller: 'DatasetMetaCtrl'
  });

  $routeProvider.when('/:name/manage/model', {
    templateUrl: '/static/templates/dataset_model.html',
    controller: 'DatasetModelCtrl'
  });

  $locationProvider.html5Mode(true);

}]);
