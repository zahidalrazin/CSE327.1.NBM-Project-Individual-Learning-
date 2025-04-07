import json
from datetime import datetime
from functools import wraps

def log_action(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[{datetime.now()}] Executing {func.__name__}...")
        return func(*args, **kwargs)
    return wrapper

class StudentExistsError(Exception):
    pass

class Student:
    def __init__(self, student_id, name, age):
        self.student_id = student_id
        self.name = name
        self.age = age

    def to_dict(self):
        return {"id": self.student_id, "name": self.name, "age": self.age}

class StudentManager:
    def __init__(self):
        self.students = {}

    @log_action
    def add_student(self, student: Student):
        if student.student_id in self.students:
            raise StudentExistsError(f"Student with ID {student.student_id} already exists.")
        self.students[student.student_id] = student
        print(f"Added student: {student.name}")

    @log_action
    def remove_student(self, student_id):
        if student_id in self.students:
            removed = self.students.pop(student_id)
            print(f"Removed student: {removed.name}")
        else:
            print(f"No student found with ID {student_id}")

    @log_action
    def list_students(self):
        if not self.students:
            print("No students available.")
        for student in self.students.values():
            print(f"{student.name} (ID: {student.student_id}, Age: {student.age})")

    @log_action
    def save_to_file(self, filename="students.json"):
        with open(filename, "w") as f:
            data = [s.to_dict() for s in self.students.values()]
            json.dump(data, f, indent=4)
        print(f"Saved {len(self.students)} students to {filename}")

    @log_action
    def load_from_file(self, filename="students.json"):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
                for entry in data:
                    student = Student(entry["id"], entry["name"], entry["age"])
                    self.students[student.student_id] = student
            print(f"Loaded {len(self.students)} students from {filename}")
        except FileNotFoundError:
            print("No file found to load.")

if __name__ == "__main__":
    manager = StudentManager()

    try:
        manager.add_student(Student("001", "Alice", 20))
        manager.add_student(Student("002", "Bob", 22))
        manager.add_student(Student("001", "Charlie", 23))  # Duplicate to test error
    except StudentExistsError as e:
        print(f"Error: {e}")

    manager.remove_student("003")  # Not found
    manager.list_students()

    manager.save_to_file()
    manager.load_from_file()
