export FLASK_APP=myflask
nohup python3 -m flask run --host=0.0.0.0 --port=8082 > service.out  2>&1 &
