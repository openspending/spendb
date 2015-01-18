
var openspending = angular.module('openspending', ['ngCookies', 'ngRoute', 'ui.bootstrap', 'localytics.directives']);


openspending.controller('AppCtrl', ['$scope', '$location', '$http', '$cookies', '$window', '$sce', 'flash',
  function($scope, $location, $http, $cookies, $window, $sce, flash) {
  
  $scope.flash = flash;

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


openspending.factory('flash', ['$rootScope', function($rootScope) {
  // Message flashing.
  var currentMessage = null;

  $rootScope.$on("$routeChangeSuccess", function() {
    currentMessage = null;
  });

  return {
    setMessage: function(message, type) {
      currentMessage = [message, type];
    },
    getMessage: function() {
      return currentMessage;
    }
  };
}]);


openspending.factory('validation', ['flash', function(flash) {
  // handle server-side form validation errors.
  return {
    handle: handle = function(form) {
      return function(res) {
        if (res.status == 400 || !form) {
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
          flash.setMessage(res.data.message || res.data.title || 'Server error', 'danger');
        }
      }
    }
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


openspending.controller('DatasetNewCtrl', ['$scope', '$http', '$window', 'referenceData', 'validation',
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
    }, validation.handle(form));
  };

  $http.get('/api/2/permissions?dataset=new').then(function(res) {
    $scope.canCreate = res.data.create;
  });

}]);


openspending.controller('DatasetManageCtrl', ['$scope', '$http', '$window', '$routeParams',
  function($scope, $http, $window, $routeParams) {
  var datasetApi = '/api/3/datasets/' + $routeParams.name;
  
  $scope.dataset = {};

  $http.get(datasetApi).then(function(res) {
      $scope.dataset = res.data;
  });

}]);


openspending.controller('DatasetMetaCtrl', ['$scope', '$http', '$location', '$routeParams', 'referenceData', 'flash', 'validation',
  function($scope, $http, $location, $routeParams, referenceData, flash, validation) {
  var datasetApi = '/api/3/datasets/' + $routeParams.name;

  $scope.reference = {};
  $scope.dataset = {};

  referenceData.get(function(reference) {
    $scope.reference = reference;
    // delay loading the dataset so that the selects are populated.
    $http.get(datasetApi).then(function(res) {
      $scope.dataset = res.data;

    });
  });

  $scope.save = function(form) {
    var dfd = $http.post(datasetApi, $scope.dataset);
    dfd.then(function(res) {
      $scope.dataset = res.data;
      flash.setMessage("Your changes have been saved!", "success");
    }, validation.handle(form));
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

  // Router hack to enable plain old links. 
  angular.element("a").prop("target", "_self");

  $locationProvider.html5Mode(true);

}]);
