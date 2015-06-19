from flask.ext.assets import Bundle

from spendb.core import assets


# Javscript bundles

js_vendor = Bundle('vendor/jquery/dist/jquery.js',
                   'vendor/moment/moment.js',
                   'vendor/speakingurl/speakingurl.min.js',
                   'vendor/angular/angular.js',
                   'vendor/angular-route/angular-route.js',
                   'vendor/angular-moment/angular-moment.js',
                   'vendor/angular-scroll/angular-scroll.js',
                   'vendor/angular-truncate/src/truncate.js',
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
                 'js/dataset_list.js',
                 'js/pager.js',
                 'js/account_login.js',
                 'js/account_reset.js',
                 'js/account_settings.js',
                 'js/account_profile.js',
                 'js/dataset_index.js',
                 'js/admin.js',
                 filters='uglifyjs', output='prod/base.js')
assets.register('js_base', js_base)


# CSS / Stylesheet bundles

css_main = Bundle('style/base.less',
                  filters='less,cssmin,cssrewrite',
                  output='prod/main.css')

assets.register('css_main', css_main)
