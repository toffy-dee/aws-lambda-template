import json

class bcolors:
    HEADER = '\033[95m'
    GOOD = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    NORMAL = '\033[37m'

def get_dict_difference(structure_response, structure_expected, key=None):

    list_floats = ["pct_in_low_workload", "pct_in_mid_workload", "pct_in_high_workload", "avg_workload_level"]

    if (not isinstance(structure_expected, dict)) or (not isinstance(structure_response, dict)):
        if (not isinstance(structure_expected, dict)) and (not isinstance(structure_response, dict)):
            if key in list_floats:
                if float(structure_response) != structure_expected:
                    return structure_response
            else:
                if structure_response != structure_expected:
                    if isinstance(structure_response, list) and isinstance(structure_expected, list):
                        print("are list type")
                        list_differing_elements = []
                        for idx, elem in enumerate(structure_expected):
                            try:
                                if structure_response[idx] != elem:
                                    print("unequal:\n", elem, "\n", structure_response[idx])
                                    list_differing_elements.append(structure_response[idx])
                            except Exception as e:
                                list_differing_elements.append("unequal length")
                                break
                        return list_differing_elements
                    if structure_response is None:
                        return "None"
                    return structure_response
        else:
            if structure_response is None:
                return "None"
            return structure_response
        return None
    else:

        diff_dict = {}

        for key, value in structure_response.items():
            if not key in structure_expected:
                diff_dict[key] = f"Unexpected new key! : {str(value)}"

        for key, value in structure_expected.items():

            if not key in structure_response:
                diff = f"non-existent! : {str(value)}"
            else:
                diff = get_dict_difference(structure_response[key], structure_expected[key], key)
            if diff is not None:
                diff_dict[key] = diff

        if diff_dict == {}:
            return None

        return diff_dict

def compare_jsons(response_json, file_expected_json, message):

    list_differing_key_value = []
    dict_differing_key_value = {}

    with open(file_expected_json) as f:
        expected_json = json.load(f)

    # removes untestable keys (datetime.now) for user_session dict 
    response_json.pop("created_at", None)
    response_json.pop("updated_at", None)
    expected_json.pop("created_at", None)
    expected_json.pop("updated_at", None)

    if response_json == expected_json:
        print(bcolors.GOOD + "{}{}".format(message,"json as expected!"))
        return
    else:
        try:
            dict_diff = get_dict_difference(response_json, expected_json)
            if dict_diff is not None:
                print(bcolors.WARNING + "{}{}".format(message,"json differs from expected!"))
                print(bcolors.NORMAL + "received json:\n",response_json)
                print(bcolors.WARNING + "differing keys:\n",dict_diff)
            else:
                print(bcolors.GOOD + "{}{}".format(message,"json as expected!"))
        except Exception as e:
            raise
            print(bcolors.WARNING + "Exception in compare json\n", e)