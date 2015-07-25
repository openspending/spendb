import os

from flask.ext.assets import Bundle

from spendb.core import assets


def iter_assets(app, folder):
    partials_dir = os.path.join(app.static_folder, folder)
    for (root, dirs, files) in os.walk(partials_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            rel_name = file_path[len(partials_dir) + 1:]
            yield file_path, rel_name


# CSS / Stylesheet bundles
css_main = Bundle('style/base.less',
                  filters='less,cssmin,cssrewrite',
                  output='prod/main.css')
assets.register('css_main', css_main)


# Javscript bundles
js_vendor = Bundle('vendor/moment/moment.js',
                   'vendor/d3/d3.js',
                   'vendor/d3-plugins/sankey/sankey.js',
                   'vendor/vega-lite/lib/vega.min.js',
                   'vendor/vega-lite/vega-lite.js',
                   'vendor/angular/angular.js',
                   'vendor/angular-route/angular-route.js',
                   'vendor/angular-moment/angular-moment.js',
                   'vendor/angular-scroll/angular-scroll.js',
                   'vendor/angular-cookies/angular-cookies.js',
                   'vendor/angular-ui-select/dist/select.js',
                   'vendor/angular-filter/dist/angular-filter.js',
                   'vendor/ng-file-upload/ng-file-upload-shim.js',
                   'vendor/ng-file-upload/ng-file-upload.js',
                   'vendor/angular-bootstrap/ui-bootstrap-tpls.min.js',
                   'vendor/babbage.ui/dist/babbage.ui.js',
                   filters='uglifyjs', output='prod/vendor.js')


def register_scripts(app):
    if 'js_vendor' not in assets:
        assets.register('js_vendor', js_vendor)
    if 'js_app' not in assets:
        scripts = ['js/' + b for (a, b) in iter_assets(app, 'js')
                   if b != 'app.js']
        js_app = Bundle('js/app.js', *scripts,
                        filters='uglifyjs', output='prod/app.js')
        assets.register('js_app', js_app)


# Angular templates
def angular_templates(app):
    """ Find all angular templates and make them available in a variable
    which can be included in a Jinja template so that angular can load
    templates without doing a server round trip. """
    for file_path, file_name in iter_assets(app, 'templates'):
        with open(file_path, 'rb') as fh:
            yield (file_name, fh.read().decode('utf-8'))
