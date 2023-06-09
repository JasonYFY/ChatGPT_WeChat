export FLASK_APP=myflask
nohup flask run --host=0.0.0.0 --port=8082 >> nohup.out  2>&1 &
