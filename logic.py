
import argparse
from pathlib import PurePath
import json
from jsonschema import validate # see https://json-schema.org/understanding-json-schema/UnderstandingJSONSchema.pdf

students_schema = {
    "type": "object",
    "properties": {
        "Students": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "id": {"type": "integer"},
                    "matrikelnummer": {"type": "integer"},
                    "solved_ex": {"type": "array"},
                    "presented_ex": {"type": "array"}
                },
                "additionalProperties": False
            }
        }
    }
}

exercise_schema = {
    "type": "object",
    "properties": {
        "Exercise": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "id": {"type": "integer"},
                    "points": {"type": "integer"},
                    "date" : {}
                },
                "additionalProperties": False
            }
        }
    }
}

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--basedir', help='Directory that holds the course data')
    #parser.add_argument('--studentlist', help='File that holds the student list (default [basedir]/students.txt')
    args = parser.parse_args()
    return args

class logic:
    def __init__(self, argv):
        self.arg_parse = parse_args()
        self.basedir = self.arg_parse.basedir or "."
        self.students_file = self.basedir + "/students.json"
        self.students = self.getStudents()
        self.exersises = self.getExersises()
        self.select_ex = -1

    def getStudents(self):
        with open(self.students_file) as f :
            students = json.load(f)
        validate(instance=students, schema=students_schema)
        return students

    def writeStudents(self):
        validate(instance=self.students, schema=students_schema)
        with open(self.students_file,'w') as f :
            json.dump(self.students,f,indent=4,ensure_ascii=False)

    def getExersises(self):
        with  open(self.basedir + "/exercise.json") as f:
            ex = json.load(f)
        validate(instance=ex, schema=exercise_schema)
        return ex
