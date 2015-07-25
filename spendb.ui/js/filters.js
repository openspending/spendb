ngBabbage.filter('formatDate', function() {
  var format = d3.time.format("%d.%m.%Y");
  return function(val) {
    var date = new Date(Date.parse(val));
    return format(date);
  };
});
