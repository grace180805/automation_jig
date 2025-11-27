import os
import sys

from api.src.common.testrail import APIClient

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
aa_test_rail_client = APIClient('https://aaecosystem.testrail.com')


# def get_test_rail_info_from_1password():
#     # login to 1password
#     subprocess.run(
#         ["op", "signin"],
#         capture_output=True,
#         text=True
#     )
#
#     # get testrail api key from 1password
#     result = subprocess.run(
#         ["op", "item", "get", "TestRail-API key-SH", "--format", "json"],
#         capture_output=True,
#         text=True
#     )
#     item = json.loads(result.stdout)
#     item_id = item['id']
#
#     # get testrail email and password from 1password
#     result_credential = subprocess.run(
#         ["op", "item", "get", item_id, "--reveal", "--format", "json"],
#         capture_output=True,
#         text=True
#     )
#     item_credentail = json.loads(result_credential.stdout)
#     email = item_credentail['fields'][4]['value']
#     credential = item_credentail['fields'][2]['value']
#     return email, credential
#
#
# def get_test_rail_client():
#     client = APIClient('https://aaecosystem.testrail.com')
#     client.user, client.password = get_test_rail_info_from_1password()
#
#     return client
#
#
# aa_test_rail_client = get_test_rail_client()

# def get_user_by_email(user_email):
#     """
#     get user info by email
#     :param user_email:
#     :return:
#     """
#     res = aa_test_rail_client.send_get('get_user_by_email&email=' + user_email)
#     return res


# def get_case_field():
#     cases_field = aa_test_rail_client.send_get('get_case_fields')
#     return cases_field
#
#
# def update_case_field(case_id, data):
#     """
#     update case field
#     :param case_id:
#     :param data:
#     data={'custom_sh_ios_automation': 2}
#     data={'custom_sh_regression_type': [3]}
#     data={'status_id': 3}
#     :return:
#     """
#     aa_test_rail_client.send_post('update_case/' + str(case_id), data=data)


# def get_aa_test_case_detail_list(test_run_id):
#     """
#     get case list of test run
#     :param test_run_id:
#     :return:
#     """
#     flag = True
#     offset = 0
#     test_run_tests = []
#     while flag:
#         tests = aa_test_rail_client.send_get('get_tests/' + str(test_run_id) + '&offset=' + str(offset))['tests']
#         test_run_tests.extend(tests)
#         if len(tests) == 250:
#             offset = offset + 250
#         else:
#             flag = False
#     return test_run_tests

# def update_test_run_cases(test_run_id, case_id_list):
#     """
#     :param test_run_id
#     :param case_id_list
#     :return:
#     """
#     tests = aa_test_rail_client.send_post('update_run/' + str(test_run_id),
#                                           data={"case_ids": case_id_list
#                                                 })

# def get_plans(project_id):
#     plans = aa_test_rail_client.send_get("get_plans/" + str(project_id))
#     return plans


# def write_result_for_august_android_fit(pass_cases, test_run_id, app_version):
#     """
#     write result for august android fit
#     :param pass_cases: [123,234,235]
#     :param test_run_id:
#     :param app_version: 23.5.0
#     :return:
#     """
#     client = APIClient('https://august.testrail.com/')
#     client.user = 'Longyan.Shen@assaabloy.com'
#     client.password = '8Z0hJpDzWaDhgsTatq4O-IR7rYiZACMX31Ri9zpNT'
#     s = set(pass_cases)
#     print(len(s))
#     pass_list = []
#     # retest_list = []
#     # 新增pendinglist 2020.11.19
#     pending_cases1 = [3871624, 3871646]  # depend on 3871561 in RFID
#     pending_cases2 = [3871648]  # depend on 3871642 in RFID
#     pending_cases3 = [3871675]  # depend on 3871626 in RFID
#     pending_cases4 = [3871677]  # depend on 3871658 in RFID
#     pending_cases5 = [3918498]  # depend on 3918399 in schedule
#     pending_cases6 = [3918499]  # depend on 3918400 in schedule
#     pending_cases7 = [3918560]  # depend on 3918401 in schedule
#     pending_cases8 = [3918563]  # depend on 3918433 in schedule
#     pending_cases9 = [3918576]  # depend on 3871658 in schedule
#     pending_cases10 = [3918577]  # depend on 3908525 in schedule
#     pending_cases11 = [3918592]  # depend on 3871664 in schedule
#     pending_cases12 = [3918595]  # depend on 3908500 in schedule
#     pending_cases13 = [3918601]  # depend on 3918362 in schedule
#     if 3871561 in pass_cases:
#         pass_cases.extend(pending_cases1)
#     elif 3871642 in pass_cases:
#         pass_cases.extend(pending_cases2)
#     elif 3871626 in pass_cases:
#         pass_cases.extend(pending_cases3)
#     elif 3871657 in pass_cases:
#         pass_cases.extend(pending_cases4)
#     elif 3918399 in pass_cases:
#         pass_cases.extend(pending_cases5)
#     elif 3918400 in pass_cases:
#         pass_cases.extend(pending_cases6)
#     elif 3918401 in pass_cases:
#         pass_cases.extend(pending_cases7)
#     elif 3918433 in pass_cases:
#         pass_cases.extend(pending_cases8)
#     elif 3871658 in pass_cases:
#         pass_cases.extend(pending_cases9)
#     elif 3908525 in pass_cases:
#         pass_cases.extend(pending_cases10)
#     elif 3871664 in pass_cases:
#         pass_cases.extend(pending_cases11)
#     elif 3908500 in pass_cases:
#         pass_cases.extend(pending_cases12)
#     elif 3918362 in pass_cases:
#         pass_cases.extend(pending_cases13)
#     else:
#         pass
#
#     print(pass_cases)
#     print(len(pass_cases))
#
#     for case in pass_cases:
#         pass_list.append({'case_id': case, 'status_id': 1,
#                           'comment': 'Passed by Android automation scripts on App Version ' + app_version})
#     result_pass = client.send_post('add_results_for_cases/' + str(test_run_id), data={'results': pass_list})


# def write_result_for_august_ios_fit(pass_cases_list, test_run_id, app_version):
#     """
#     :param pass_cases_list: ["@3871561", "@3871601"]
#     :param test_run_id:
#     :param app_version: v22.24.0-rc.2+2022.12.20.58724
#     :return:
#     """
#     client = APIClient('https://august.testrail.com/')
#     client.user = 'yong.zhang2@assaabloy.com'
#     client.password = '5mOdJ64uk3YeQsNdVdpp-SRRImqFh70J6iVFDvr76'
#     flag = True
#     offset = 0
#     test_run_tests = []
#     while flag:
#         tests = client.send_get('get_tests/' + str(test_run_id) + '&offset=' + str(offset))['tests']
#         test_run_tests.extend(tests)
#         if len(tests) == 250:
#             offset = offset + 250
#         else:
#             flag = False
#     test_run_case_list = [i["case_id"] for i in test_run_tests]
#
#     print(test_run_case_list)
#     pass_cases = pass_cases_list
#
#     pass_cases_id_lst = []
#     for case in pass_cases:
#         if case.find('@') > -1:
#             case = case.replace('@', '')
#         if case.find('C') > -1:
#             case = case.replace('C', '')
#         pass_cases_id_lst.append(int(case))
#
#     join = set(test_run_case_list) & set(pass_cases_id_lst)
#     pass_list = []
#     for case in join:
#         pass_list.append({'case_id': case, 'status_id': 1,
#                           'comment': 'Passed by ios automation scripts on App Version ' + app_version})
#     result_pass = client.send_post('add_results_for_cases/' + str(test_run_id), data={'results': pass_list})


# def update_case(case_id, data):
#     aa_test_rail_client.send_post('update_case/' + str(case_id), data=data)


# def get_test_run_failed_case_lst(test_run_id):
#     flag = True
#     offset = 0
#     test_run_tests = []
#     while flag:
#         tests = aa_test_rail_client.send_get('get_tests/' + str(test_run_id) + '&offset=' + str(offset))['tests']
#         test_run_tests.extend(tests)
#         if len(tests) == 250:
#             offset = offset + 250
#         else:
#             flag = False
#     test_run_failed_case_list = filter(lambda x: x['status_id'] != 1, test_run_tests)
#     test_run_failed_case_id_list = set([i["case_id"] for i in test_run_failed_case_list])
#     return test_run_failed_case_id_list


# aa_tests1 = get_aa_test_case_list(3583)
# aa_case_list_1 = [i["case_id"] for i in aa_tests1 if i["status_id"] == 1]
# print(aa_case_list_1)
# print(len(aa_case_list_1))
#
# aa_tests = get_aa_test_case_list(3878)
# aa_case_list = [i["case_id"] for i in aa_tests]
# print(aa_case_list)
# print(len(aa_case_list))
#
# print(set(aa_case_list_1).difference(set(aa_case_list)))


def clone_testrun_to_plan(source_testrun_id, target_testplan_id, target_testrun_name):
    case_lists = get_aa_test_case_list(source_testrun_id)
    data = {
        "suite_id": 457,
        "include_all": False,
        "case_ids": list(case_lists),
        # actual test run name:
        "name": target_testrun_name,
        "runs": [
            {
                # for testrail api structure, currently, not display in testrail UI,
                # suggest-use same name with up
                "name": target_testrun_name,
                "include_all": False,
                "case_ids": list(case_lists)
            }]
    }
    add_plan_entries(target_testplan_id, data)


def get_testrun_entry_id_in_plan(data, target_key, target_value, print_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key and value == target_value:
                return data.get(print_key)
            else:
                result = get_testrun_entry_id_in_plan(value, target_key, target_value, print_key)
                if result is not None:
                    return result

    elif isinstance(data, list):
        for item in data:
            result = get_testrun_entry_id_in_plan(item, target_key, target_value, print_key)
            if result is not None:
                return result


# for testrun in configuration, only can update configuration cases,
# we need clear Test Cases selection, to become default: As above
def update_testrun_in_plan_cases(testplan_id, update_testrun_id, case_list_or_testrun_id, remove_or_add):
    entry_id = get_testrun_entry_id_in_plan(get_plan_entries(testplan_id), 'id',
                                            update_testrun_id, 'entry_id')
    target_run_cases = get_aa_test_case_list(update_testrun_id).split(', ')
    if isinstance(case_list_or_testrun_id, list):
        remove_or_add_cases = case_list_or_testrun_id
    else:
        remove_or_add_cases = get_aa_test_case_list(case_list_or_testrun_id).split(', ')
    if remove_or_add == "remove":
        # remove cases in remove_or_add_cases list from target_run
        final_list = [item for item in target_run_cases if item not in remove_or_add_cases]
    else:
        # add cases in remove_or_add_cases list into target_run, and not duplicate, just like union
        final_list = list(remove_or_add_cases) + [item for item in target_run_cases if item not in remove_or_add_cases]
    update_plan_entry_cases(testplan_id, entry_id, final_list)


def get_plan_entries(plan_id):
    """
    get plan entry list
    :param plan_id:
    :return:
    """
    test_entries = aa_test_rail_client.send_get("get_plan/" + str(plan_id))['entries']
    return test_entries


def add_plan_entries(plan_id, data):
    aa_test_rail_client.send_post("add_plan_entry/" + str(plan_id), data=data)


def update_plan_entry_cases(test_plan_id, entry_id, case_id_list):
    """
    update the case list of entry
    :param test_plan_id:
    :param entry_id:
    :param case_id_list:
    :return:
    """
    tests = aa_test_rail_client.send_post('update_plan_entry/' + str(test_plan_id) + '/' + str(entry_id), data={
        "case_ids": case_id_list
    })


def add_cases_to_test_run(from_run, to_plan, to_run):
    # Get cases to add
    cases_from_run = get_aa_test_case_list(from_run)

    # Get existing cases
    cases_to_run = get_aa_test_case_list(to_run)

    # Combine cases (remove duplicates)
    all_case_ids = list(cases_to_run.union(cases_from_run))

    # Add new cases to test run
    data = {
        "include_all": False,
        "case_ids": all_case_ids
    }

    run_detail = aa_test_rail_client.send_get("get_run/" + str(to_run))
    plan_id = run_detail["plan_id"]
    plan_detail = aa_test_rail_client.send_get('get_plan/' + str(to_plan))
    entries = plan_detail["entries"]
    entry_id = ''
    for entry in entries:
        run = filter(lambda run: run['id'] == int(to_run), entry['runs'])
        if len(list(run)) > 0:
            entry_id = entry['id']
            break
    aa_test_rail_client.send_post('update_plan_entry/' + str(plan_id) + '/' + entry_id,
                                  data=data)


def get_unpassed_case_lst(test_run_id):
    """
    :param test_run_id:
    :return: unpassed cases list
    """
    flag = True
    offset = 0
    test_run_tests = []
    while flag:
        tests = aa_test_rail_client.send_get('get_tests/' + str(test_run_id) + '&offset=' + str(offset))['tests']
        test_run_tests.extend(tests)
        if len(tests) == 250:
            offset = offset + 250
        else:
            flag = False
    test_run_unpassed_case_list = filter(lambda x: x['status_id'] != 1, test_run_tests)
    test_run_unpassed_case_id_list = set([i["case_id"] for i in test_run_unpassed_case_list])
    # test_run_unpassed_case_id_list_str = ', '.join(map(str, test_run_unpassed_case_id_list))
    return test_run_unpassed_case_id_list


def send_result_to_test_rail(pass_cases, not_pass_cases, test_run_id, comment=''):
    """
    pass_cases: pass cases list
    test_run_id: test run id
    """
    send_result = []
    for case in pass_cases:
        send_result.append({'case_id': case, 'status_id': 1, 'comment': comment})
    # for case in not_pass_cases:
    #     send_result.append({'case_id': case, 'status_id': 5, 'comment': comment})

    aa_test_rail_client.send_post('add_results_for_cases/' + str(test_run_id), data={'results': send_result})


def get_aa_test_case_list(test_run_id):
    """
    get case list of test run
    :param test_run_id:
    :return:
    """
    flag = True
    offset = 0
    test_run_tests = []
    while flag:
        tests = aa_test_rail_client.send_get('get_tests/' + str(test_run_id) + '&offset=' + str(offset))['tests']
        test_run_tests.extend(tests)
        if len(tests) == 250:
            offset = offset + 250
        else:
            flag = False
    test_run_case_id_list = set([i["case_id"] for i in test_run_tests])
    # test_run_case_id_list_str = ', '.join(map(str, test_run_case_id_list))

    return test_run_case_id_list


def get_test_run_details(test_run_id):
    """
    get test run details
    :param test_run_id:
    :return:
    """
    test_run_details = aa_test_rail_client.send_get("get_run/" + str(test_run_id))
    return test_run_details


def add_plan(project_id, plan_name, milestone_id):
    try:
        response = aa_test_rail_client.send_post("add_plan/" + str(project_id), {"name": plan_name, "milestone_id": milestone_id})
        if response.get('error'):
            print(f"Error adding plan: {response.get('error')}")
        else:
            print("plan created successfully")
    except Exception as e:
        print(f"An error occurred while adding plan: {e}")


def get_plan_ids(project_id, milestone_id):
    try:
        response = aa_test_rail_client.send_get("get_plans/" + str(project_id) + '&milestone_id=' + str(milestone_id))['plans']
        return response
    except Exception as e:
        print(f"An error occurred while getting plan id: {e}")

def add_run_to_plan(plan_id, case_id, suite_id, testrun_name):
    try:
        response = aa_test_rail_client.send_post("add_plan_entry/" + str(plan_id),
                                   {"suite_id":  suite_id,
                                    "name": testrun_name,
                                    "include_all": False,
                                    "case_ids": case_id})
        if response.get('error'):
            print(f"Error adding run to plan: {response.get('error')}")
            return None
        return response['runs'][0]['id']
    except KeyError as e:
        print(f"KeyError in response: {e} - The response format may have changed.")
    except Exception as e:
        print(f"An error occurred while adding run to plan: {e}")
        return None

def update_plan_entry_name(test_run_id, name):
    run_detail = get_test_run_details(test_run_id)
    plan_id = run_detail["plan_id"]
    plan_detail = aa_test_rail_client.send_get('get_plan/' + str(plan_id))
    entries = plan_detail["entries"]
    entry_id = ''
    for entry in entries:
        run = filter(lambda run: run['id'] == int(test_run_id), entry['runs'])
        if len(list(run)) > 0:
            entry_id = entry['id']
            break
    aa_test_rail_client.send_post('update_plan_entry/' + str(plan_id) + '/' + entry_id,
                                                 data={"name": name})

def get_test_run_results(test_run_id):
    """
        :param test_run_id:
        :return: test_run_results
    """
    try:
        response = aa_test_rail_client.send_get("get_results_for_run/" + str(test_run_id))
        return response
    except Exception as e:
        print(f"An error occurred while getting plan id: {e}")

def get_user(user_id):
    """
        An error occurred while getting user with ID 30: 403 Client Error: Forbidden for url: /get_user/<user_id>
        :param user_id:
        :return: user_name
    """
    try:
        result = aa_test_rail_client.send_get(f"get_user/{user_id}")
        if 'name' not in result:
            raise KeyError(f"Response from get_user/{user_id} does not contain 'name' key.")
        response = result['name']
        return response
    except KeyError as ke:
        print(f"KeyError occurred while getting user: {ke}")
    except Exception as e:
        print(f"An error occurred while getting user with ID {user_id}: {e}")

# if __name__ == '__main__':
#     print(get_test_run_details(10016))
