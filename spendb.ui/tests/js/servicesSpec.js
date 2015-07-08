describe('styleHelper', function(){
  beforeEach( function() {
    module('spendb');
  });
  beforeEach(inject(function(validation) {
    return this.validation = validation;
  }));

  // describe('#validation', function() {
  //   it('makes a slug', function() {
  //     expect(this.validation.makeSlug('test test')).to.eq('test_test');
  //   });
  // });
});
