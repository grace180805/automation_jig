import sys
import os

from api.src.common.testrail_tool import update_testrun_in_plan_cases, clone_testrun_to_plan, add_cases_to_test_run, \
    get_unpassed_case_lst, get_aa_test_case_list, send_result_to_test_rail, get_test_run_details, add_plan, \
    get_plan_ids, add_run_to_plan, update_plan_entry_name, get_test_run_results, get_user

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ssl

from flask import request, jsonify
from flask import Flask
from flask_mqtt import Mqtt

import config

from database import Jig, LockAndDoorSteps, add_or_update_jig
from api_enum_data import OperationEnum, LockAndDoorStatus, Message

import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)

if not app.debug:
    handler = RotatingFileHandler('api_server.log', maxBytes=10000, backupCount=3)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

# method 1
# app.config['MQTT_BROKER_URL'] = config.configure["mqtt_host"]
# app.config['MQTT_BROKER_PORT'] = 8883
# app.config['MQTT_CLIENT_ID'] = 'server'
# app.config['MQTT_TLS_VERSION'] = ssl.PROTOCOL_TLS
# app.config['MQTT_USERNAME'] = config.configure["mqtt_user"]  # Set this item when you need to verify username and password
# app.config['MQTT_PASSWORD'] = config.configure["mqtt_pwd"]  # Set this item when you need to verify username and password
# # app.config['MQTT_KEEPALIVE'] = 60  # Set KeepAlive time in seconds
# app.config['MQTT_TLS_ENABLED'] = True  # If your broker supports TLS, set it True


# method 2
app.config['MQTT_BROKER_URL'] = config.configure["mqtt_host"]  # URL for HiveMQ cluster
app.config['MQTT_USERNAME'] = config.configure["mqtt_user"]  # From the credentials created in HiveMQ
app.config['MQTT_PASSWORD'] = config.configure["mqtt_pwd"]  # From the credentials created in HiveMQ
app.config['MQTT_CLIENT_ID'] = 'test'  # Must be unique for any client that connects to the cluster
app.config['MQTT_BROKER_PORT'] = 8883  # MQTT port for encrypted traffic
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = True
app.config['MQTT_TLS_INSECURE'] = False
app.config['MQTT_TLS_CA_CERTS'] = 'MQTT/isrgrootx1.pem'  # CA for HiveMQ, read: https://letsencrypt.org/about/
app.config['MQTT_TLS_VERSION'] = ssl.PROTOCOL_TLSv1_2
app.config['MQTT_TLS_CIPHERS'] = None
app.config['MQTT_LAST_WILL_QOS'] = 2

topic = '#'
mqtt_client = Mqtt(app)


# received_messages = []


@mqtt_client.on_connect()
def handle_connect(client, userdata, flags, rc):
    if rc == 0:
        # print('Connected successfully')
        mqtt_client.subscribe(topic)  # subscribe topic
    else:
        print('Bad connection. Code:', rc)


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )

    # received_messages.append(data['payload'])
    if Message.SUCCESS.value in str(message.payload):
        record = Jig.get(Jig.jig_id == message.topic[:5])
        if (OperationEnum.LOCK_FULLY_OPEN.value in message.topic) \
                or (OperationEnum.LOCK_OPEN.value in message.topic) \
                or (OperationEnum.LOCK_JUST_OPEN.value in message.topic):
            record.lock_state = LockAndDoorStatus.LOCK_UNLOCK.value

        elif (OperationEnum.LOCK_FULLY_CLOSE.value in message.topic) \
                or (OperationEnum.LOCK_CLOSE.value in message.topic) \
                or (OperationEnum.LOCK_JUST_CLOSE.value in message.topic):
            record.lock_state = LockAndDoorStatus.LOCK_LOCK.value

        elif OperationEnum.DOOR_OPEN.value in message.topic:
            record.door_state = LockAndDoorStatus.DOOR_OPEN.value
        elif OperationEnum.DOOR_AJAR.value in message.topic:
            record.door_state = LockAndDoorStatus.DOOR_AJAR.value
        elif OperationEnum.DOOR_CLOSE.value in message.topic:
            record.door_state = LockAndDoorStatus.DOOR_CLOSED.value

        record.save()

    if data['topic'].find(OperationEnum.LOCK_STATUS.value) > -1 and data['payload'].find('steps') > -1:
        msg = data['payload']
        steps = int(msg.split('=')[1])
        jig_status_record = Jig.get(Jig.jig_id == message.topic[:5])
        lock_and_door_steps_record = LockAndDoorSteps.get(LockAndDoorSteps.model == jig_status_record.model)
        if steps <= lock_and_door_steps_record.lock_just_lock_steps + 10:
            jig_status_record.lock_state = LockAndDoorStatus.LOCK_LOCK.value

        if lock_and_door_steps_record.lock_just_unlock_steps - 10 <= steps:
            jig_status_record.lock_state = LockAndDoorStatus.LOCK_UNLOCK.value
        jig_status_record.save()
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))


@app.route('/send', methods=['POST'])
def publish_message():
    request_data = request.get_json()
    jig_id = request_data["jigId"]
    print(jig_id)
    device_type = request_data["deviceType"]
    topic = request_data["topic"]
    new_topic = '/automation/{}/{}/{}'.format(jig_id, device_type, topic)
    publish_result = mqtt_client.publish(new_topic, topic, qos=2)
    return jsonify({'code': publish_result[0]})


@app.route('/jigModel', methods=['PUT'])
def jig_model_api():
    request_data = request.get_json()
    jig_id = request_data["jigId"]
    jig_model = request_data["model"]
    jig_model_options = ["forma_scan01", "forma_scan02", "forma_scan03", "forma_fin01", "forma_fin02",
                         "forma_euro01", "forma_euro02", "forma_euro03", "forma_swiss01", "forma_swiss02",
                         "forma_swiss03"]
    if jig_model not in jig_model_options:
        return jsonify({'code': 10400, 'message': 'the jig model is not existed!'})
    add_or_update_jig(jig_id, jig_model)
    new_topic = '{}/{}'.format(jig_id, OperationEnum.DOOR_CLOSE.value)
    mqtt_client.publish(new_topic, Message.MOVE.value, qos=2)
    app.logger.info("published init jig topic.")
    record = Jig.get(Jig.jig_id == jig_id)
    return jsonify({'code': 200, 'data': record.model, 'message': 'success'})


# def get_angel(topic):
#     return {
#         'door/close': '1',
#         'door/ajar': '2',
#         'door/open': '3'
#     }.get(topic, 'error')
# 'error' is default value, can set by yourself

@app.route('/sendTopic', methods=['POST'])
def send_topic_api():
    request_data = request.get_json()
    jig_id = request_data["jigId"]
    device_type = request_data["deviceType"]
    topic = request_data["topic"]
    model = Jig.select().where(Jig.jig_id == jig_id).get().model
    model_steps_row = LockAndDoorSteps.get(LockAndDoorSteps.model == model)
    steps = 0

    if topic == OperationEnum.LOCK_FULLY_OPEN.value:
        steps = model_steps_row.lock_fully_unlock_steps
    elif topic == OperationEnum.LOCK_OPEN.value:
        steps = model_steps_row.lock_unlock_steps
    elif topic == OperationEnum.LOCK_JUST_OPEN.value:
        steps = model_steps_row.lock_just_unlock_steps

    elif topic == OperationEnum.LOCK_FULLY_CLOSE.value:
        steps = model_steps_row.lock_fully_lock_steps
    elif topic == OperationEnum.LOCK_CLOSE.value:
        steps = model_steps_row.lock_lock_steps
    elif topic == OperationEnum.LOCK_JUST_CLOSE.value:
        steps = model_steps_row.lock_just_lock_steps

    elif topic == OperationEnum.DOOR_OPEN.value:
        steps = model_steps_row.door_open_steps
    elif topic == OperationEnum.DOOR_AJAR.value:
        steps = model_steps_row.door_ajar_steps
    elif topic == OperationEnum.DOOR_CLOSE.value:
        steps = model_steps_row.door_closed_steps

    new_topic = '{}/{}'.format(jig_id, topic)
    if topic != OperationEnum.LOCK_STATUS.value:
        publish_result = mqtt_client.publish(new_topic, Message.MOVE.value + '&steps=' + str(steps), qos=2)
    else:
        publish_result = mqtt_client.publish(new_topic, qos=2)

    # if not received_messages:
    #     return jsonify({"message": "No messages received"}), 404
    # latest_message = received_messages.pop(0)
    return jsonify({'code': 200, 'message': 'success'})
    # else:
    #     return jsonify({'code': 500, 'message': 'operate jig failed'})


@app.route('/lockAndDoorStatus/<jig_id>', methods=['GET'])
def status_api(jig_id):
    query = Jig.select().where(Jig.jig_id == jig_id)
    result = query.get()
    data = {'doorState': result.door_state,
            'lockState': result.lock_state,
            "jigState": result.jig_state,
            'model': result.model}
    return jsonify({'code': 200, 'data': data, 'message': 'success'})


"""
Testrail API
"""
@app.route('/updateTestrunInPlanCases', methods=['PUT'])
def update_testrun_in_plan_cases_api():
    """
    request body:
    {
        "testplanId": 123,     // target plan id
        "updateTestrunId": 456,  // target test run id
        "caseListOrTestrunId": [1, 2, 3],  // list of case ids or test run id
        "removeOrAdd": "remove"  // "remove" or "add"
    }
    :return:
    """
    try:
        request_data = request.get_json()

        if not request_data:
            raise ValueError("Invalid JSON data received.")

        testplan_id = request_data["testplanId"]
        update_testrun_id = request_data["updateTestrunId"]
        case_list_or_testrun_id = request_data["caseListOrTestrunId"]
        remove_or_add = request_data["removeOrAdd"]

        if None in [testplan_id, update_testrun_id, case_list_or_testrun_id, remove_or_add]:
            raise ValueError("Missing required parameters in JSON data.")

        update_testrun_in_plan_cases(testplan_id, update_testrun_id, case_list_or_testrun_id, remove_or_add)
        return jsonify({'code': 200, 'message': 'success'})

    except ValueError as ve:
        app.logger.error(f"Value error in updateTestrunInPlanCases API: {str(ve)}")
        return jsonify({'code': 400, 'message': str(ve)}), 400

    except Exception as e:
        app.logger.error(f"An unexpected error occurred in updateTestrunInPlanCases API: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500


@app.route('/cloneTestrunToPlan', methods=['POST'])
def clone_testrun_to_plan_api():
    """
    request body:
    {
        "copyFrom": 123,     // source test run id
        "toPlan": 456,       // target plan id
        "newTestrunName": "new test run name"  // new test run name
    :return:
    """
    try:
        request_data = request.get_json()

        if not request_data:
            raise ValueError("Invalid JSON data received.")

        source_testrun_id = request_data["copyFrom"]
        target_testplan_id = request_data["toPlan"]
        target_testrun_name = request_data["newTestrunName"]

        if None in [source_testrun_id, target_testplan_id, target_testrun_name]:
            raise ValueError("Missing required parameters in JSON data.")

        clone_testrun_to_plan(source_testrun_id, target_testplan_id, target_testrun_name)
        app.logger.info(
            f"Successfully cloned test run {source_testrun_id} to plan {target_testplan_id} with name {target_testrun_name}")
        return jsonify({'code': 200, 'message': 'success'})

    except ValueError as ve:
        app.logger.error(f"Value error in cloneTestrunToPlan API: {str(ve)}")
        return jsonify({'code': 400, 'message': str(ve)}), 400

    except Exception as e:
        app.logger.error(f"An unexpected error occurred in cloneTestrunToPlan API: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500

@app.route('/addNewCasesToTestrun', methods=['POST'])
def add_cases_to_test_run_api():
    """
    :request body:
    {
        "copyFrom": 123,
        "toPlan": 456,
        "toRun": 789
    }
    :return:
    """
    try:
        request_data = request.get_json()

        if not request_data:
            raise ValueError("Invalid JSON data received.")

        copyFrom_testrun_id = request_data["copyFrom"]
        copy_to_plan_id = request_data["toPlan"]
        copy_to_testrun_id = request_data["toRun"]

        if not all([copyFrom_testrun_id, copy_to_plan_id, copy_to_testrun_id]):
            raise ValueError("Missing required parameters in JSON data.")

        add_cases_to_test_run(copyFrom_testrun_id, copy_to_plan_id, copy_to_testrun_id)
        app.logger.info(f"Successfully added cases to test run {copy_to_testrun_id}")
        return jsonify({'code': 200, 'message': 'success'})
    except ValueError as ve:
        app.logger.error(f"Value error in addNewCasesToTestrun API: {str(ve)}")
        return jsonify({'code': 400, 'message': str(ve)}), 400

    except Exception as e:
        app.logger.error(f"An unexpected error occurred in addNewCasesToTestrun API: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500


# --------------------Android UI automation request----------------------
@app.route('/getUnpassedCaseList/<test_run_id>', methods=['GET'])
def get_test_run_unpassed_case_lst_api(test_run_id):
    """
    :param test_run_id:
    :return: unpassed_case_lst unpassed_case_lst_num
    """
    try:
        test_run_id = test_run_id.strip()

        if not test_run_id:
            return jsonify({'code': 400, 'message': 'test_run_id is missing or empty!'}), 400

        unpassed_case_lst = list(get_unpassed_case_lst(test_run_id) or [])
        unpassed_case_lst_num = len(unpassed_case_lst) if unpassed_case_lst else 0

        return jsonify({'code': 200, 'unpassed_case_lst': unpassed_case_lst, 'unpassed_case_lst_num': unpassed_case_lst_num})

    except Exception as e:
            app.logger.error(f"Failed to get unpassed cases list for test run {test_run_id}: {str(e)}")
            return jsonify({'code': 500, 'message': 'Internal server error!'}), 500

@app.route('/getTestRunCaseLst/<test_run_id>', methods=['GET'])
def get_test_run_case_id_list_api(test_run_id):
    """
    :param test_run_id:
    :return: test_run_case_id_list
    """
    try:
        test_run_id = test_run_id.strip()

        if not test_run_id:
            return jsonify({'code': 400, 'message': 'test_run_id is missing or empty!'}), 400

        test_run_case_id_list = list(get_aa_test_case_list(test_run_id) or [])
        test_run_case_id_list_num = len(test_run_case_id_list) if test_run_case_id_list else 0

        return (jsonify({'code': 200, 'test_case_id_lst': test_run_case_id_list, 'test_run_case_id_list_num': test_run_case_id_list_num}))

    except Exception as e:
            app.logger.error(f"Failed to get cases list for test run {test_run_id}: {str(e)}")
            return jsonify({'code': 500, 'message': 'Internal server error!'}), 500

@app.route('/getTestRunDetails/<test_run_id>', methods=['GET'])
def get_test_run_details_api(test_run_id):
    """
    :param test_run_id:
    :return: test_run_details
    """
    try:
        test_run_id = test_run_id.strip()

        if not test_run_id:
            return jsonify({'code': 400, 'message': 'test_run_id is missing or empty!'}), 400

        test_run_details = get_test_run_details(test_run_id)
        # data = {'test_run_details': test_run_details}
        return jsonify({'code': 200, 'test_run_details': test_run_details})
    except Exception as e:
        app.logger.error(f"Failed to get test run details: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500

@app.route('/sendResultToTestRail', methods=['POST'])
def send_result_to_test_rail_api():
    """
    :request body:
        {
        passCases: [1, 2, 3]
        notPassCases: [4, 5, 6]
        testRunId: 123
        comment: "comment"
        }
    :return:
    """
    try:
        request_data = request.get_json()

        if not request_data:
            app.logger.error("Invalid JSON data received.")
            return jsonify({'code': 400, 'message': 'Invalid JSON data!'}), 400

        pass_cases_list = request_data["passCases"]
        unpass_cases_list = request_data["notPassCases"]
        test_run_id = request_data["testRunId"]
        comment = request_data["comment"]

        if pass_cases_list is None or unpass_cases_list is None or test_run_id is None or comment is None:
            app.logger.error("Missing required parameters in JSON data.")
            return jsonify({'code': 400, 'message': 'Missing required parameters!'}), 400

        send_result_to_test_rail(pass_cases=pass_cases_list, not_pass_cases=unpass_cases_list, test_run_id=test_run_id, comment=comment)
        return jsonify({'code': 200, 'message': 'success'})

    except Exception as e:
        app.logger.error(f"Failed to send result to TestRail: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500

@app.route('/addPlan', methods=['POST'])
def add_plan_api():
    """
    :request body:
        {
        projectId
        planName
        milestoneId
        }
    :return:
    """
    try:
        request_data = request.get_json()

        if not request_data:
            raise ValueError("Invalid JSON data received.")

        project_id = request_data["projectId"]
        plan_name = request_data["planName"]
        milestone_id = request_data["milestoneId"]

        if project_id is None or plan_name is None or milestone_id is None:
            raise ValueError("Missing required parameters in JSON data.")

        add_plan(project_id=project_id, plan_name=plan_name, milestone_id=milestone_id)
        return jsonify({'code': 200, 'message': 'success'})

    except ValueError as e:
        app.logger.error(f"Value error in addPlan API: {str(e)}")
        return jsonify({'code': 400, 'message': str(e)}), 400

    except Exception as e:
        app.logger.error(f"An unexpected error occurred in addPlan API: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500

@app.route('/getPlanId/<project_id>', methods=['GET'])
def get_plan_ids_api(project_id):
    """
    :param project_id:
    :return: plan_ids
    """
    try:
        project_id = project_id.strip()
        milestone_id = request.args.get('milestoneId')

        if project_id is None or milestone_id is None:
            return jsonify({'code': 400, 'message': 'Missing required parameters!'}), 400

        plan_ids = get_plan_ids(project_id=project_id, milestone_id=milestone_id)
        # data = {'plan_ids': plan_ids}
        return jsonify({'code': 200, 'plans': plan_ids})

    except Exception as e:
        app.logger.error(f"Failed to get plan IDs: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500


@app.route('/addRunToPlan', methods=['POST'])
def add_run_to_plan_api():
    """
    :request body:
        {
        planId
        caseId
        suiteId
        testrunName
        }
    :return: test_run_id
    """
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({'code': 400, 'message': 'Invalid JSON data!'}), 400

        plan_id = request_data["planId"]
        case_id = request_data["caseId"]
        suite_id = request_data["suiteId"]
        testrun_name = request_data["testrunName"]
        if None in [plan_id, case_id, suite_id, testrun_name]:
            return jsonify({'code': 400, 'message': 'Invalid request data!'}), 400

        test_run_id = add_run_to_plan(plan_id, case_id, suite_id, testrun_name)
        return jsonify({'code': 200, 'testRunId': test_run_id})

    except KeyError as e:
        app.logger.error(f"Missing key in JSON data: {str(e)}")
        return jsonify({'code': 400, 'message': f'Missing required parameter: {str(e)}'}), 400
    except Exception as e:
        app.logger.error(f"Failed to add run to plan: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500

@app.route('/updatePlanEntryName', methods=['POST'])
def update_plan_entry_name_api():
    """
    :request body:
        {
        testRunId
        testRunName
        }
    :return:
    """
    try:
        request_data = request.get_json()
        if not request_data:
            return jsonify({'code': 400, 'message': 'Invalid JSON data!'}), 400

        test_run_id = request_data["testRunId"]
        plan_entry_name = request_data["testRunName"]

        if test_run_id is None or plan_entry_name is None:
            return jsonify({'code': 400, 'message': 'Missing required parameters!'}), 400

        update_plan_entry_name(test_run_id, plan_entry_name)
        return jsonify({'code': 200, 'message': 'success'})

    except KeyError as e:
        app.logger.error(f"Missing key in JSON data: {str(e)}")
        return jsonify({'code': 400, 'message': f'Missing required parameter: {str(e)}'}), 400

    except Exception as e:
        app.logger.error(f"Failed to update plan entry name: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500

# --------------------Carol request----------------------
@app.route('/getTestRunResults/<test_run_id>', methods=['GET'])
def get_test_run_results_api(test_run_id):
    """
    :param test_run_id:
    :return: test_run_results
    """
    try:
        test_run_id = test_run_id.strip()

        if test_run_id is None:
            return jsonify({'code': 400, 'message': 'Missing required parameters!'}), 400

        test_run_results = get_test_run_results(test_run_id=test_run_id)
        # data = {'plan_ids': plan_ids}
        return jsonify({'code': 200, 'test_run_results': test_run_results})

    except Exception as e:
        app.logger.error(f"Failed to get plan IDs: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500

@app.route('/getUser/<user_id>', methods=['GET'])
def get_user_api(user_id):
    """
    An error occurred while getting user with ID 30: 403 Client Error: Forbidden for url: /get_user/<user_id>
    :param user_id:
    :return: user_name
    """

    try:
        user_id = user_id.strip()

        if user_id is None:
            return jsonify({'code': 400, 'message': 'Missing required parameters!'}), 400

        user_name = get_user(user_id=user_id)

        if user_name is None:  # 检查用户是否存在
            return jsonify({'code': 404, 'message': 'User not found!'}), 404

        return jsonify({'code': 200, 'user_name': user_name})

    except ValueError as e:  # 处理用户ID格式错误的情况
        app.logger.error(f"Invalid user ID format: {str(e)}")
        return jsonify({'code': 400, 'message': 'Invalid user ID format!'}), 400
    except Exception as e:
        app.logger.error(f"Failed to get user: {str(e)}")
        return jsonify({'code': 500, 'message': 'Internal server error!'}), 500

if __name__ == '__main__':
    app.run(host='172.16.0.95', port=5002, debug=True)
