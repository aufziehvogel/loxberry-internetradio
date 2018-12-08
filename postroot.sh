pluginfoldername=$3

cp /opt/loxberry/data/plugins/$pluginfoldername/supervisor.conf /etc/supervisor/conf.d/internetradio.conf

supervisorctl reread
supervisorctl start internetradio
