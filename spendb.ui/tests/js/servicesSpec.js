describe('styleHelper', function(){
  beforeEach( function() {
    module('spendb');
  });
  beforeEach(inject(function(flash) {
    return this.flash = flash;
  }));

  describe('#flash', function() {
    it('no default message', function() {
      expect(this.flash.getMessage()).to.eq(undefined);
    });
  });
});
