# task_management_system.py

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import uuid
import json
import os
from enum import Enum


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class TaskStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Task(ABC):
    """Abstract base class for all tasks in the system."""
    
    def __init__(self, title, description=None, priority=Priority.MEDIUM, due_date=None):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.priority = priority
        self.status = TaskStatus.NOT_STARTED
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.due_date = due_date
        self.completion_date = None
        self.tags = set()
    
    def update_status(self, status):
        """Update the task status and record the time of update."""
        if status not in TaskStatus:
            raise ValueError(f"Invalid status: {status}")
        
        self.status = status
        self.updated_at = datetime.now()
        
        if status == TaskStatus.COMPLETED:
            self.completion_date = self.updated_at
    
    def add_tag(self, tag):
        """Add a tag to the task."""
        self.tags.add(tag.lower())
        self.updated_at = datetime.now()
    
    def remove_tag(self, tag):
        """Remove a tag from the task."""
        if tag.lower() in self.tags:
            self.tags.remove(tag.lower())
            self.updated_at = datetime.now()
    
    def is_overdue(self):
        """Check if the task is overdue."""
        if self.due_date and self.status != TaskStatus.COMPLETED:
            return datetime.now() > self.due_date
        return False
    
    @abstractmethod
    def estimate_effort(self):
        """Estimate the effort required to complete this task."""
        pass
    
    def to_dict(self):
        """Convert task to dictionary for serialization."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.name,
            "status": self.status.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completion_date": self.completion_date.isoformat() if self.completion_date else None,
            "tags": list(self.tags),
            "type": self.__class__.__name__
        }
    
    def __str__(self):
        status_symbol = {
            TaskStatus.NOT_STARTED: "⭕",
            TaskStatus.IN_PROGRESS: "⏳",
            TaskStatus.BLOCKED: "🚫",
            TaskStatus.COMPLETED: "✅",
            TaskStatus.CANCELLED: "❌"
        }
        priority_symbol = {
            Priority.LOW: "⬇️",
            Priority.MEDIUM: "➡️",
            Priority.HIGH: "⬆️",
            Priority.URGENT: "🔥"
        }
        
        due_str = f" (Due: {self.due_date.strftime('%Y-%m-%d')})" if self.due_date else ""
        return f"{status_symbol[self.status]} {priority_symbol[self.priority]} {self.title}{due_str}"


class SimpleTask(Task):
    """A basic task with minimal attributes."""
    
    def estimate_effort(self):
        """Estimate effort based on priority."""
        effort_map = {
            Priority.LOW: "Low",
            Priority.MEDIUM: "Medium",
            Priority.HIGH: "High",
            Priority.URGENT: "Very High"
        }
        return effort_map[self.priority]


class ProjectTask(Task):
    """A task that is part of a larger project."""
    
    def __init__(self, title, project, description=None, priority=Priority.MEDIUM, due_date=None):
        super().__init__(title, description, priority, due_date)
        self.project = project
        self.dependencies = set()
        self.estimated_hours = 1.0  # Default estimate
        
    def add_dependency(self, task):
        """Add a task that must be completed before this one."""
        self.dependencies.add(task.id)
        self.updated_at = datetime.now()
    
    def remove_dependency(self, task):
        """Remove a dependency."""
        if task.id in self.dependencies:
            self.dependencies.remove(task.id)
            self.updated_at = datetime.now()
    
    def set_estimate(self, hours):
        """Set the estimated hours to complete the task."""
        self.estimated_hours = float(hours)
        self.updated_at = datetime.now()
        
    def estimate_effort(self):
        """Estimate effort based on estimated hours."""
        if self.estimated_hours < 2:
            return "Small"
        elif self.estimated_hours < 8:
            return "Medium"
        else:
            return "Large"
    
    def to_dict(self):
        """Convert task to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "project": self.project,
            "dependencies": list(self.dependencies),
            "estimated_hours": self.estimated_hours
        })
        return data


class RecurringTask(Task):
    """A task that repeats at regular intervals."""
    
    def __init__(self, title, frequency, description=None, priority=Priority.MEDIUM, due_date=None):
        super().__init__(title, description, priority, due_date)
        self.frequency = frequency  # "daily", "weekly", "monthly", etc.
        self.recurrence_count = 0  # How many times it has recurred
        self.last_completed = None
    
    def complete_occurrence(self):
        """Mark the current occurrence as complete and prepare for the next one."""
        self.last_completed = datetime.now()
        self.recurrence_count += 1
        self.status = TaskStatus.NOT_STARTED  # Reset for next occurrence
        
        # Calculate next due date based on frequency
        if self.due_date:
            if self.frequency == "daily":
                self.due_date += timedelta(days=1)
            elif self.frequency == "weekly":
                self.due_date += timedelta(weeks=1)
            elif self.frequency == "monthly":
                # Simple approximation for monthly
                self.due_date += timedelta(days=30)
            elif self.frequency == "yearly":
                # Simple approximation for yearly
                self.due_date += timedelta(days=365)
        
        self.updated_at = datetime.now()
    
    def estimate_effort(self):
        """Estimate effort based on frequency and priority."""
        frequency_factor = {
            "daily": 3,
            "weekly": 2,
            "monthly": 1.5,
            "yearly": 1
        }
        
        priority_factor = {
            Priority.LOW: 1,
            Priority.MEDIUM: 2,
            Priority.HIGH: 3,
            Priority.URGENT: 4
        }
        
        factor = frequency_factor.get(self.frequency, 1) * priority_factor[self.priority]
        
        if factor <= 2:
            return "Minimal"
        elif factor <= 4:
            return "Moderate"
        elif factor <= 8:
            return "Substantial"
        else:
            return "Intensive"
    
    def to_dict(self):
        """Convert task to dictionary for serialization."""
        data = super().to_dict()
        data.update({
            "frequency": self.frequency,
            "recurrence_count": self.recurrence_count,
            "last_completed": self.last_completed.isoformat() if self.last_completed else None
        })
        return data


class TaskManager:
    """Manages collections of tasks and provides operations on them."""
    
    def __init__(self):
        self.tasks = {}
        self.task_history = []  # For maintaining history of task changes
    
    def add_task(self, task):
        """Add a new task to the manager."""
        self.tasks[task.id] = task
        self._record_history("add", task)
        return task
    
    def get_task(self, task_id):
        """Retrieve a task by its ID."""
        return self.tasks.get(task_id)
    
    def update_task(self, task_id, **kwargs):
        """Update a task's attributes."""
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        task.updated_at = datetime.now()
        self._record_history("update", task)
        return True
    
    def delete_task(self, task_id):
        """Remove a task by its ID."""
        if task_id in self.tasks:
            task = self.tasks.pop(task_id)
            self._record_history("delete", task)
            return True
        return False
    
    def _record_history(self, action, task):
        """Record a task action in the history."""
        self.task_history.append({
            "action": action,
            "task_id": task.id,
            "task_title": task.title,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_tasks_by_status(self, status):
        """Get all tasks with a specific status."""
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_tasks_by_priority(self, priority):
        """Get all tasks with a specific priority."""
        return [task for task in self.tasks.values() if task.priority == priority]
    
    def get_tasks_by_tag(self, tag):
        """Get all tasks with a specific tag."""
        return [task for task in self.tasks.values() if tag.lower() in task.tags]
    
    def get_overdue_tasks(self):
        """Get all tasks that are overdue."""
        return [task for task in self.tasks.values() if task.is_overdue()]
    
    def save_to_file(self, filename):
        """Save tasks to a JSON file."""
        data = {
            "tasks": [task.to_dict() for task in self.tasks.values()],
            "history": self.task_history
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_from_file(self, filename):
        """Load tasks from a JSON file."""
        if not os.path.exists(filename):
            return False
        
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Clear existing tasks
        self.tasks = {}
        self.task_history = data.get("history", [])
        
        # Reconstruct tasks based on their type
        for task_data in data.get("tasks", []):
            task_type = task_data.pop("type")
            
            # Convert string dates back to datetime objects
            for date_field in ["created_at", "updated_at", "due_date", "completion_date", "last_completed"]:
                if task_data.get(date_field):
                    task_data[date_field] = datetime.fromisoformat(task_data[date_field])
                    
            # Convert string enums back to enum objects
            if "priority" in task_data:
                task_data["priority"] = Priority[task_data["priority"]]
            if "status" in task_data:
                task_data["status"] = TaskStatus[task_data["status"]]
            
            # Create appropriate task object
            if task_type == "SimpleTask":
                task = SimpleTask(task_data.pop("title"), 
                                  task_data.pop("description"), 
                                  task_data.pop("priority"),
                                  task_data.pop("due_date", None))
            elif task_type == "ProjectTask":
                task = ProjectTask(task_data.pop("title"),
                                  task_data.pop("project"),
                                  task_data.pop("description"),
                                  task_data.pop("priority"),
                                  task_data.pop("due_date", None))
                task.dependencies = set(task_data.pop("dependencies", []))
                task.estimated_hours = task_data.pop("estimated_hours", 1.0)
            elif task_type == "RecurringTask":
                task = RecurringTask(task_data.pop("title"),
                                    task_data.pop("frequency"),
                                    task_data.pop("description"),
                                    task_data.pop("priority"),
                                    task_data.pop("due_date", None))
                task.recurrence_count = task_data.pop("recurrence_count", 0)
                task.last_completed = task_data.pop("last_completed", None)
            else:
                continue  # Skip unknown task types
            
            # Set common properties
            task.id = task_data.pop("id")
            task.status = task_data.pop("status")
            task.created_at = task_data.pop("created_at")
            task.updated_at = task_data.pop("updated_at")
            task.completion_date = task_data.pop("completion_date", None)
            task.tags = set(task_data.pop("tags", []))
            
            # Add task to manager
            self.tasks[task.id] = task
        
        return True


class TaskFilter:
    """Applies filters to collections of tasks."""
    
    @staticmethod
    def filter_by_date_range(tasks, start_date, end_date):
        """Filter tasks that have due dates within a specific range."""
        return [task for task in tasks if task.due_date and start_date <= task.due_date <= end_date]
    
    @staticmethod
    def filter_by_multiple_tags(tasks, tags):
        """Filter tasks that have all the specified tags."""
        return [task for task in tasks if all(tag.lower() in task.tags for tag in tags)]
    
    @staticmethod
    def filter_by_effort(tasks, effort_level):
        """Filter tasks by their estimated effort level."""
        return [task for task in tasks if task.estimate_effort() == effort_level]


# CLI interface for the Task Management System
def main():
    task_manager = TaskManager()
    
    # Try to load existing tasks from file
    if os.path.exists("tasks.json"):
        print("Loading tasks from file...")
        task_manager.load_from_file("tasks.json")
        print(f"Loaded {len(task_manager.tasks)} tasks.")
    
    while True:
        print("\n===== Task Management System =====")
        print("1. Create new task")
        print("2. List tasks")
        print("3. Update task status")
        print("4. Add tag to task")
        print("5. View task details")
        print("6. Delete task")
        print("7. Save tasks")
        print("8. Exit")
        
        choice = input("\nEnter your choice (1-8): ")
        
        if choice == "1":
            # Create new task
            print("\n--- Create New Task ---")
            title = input("Task title: ")
            description = input("Description (optional): ")
            
            print("Priority: ")
            for i, priority in enumerate(Priority, 1):
                print(f"{i}. {priority.name}")
            
            try:
                priority_choice = int(input("Select priority (1-4): "))
                priority = list(Priority)[priority_choice - 1]
            except (ValueError, IndexError):
                print("Invalid priority. Using MEDIUM as default.")
                priority = Priority.MEDIUM
            
            due_date = input("Due date (YYYY-MM-DD, leave blank for none): ")
            if due_date:
                try:
                    due_date = datetime.strptime(due_date, "%Y-%m-%d")
                except ValueError:
                    print("Invalid date format. No due date will be set.")
                    due_date = None
            else:
                due_date = None
            
            print("Task type:")
            print("1. Simple Task")
            print("2. Project Task")
            print("3. Recurring Task")
            
            task_type = input("Select task type (1-3): ")
            
            if task_type == "2":
                project = input("Project name: ")
                estimated_hours = input("Estimated hours (default 1.0): ")
                
                try:
                    estimated_hours = float(estimated_hours) if estimated_hours else 1.0
                except ValueError:
                    estimated_hours = 1.0
                
                task = ProjectTask(title, project, description, priority, due_date)
                task.set_estimate(estimated_hours)
            
            elif task_type == "3":
                print("Frequency:")
                print("1. Daily")
                print("2. Weekly")
                print("3. Monthly")
                print("4. Yearly")
                
                freq_choice = input("Select frequency (1-4): ")
                frequencies = ["daily", "weekly", "monthly", "yearly"]
                
                try:
                    frequency = frequencies[int(freq_choice) - 1]
                except (ValueError, IndexError):
                    print("Invalid frequency. Using weekly as default.")
                    frequency = "weekly"
                
                task = RecurringTask(title, frequency, description, priority, due_date)
            
            else:  # Default to simple task
                task = SimpleTask(title, description, priority, due_date)
            
            task_manager.add_task(task)
            print(f"Task created with ID: {task.id}")
        
        elif choice == "2":
            # List tasks
            print("\n--- Task List ---")
            print("Filter by:")
            print("1. All tasks")
            print("2. By status")
            print("3. By priority")
            print("4. By tag")
            print("5. Overdue tasks")
            
            filter_choice = input("Select filter (1-5): ")
            
            if filter_choice == "2":
                print("Status:")
                for i, status in enumerate(TaskStatus, 1):
                    print(f"{i}. {status.name}")
                
                try:
                    status_choice = int(input("Select status (1-5): "))
                    status = list(TaskStatus)[status_choice - 1]
                    tasks = task_manager.get_tasks_by_status(status)
                except (ValueError, IndexError):
                    print("Invalid status. Showing all tasks.")
                    tasks = list(task_manager.tasks.values())
            
            elif filter_choice == "3":
                print("Priority:")
                for i, priority in enumerate(Priority, 1):
                    print(f"{i}. {priority.name}")
                
                try:
                    priority_choice = int(input("Select priority (1-4): "))
                    priority = list(Priority)[priority_choice - 1]
                    tasks = task_manager.get_tasks_by_priority(priority)
                except (ValueError, IndexError):
                    print("Invalid priority. Showing all tasks.")
                    tasks = list(task_manager.tasks.values())
            
            elif filter_choice == "4":
                tag = input("Enter tag: ")
                tasks = task_manager.get_tasks_by_tag(tag)
            
            elif filter_choice == "5":
                tasks = task_manager.get_overdue_tasks()
            
            else:  # Default to all tasks
                tasks = list(task_manager.tasks.values())
            
            if not tasks:
                print("No tasks found matching the criteria.")
            else:
                for i, task in enumerate(tasks, 1):
                    print(f"{i}. {task}")
        
        elif choice == "3":
            # Update task status
            print("\n--- Update Task Status ---")
            task_id = input("Enter task ID: ")
            
            task = task_manager.get_task(task_id)
            if not task:
                print("Task not found.")
                continue
            
            print(f"Current status: {task.status.name}")
            print("New status:")
            for i, status in enumerate(TaskStatus, 1):
                print(f"{i}. {status.name}")
            
            try:
                status_choice = int(input("Select new status (1-5): "))
                new_status = list(TaskStatus)[status_choice - 1]
                
                if task.status != new_status:
                    if isinstance(task, RecurringTask) and new_status == TaskStatus.COMPLETED:
                        task.complete_occurrence()
                        print(f"Task marked complete and scheduled for next occurrence.")
                    else:
                        task.update_status(new_status)
                        print(f"Task status updated to {new_status.name}.")
                else:
                    print("Status unchanged.")
            except (ValueError, IndexError):
                print("Invalid status choice.")
        
        elif choice == "4":
            # Add tag to task
            print("\n--- Add Tag to Task ---")
            task_id = input("Enter task ID: ")
            
            task = task_manager.get_task(task_id)
            if not task:
                print("Task not found.")
                continue
            
            print(f"Current tags: {', '.join(task.tags) if task.tags else 'None'}")
            new_tag = input("Enter new tag: ")
            
            if new_tag:
                task.add_tag(new_tag)
                print(f"Tag '{new_tag}' added to task.")
        
        elif choice == "5":
            # View task details
            print("\n--- Task Details ---")
            task_id = input("Enter task ID: ")
            
            task = task_manager.get_task(task_id)
            if not task:
                print("Task not found.")
                continue
            
            print(f"ID: {task.id}")
            print(f"Title: {task.title}")
            print(f"Description: {task.description or 'None'}")
            print(f"Status: {task.status.name}")
            print(f"Priority: {task.priority.name}")
            print(f"Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"Last Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M')}")
            
            if task.due_date:
                print(f"Due Date: {task.due_date.strftime('%Y-%m-%d')}")
                if task.is_overdue():
                    print("⚠️ OVERDUE ⚠️")
            
            if task.completion_date:
                print(f"Completed: {task.completion_date.strftime('%Y-%m-%d %H:%M')}")
            
            print(f"Tags: {', '.join(task.tags) if task.tags else 'None'}")
            print(f"Estimated Effort: {task.estimate_effort()}")
            
            if isinstance(task, ProjectTask):
                print(f"Project: {task.project}")
                print(f"Estimated Hours: {task.estimated_hours}")
                if task.dependencies:
                    print(f"Dependencies: {len(task.dependencies)} task(s)")
            
            if isinstance(task, RecurringTask):
                print(f"Frequency: {task.frequency}")
                print(f"Recurrence Count: {task.recurrence_count}")
                if task.last_completed:
                    print(f"Last Completed: {task.last_completed.strftime('%Y-%m-%d %H:%M')}")
        
        elif choice == "6":
            # Delete task
            print("\n--- Delete Task ---")
            task_id = input("Enter task ID: ")
            
            if task_manager.delete_task(task_id):
                print("Task deleted successfully.")
            else:
                print("Task not found.")
        
        elif choice == "7":
            # Save tasks
            task_manager.save_to_file("tasks.json")
            print("Tasks saved successfully.")
        
        elif choice == "8":
            # Exit
            print("Saving tasks before exit...")
            task_manager.save_to_file("tasks.json")
            print("Thank you for using the Task Management System. Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()