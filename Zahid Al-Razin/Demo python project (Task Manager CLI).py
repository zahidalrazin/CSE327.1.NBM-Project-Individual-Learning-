import json

class Task:
    def __init__(self, title, completed=False):
        self.title = title
        self.completed = completed

    def to_dict(self):
        return {"title": self.title, "completed": self.completed}

    @classmethod
    def from_dict(cls, data):
        return cls(data['title'], data['completed'])

class TaskManager:
    def __init__(self, filename="data.json"):
        self.filename = filename
        self.tasks = self.load_tasks()

    def add_task(self, title):
        self.tasks.append(Task(title))

    def view_tasks(self):
        if not self.tasks:
            print("No tasks found.")
        for i, task in enumerate(self.tasks, 1):
            status = "✓" if task.completed else "✗"
            print(f"{i}. [{status}] {task.title}")

    def mark_done(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks[index].completed = True
        else:
            print("Invalid task number.")

    def delete_task(self, index):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
        else:
            print("Invalid task number.")

    def save_tasks(self):
        with open(self.filename, "w") as f:
            json.dump([task.to_dict() for task in self.tasks], f)

    def load_tasks(self):
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                return [Task.from_dict(item) for item in data]
        except FileNotFoundError:
            return []

def main():
    manager = TaskManager()

    while True:
        print("\n===== Task Manager =====")
        print("1. Add Task")
        print("2. View Tasks")
        print("3. Mark Task as Done")
        print("4. Delete Task")
        print("5. Save & Exit")
        choice = input("Choose an option (1-5): ")

        if choice == '1':
            title = input("Enter task title: ")
            manager.add_task(title)

        elif choice == '2':
            manager.view_tasks()

        elif choice == '3':
            manager.view_tasks()
            idx = int(input("Enter task number to mark as done: ")) - 1
            manager.mark_done(idx)

        elif choice == '4':
            manager.view_tasks()
            idx = int(input("Enter task number to delete: ")) - 1
            manager.delete_task(idx)

        elif choice == '5':
            manager.save_tasks()
            print("Tasks saved. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
