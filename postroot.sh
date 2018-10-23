cp /opt/loxberry/data/plugins/$pluginname/supervisor.conf /etc/supervisor/conf.d/internetradio.conf

supervisorctl reread
supervisorctl start internetradio
