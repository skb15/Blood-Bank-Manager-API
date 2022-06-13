from flask import Flask, jsonify, request
from flask_cors import CORS
from hospitals import hospitalDB
from users import userDB
import re

app = Flask(__name__)
CORS(app)


def parse_blood(bloodgroup):
    group = bloodgroup[0:-1]
    rh = bloodgroup[-1]

    return (group, rh)


@app.route('/hospitals', methods=['GET', 'POST'])
def hospitals():
    if request.method == "GET":
        db = hospitalDB[:]
        query = request.args

        # Filteration by name
        if query.get("name") != None:
            name = query.get("name").lower()

            def filter_by_name(hospital):
                unformattedwords = hospital["name"].lower()
                words = re.sub("[^a-z]+", " ", unformattedwords).strip()

                for word in name.split(" "):
                    if word not in words:
                        return False

                return True
            db = [h for h in filter(filter_by_name, db)]

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
                    if hospital["stocks"][group][rh] > 0:
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


@app.route('/hospitals/<id>', methods=['GET', 'PUT', 'DELETE'])
def hospital(id):
    if request.method == "GET":
        hospital_id = int(id)

        for hospital in hospitalDB:
            if(hospital["id"] == hospital_id):
                return jsonify(hospital)


@app.route('/stocks/<id>', methods=['GET', 'PUT'])
def stock(id):
    if request.method == "PUT":
        hospital_id = int(id)
        data = request.json

        for hospital in hospitalDB:
            if(hospital["id"] == hospital_id):
                hospital["stocks"] = data["stock"]
                hospital["lastUpdate"] = data["timestamp"]

        return data


@app.route('/users', methods=['GET', 'POST'])
def user():
    if request.method == "POST":
        data = request.json

        for user in userDB:
            if user["username"] == data["username"]:
                if user["password"] == data["password"]:
                    return jsonify({"type": user["type"], "id": user["id"]})
                return jsonify({"error": "Incorrect Password"})

        return jsonify({"error": "No Account found"})
