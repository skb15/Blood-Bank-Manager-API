from flask import Flask, jsonify, request
from hospitals import database

app = Flask(__name__)


def parse_blood(bloodgroup):
    group = bloodgroup[0:-1]
    rh = bloodgroup[-1]

    return (group, rh)


@app.route('/hospitals')
def hospitals():
    db = database[:]
    query = request.args

    # Filtering
    if query.get("bloodGroup") != None:
        bloodgroup = query.get("bloodGroup")

        compatibility_list = {
            'A+': ['A+', 'A-', 'O+', 'O-'],
            'A-': ['A-', 'O-'],
            'B+': ['B+', 'B-', 'O+', 'O-'],
            'B-': ['B-', 'O-'],
            'AB+': ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'],
            'AB-': ['AB-', 'A-', 'B-', 'O-'],
            'O+': ['O+', 'O-'],
            'O-': ['O-']
        }

        def filter_by_bloodgroup(hospital):
            compatible_bloodgroups = compatibility_list[bloodgroup]

            for compatible_bloodgroup in compatible_bloodgroups:
                group, rh = parse_blood(compatible_bloodgroup)
                if hospital["stock"][group][rh] > 0:
                    return True

            return False

        db = [h for h in filter(filter_by_bloodgroup, db)]

    # Sorting
    if query.get("pincode") != None:
        pincode = int(query.get("pincode"))

        def sort_by_pincode(hospital):
            return abs(pincode - hospital["pincode"])

        db.sort(key=sort_by_pincode)

    return jsonify(db)
