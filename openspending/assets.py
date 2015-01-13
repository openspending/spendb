from flask.ext.assets import Bundle

from openspending.core import assets


# Javscript bundles

js_vendor = Bundle('vendor/angular/angular.js',
                   'vendor/angular-bootstrap/ui-bootstrap-tpls.js',
                   'vendor/angular-cookies/angular-cookies.js')

js_base = Bundle(js_vendor,
                 'js/app.js',
                 filters='uglifyjs', output='prod/base.js')
assets.register('js_base', js_base)


# CSS / Stylesheet bundles

css_main = Bundle('style/base.less',
                  'style/bs2_style.less',
                  'style/views.less',
                  filters='less,cssmin',
                  output='prod/main.css')

assets.register('css_main', css_main)

css_embed = Bundle(css_main,
                   'style/embed.less',
                   filters='less,cssmin',
                   output='prod/embed.css')

assets.register('css_embed', css_embed)
