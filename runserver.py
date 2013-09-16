from okcreeper import app

if __name__ == '__main__':
    app.debug = True
    app.config['asset_url'] = '/static/'
    app.run()