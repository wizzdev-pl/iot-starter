import machine
import picoweb
import ujson
import ulogging as logging
import ure as re
import utime

from common import config

app = picoweb.WebApp(__name__)
hooks = {}

CONFIGURE_DEVICE_HOOK = 'CONFIGURE_WIFI'
CONFIGURE_AWS_HOOK = 'CONFIGURE_AWS'
CONFIGURE_SENSOR_HOOK = "CONFIGURE_SENSOR"
GET_STATUS_HOOK = 'GET_STATUS'


# API helpers
def create_success_response(data: dict):
    return _create_common_response(data=data, status=0, status_text='ok')


def _create_common_response(data, status: int, status_text: str):
    response_dict = {
        'data': data,
        'status': status,
        'status_text': status_text,
    }
    encoded = ujson.dumps(response_dict)
    return encoded


def create_failed_response(resp, status_text: str, status: int = 500):
    return _create_common_response(data=None, status=status, status_text=status_text)


# modified picoweb's req.read_form_data:
def parse_post_body(req):
    size = int(req.headers[b"Content-Length"])
    data = yield from req.reader.readexactly(size)
    data_txt = data.decode('utf-8')
    return ujson.loads(data_txt)


# Requests handling
@app.route("/status")
def get_status(req, resp):
    data = {"timestamp": utime.time()}
    status = hooks[GET_STATUS_HOOK]()
    for key in status.keys():
        data[key] = status[key]
    encoded = create_success_response(data=data)
    yield from picoweb.start_response(resp, content_type="application/json")
    yield from resp.awrite(encoded)


@app.route("/measurement")
def get_last_measurement(req, resp):
    value = hooks['get_measurement_hook']()
    data = {"value": value}

    encoded = create_success_response(data=data)
    yield from picoweb.start_response(resp, content_type="application/json")
    yield from resp.awrite(encoded)


@app.route("/battery")
def get_last_measurement(req, resp):
    assert req.method == 'GET'
    try:
        battery_v = machine.ADC(machine.Pin(config.cfg.battery_voltage_pin))
        battery_v.atten(machine.ADC.ATTN_11DB)
        ADC_11DB_TO_VOLT = 0.000805664
        voltage = battery_v.read() * ADC_11DB_TO_VOLT

        voltage_divider_ratio = config.cfg.voltage_divider_r2_k / \
            (config.cfg.voltage_divider_r1_k + config.cfg.voltage_divider_r2_k)

        voltage = voltage / voltage_divider_ratio
    except:
        logging.info("Error reading battery voltage!")
        voltage = 'ERROR'
    data = {"voltage": voltage}

    encoded = create_success_response(data=data)
    yield from picoweb.start_response(resp, content_type="application/json")
    yield from resp.awrite(encoded)


@app.route("/")
def index(req, resp):
    print("route /")
    headers = {"Location": "/web_pages/index.html"}
    yield from picoweb.start_response(resp, status="303", headers=headers)


@app.route("/config")
def set_config(req, resp):
    assert req.method == 'POST'
    data = yield from parse_post_body(req)
    print(data)

    if 'wifi' in data.keys():
        print(data['wifi'])
        hooks[CONFIGURE_DEVICE_HOOK](data['wifi'])
    if 'aws' in data.keys():
        hooks[CONFIGURE_AWS_HOOK](data['aws'])
    if 'sensor' in data.keys():
        hooks[CONFIGURE_SENSOR_HOOK](data['sensor'])

    config.cfg.save()

    response_data = {'result': 'ok'}
    encoded = create_success_response(data=response_data)
    yield from picoweb.start_response(resp, content_type="application/json")
    yield from resp.awrite(encoded)


@app.route(re.compile("/web_pages/(.+)"))
def get_static_file(req, resp):
    print("Get static call")
    file_path = '/web_server/web_pages/' + req.url_match.group(1)
    logging.info('About to send file: ' + file_path)
    yield from app.sendfile(resp, file_path)


@app.route(re.compile("/start_test_data_acquisition"))
def start_test_data_acquisition(req, resp):
    hooks['start_test_data_acquisition']()

    response_data = {'result': 'ok'}
    encoded = create_success_response(data=response_data)
    yield from picoweb.start_response(resp, content_type="application/json")
    yield from resp.awrite(encoded)


@app.route(re.compile("/start_data_acquisition"))
def start_data_acquisition(req, resp):
    hooks['start_data_acquisition']()

    response_data = {'result': 'ok'}
    encoded = create_success_response(data=response_data)
    yield from picoweb.start_response(resp, content_type="application/json")
    yield from resp.awrite(encoded)


# setup and run
def setup(get_measurement_hook=None,
          configure_device_hook=None,
          configure_aws_hook=None,
          configure_sensor_hook=None,
          get_status_hook=None,
          start_test_data_acquisition=None,
          start_data_acquisition=None):
    global hooks
    hooks['get_measurement_hook'] = get_measurement_hook
    hooks[CONFIGURE_DEVICE_HOOK] = configure_device_hook
    hooks[CONFIGURE_AWS_HOOK] = configure_aws_hook
    hooks[CONFIGURE_SENSOR_HOOK] = configure_sensor_hook
    hooks[GET_STATUS_HOOK] = get_status_hook
    hooks['start_test_data_acquisition'] = start_test_data_acquisition
    hooks['start_data_acquisition'] = start_data_acquisition


def run():
    global app
    global hooks

    if not hooks:
        raise Exception('Please setup server with hooks first!')

    logging.info('About to start server...')
    app.run(debug=1, port=80, host='0.0.0.0')


def stop_server():
    app.stop_server()
