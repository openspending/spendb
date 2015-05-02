from flask.ext.assets import Bundle

from spendb.core import assets


# Javscript bundles

js_vendor = Bundle('vendor/jquery/dist/jquery.js',
                   'vendor/moment/moment.js',
                   'vendor/angular/angular.js',
                   'vendor/angular-route/angular-route.js',
                   'vendor/angular-moment/angular-moment.js',
                   'vendor/chosen/chosen.jquery.js',
                   'vendor/ng-file-upload/ng-file-upload-all.js',
                   'vendor/angular-chosen-localytics/chosen.js',
                   'vendor/angular-bootstrap/ui-bootstrap-tpls.js',
                   'vendor/angular-cookies/angular-cookies.js')

js_base = Bundle(js_vendor,
                 'js/app.js',
                 'js/loaders.js',
                 'js/services.js',
                 'js/directives.js',
                 'js/controllers.js',
                 filters='uglifyjs', output='prod/base.js')
assets.register('js_base', js_base)


# CSS / Stylesheet bundles

css_main = Bundle('style/base.less',
                  'style/views.less',
                  filters='less,cssmin',
                  output='prod/main.css')

assets.register('css_main', css_main)

css_embed = Bundle(css_main,
                   'style/embed.less',
                   filters='less,cssmin',
                   output='prod/embed.css')

assets.register('css_embed', css_embed)
