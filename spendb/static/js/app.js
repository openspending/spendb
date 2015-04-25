
var spendb = angular.module('spendb', ['ngCookies', 'ngRoute', 'ui.bootstrap', 'localytics.directives']);


spendb.controller('AppCtrl', ['$scope', '$location', '$http', '$cookies', '$window', '$sce', 'flash', 'session',
  function($scope, $location, $http, $cookies, $window, $sce, flash, session) {
  
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

  // Allow SCE escaping in the app
  $scope.trustAsHtml = function(text) {
    return $sce.trustAsHtml('' + text);
  };

  session.get(function(s) {
    $scope.session = s;
  });

}]);


spendb.factory('flash', ['$rootScope', function($rootScope) {
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


spendb.factory('validation', ['flash', function(flash) {
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


spendb.factory('data', ['$http', function($http) {
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


spendb.factory('session', ['$http', function($http) {
  var sessionDfd = $http.get('/api/3/sessions');
  return {
    'get': function(cb) {
      sessionDfd.then(function(res) {
        cb(res.data);
      });  
    }
  }
}]);


spendb.controller('DatasetNewCtrl', ['$scope', '$http', '$window', 'data', 'validation',
  function($scope, $http, $window, data, validation) {
  /* This controller is not activated via routing, but explicitly through the 
  dataset.new flask route. */
  
  $scope.reference = {};
  $scope.dataset = {'category': 'budget', 'territories': []};

  data.get(function(reference) {
    $scope.reference = reference;
  });

  $scope.save = function(form) {
    var dfd = $http.post('/api/3/datasets', $scope.dataset);
    dfd.then(function(res) {
      $window.location.href = '/datasets/' + res.data.name;
    }, validation.handle(form));
  };

}]);


spendb.config(['$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {

  $routeProvider.when('/datasets/:dataset/manage', {
    templateUrl: '/static/templates/dataset/manage.html',
    controller: 'DatasetManageCtrl',
    resolve: {
      dataset: loadDataset
    }
  });

  $routeProvider.when('/datasets/:dataset/manage/meta', {
    templateUrl: '/static/templates/dataset/meta.html',
    controller: 'DatasetMetaCtrl',
    resolve: {
      dataset: loadDataset,
      reference: loadReferenceData
    }
  });

  $routeProvider.when('/datasets/:dataset/manage/model', {
    templateUrl: '/static/templates/dataset/model.html',
    controller: 'DatasetModelCtrl',
    resolve: {
      dataset: loadDataset
    }
  });

  // Router hack to enable plain old links. 
  angular.element("a").prop("target", "_self");
  $locationProvider.html5Mode(true);

}]);
