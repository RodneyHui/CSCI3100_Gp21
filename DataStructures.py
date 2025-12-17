"""
Enhanced Task and KanbanBoard Classes
Refactored with improved architecture, type safety, and performance optimizations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
import KanbanInfoDatabase as kdb


class TaskStatus(Enum):
    """Enumeration for task status to ensure type safety"""
    TO_DO = "To-Do"
    IN_PROGRESS = "In Progress"
    WAITING_REVIEW = "Waiting Review"
    FINISHED = "Finished"
    
    @classmethod
    def get_valid_statuses(cls) -> List[str]:
        """Get list of all valid status values"""
        return [status.value for status in cls]
    
    @classmethod
    def from_number(cls, status_num: int) -> Optional[str]:
        """Convert numeric input to status string"""
        status_map = {
            1: cls.TO_DO.value,
            2: cls.IN_PROGRESS.value,
            3: cls.WAITING_REVIEW.value,
            4: cls.FINISHED.value
        }
        return status_map.get(status_num)


class Task:
    """
    Enhanced Task class with improved encapsulation, validation, and functionality
    """
    
    def __init__(self, 
                 title: str,
                 status: str,
                 person_in_charge: int,
                 due_date: str,
                 creator: int,
                 additional_info: str = "",
                 creation_date: Optional[Union[datetime, str]] = None,
                 editors: Optional[int] = None,
                 task_id: Optional[int] = None):
        """
        Initialize a Task with comprehensive validation
        
        Args:
            title: Task title (required)
            status: Task status from TaskStatus enum
            person_in_charge: Phone number of responsible person
            due_date: Due date in YYYY-MM-DD format
            creator: Phone number of task creator
            additional_info: Additional task details
            creation_date: Task creation date (auto-generated if not provided)
            editors: Phone number of last editor
            task_id: Unique task identifier
        """
        self._validate_constructor_args(title, status, person_in_charge, creator)
        
        self._task_id = task_id
        self._title = title.strip()
        self._status = self._validate_status(status)
        self._person_in_charge = person_in_charge
        self._due_date = due_date
        self._creator = creator
        self._additional_info = additional_info
        self._editors = editors
        self._creation_date = self._initialize_creation_date(creation_date)
    
    def _validate_constructor_args(self, title: str, status: str, 
                                 person_in_charge: int, creator: int) -> None:
        """Validate required constructor arguments"""
        if not title or not title.strip():
            raise ValueError("Task title cannot be empty")
        if not status:
            raise ValueError("Task status cannot be empty")
        if not isinstance(person_in_charge, int) or person_in_charge <= 0:
            raise ValueError("Person in charge must be a positive integer")
        if not isinstance(creator, int) or creator <= 0:
            raise ValueError("Creator must be a positive integer")
    
    def _validate_status(self, status: str) -> str:
        """Validate and normalize task status"""
        valid_statuses = TaskStatus.get_valid_statuses()
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        return status
    
    def _initialize_creation_date(self, creation_date: Optional[Union[datetime, str]]) -> datetime:
        """Initialize creation date with proper type handling"""
        if creation_date is None:
            return datetime.now()
        elif isinstance(creation_date, str):
            return datetime.fromisoformat(creation_date.replace('Z', '+00:00'))
        elif isinstance(creation_date, datetime):
            return creation_date
        else:
            raise TypeError("Creation date must be datetime, ISO string, or None")
    
    # Property-based interface for better encapsulation
    @property
    def task_id(self) -> Optional[int]:
        return self._task_id
    
    @task_id.setter
    def task_id(self, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Task ID must be a positive integer")
        self._task_id = value
    
    @property
    def title(self) -> str:
        return self._title
    
    @title.setter
    def title(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Task title cannot be empty")
        self._title = value.strip()
    
    @property
    def status(self) -> str:
        return self._status
    
    @status.setter
    def status(self, value: str) -> None:
        self._status = self._validate_status(value)
    
    @property
    def person_in_charge(self) -> int:
        return self._person_in_charge
    
    @person_in_charge.setter
    def person_in_charge(self, value: int) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Person in charge must be a positive integer")
        if not kdb.CheckUserExist(value):
            raise ValueError(f"User {value} does not exist")
        self._person_in_charge = value
    
    @property
    def due_date(self) -> str:
        return self._due_date
    
    @due_date.setter
    def due_date(self, value: str) -> None:
        if not self._is_valid_date_format(value):
            raise ValueError("Due date must be in YYYY-MM-DD format")
        self._due_date = value
    
    @property
    def creator(self) -> int:
        return self._creator
    
    @property
    def editors(self) -> Optional[int]:
        return self._editors
    
    @editors.setter
    def editors(self, value: Optional[int]) -> None:
        if value is not None and (not isinstance(value, int) or value <= 0):
            raise ValueError("Editors must be a positive integer or None")
        if value is not None and not kdb.CheckUserExist(value):
            raise ValueError(f"Editor user {value} does not exist")
        self._editors = value
    
    @property
    def additional_info(self) -> str:
        return self._additional_info
    
    @additional_info.setter
    def additional_info(self, value: str) -> None:
        self._additional_info = value
    
    @property
    def creation_date(self) -> datetime:
        return self._creation_date
    
    def _is_valid_date_format(self, date_str: str) -> bool:
        """Validate date format without throwing exceptions"""
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def format_date(self, date_obj: Optional[Union[datetime, str]]) -> str:
        """
        Format date for display, handling both datetime objects and strings
        
        Args:
            date_obj: Date to format (datetime or ISO string)
            
        Returns:
            Formatted date string
        """
        if date_obj is None:
            return "Not set"
        
        if isinstance(date_obj, str):
            # Already formatted or ISO string
            if " " in date_obj and ":" in date_obj:
                return date_obj  # Assume already formatted
            try:
                # Try to parse and reformat
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except ValueError:
                return date_obj  # Return as-is if can't parse
        
        if isinstance(date_obj, datetime):
            return date_obj.strftime("%Y-%m-%d %H:%M:%S")
        
        return str(date_obj)
    
    def display_task(self, detailed: bool = True) -> None:
        """
        Display task information with configurable detail level
        
        Args:
            detailed: If True, show full details; if False, show summary
        """
        separator = "\n" + "="*60
        
        if detailed:
            print(separator)
            print(f"TASK DETAILS - ID: {self.task_id or 'New'}")
            print("="*60)
            
            display_data = [
                ("Title", self.title),
                ("Status", self.status),
                ("Assigned to", self._get_user_display(self.person_in_charge)),
                ("Due Date", self.due_date),
                ("Created", self.format_date(self.creation_date)),
                ("Created by", self._get_user_display(self.creator)),
                ("Last edited by", self._get_user_display(self.editors)),
                ("Additional Info", self.additional_info or "None")
            ]
            
            for label, value in display_data:
                print(f"{label:>15}: {value}")
            
            print(separator)
        else:
            # Summary view
            due_indicator = " [OVERDUE]" if self._is_overdue() else ""
            print(f"Task {self.task_id}: {self.title} ({self.status}) - Due: {self.due_date}{due_indicator}")
    
    def _get_user_display(self, user_id: Optional[int]) -> str:
        """Get user display name with safe handling"""
        if user_id is None:
            return "Not assigned"
        
        try:
            user_info = kdb.GetUserByPhone(user_id)
            if user_info and len(user_info) > 1:
                return user_info[1]  # Assuming name is at index 1
            return f"User {user_id}"
        except Exception:
            return f"User {user_id} (info unavailable)"
    
    def _is_overdue(self) -> bool:
        """Check if task is overdue"""
        try:
            due_date = datetime.strptime(self.due_date, "%Y-%m-%d").date()
            return due_date < datetime.now().date()
        except (ValueError, TypeError):
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for serialization"""
        return {
            'id': self.task_id,
            'title': self.title,
            'status': self.status,
            'person_in_charge': self.person_in_charge,
            'due_date': self.due_date,
            'creator': self.creator,
            'editors': self.editors,
            'additional_info': self.additional_info,
            'creation_date': self.creation_date.isoformat() if self.creation_date else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create Task instance from dictionary"""
        return cls(
            title=data['title'],
            status=data['status'],
            person_in_charge=data['person_in_charge'],
            due_date=data['due_date'],
            creator=data['creator'],
            additional_info=data.get('additional_info', ''),
            creation_date=data.get('creation_date'),
            editors=data.get('editors'),
            task_id=data.get('id')
        )
    
    @classmethod
    def from_database_row(cls, row: tuple) -> 'Task':
        """
        Create Task from database row tuple
        Assumes row structure: (id, title, status, person_in_charge, creation_date, 
                              due_date, creator, editors, additional_info)
        """
        if len(row) < 9:
            raise ValueError(f"Invalid row format. Expected 9 columns, got {len(row)}")
        
        return cls(
            task_id=row[0],
            title=row[1],
            status=row[2],
            person_in_charge=row[3],
            due_date=row[5],
            creator=row[6],
            additional_info=row[8],
            creation_date=row[4],
            editors=row[7]
        )
    
    def __str__(self) -> str:
        """String representation for logging and debugging"""
        return (f"Task(id={self.task_id}, title='{self.title}', status='{self.status}', "
                f"due_date='{self.due_date}', assigned_to={self.person_in_charge})")
    
    def __repr__(self) -> str:
        """Technical representation for debugging"""
        return (f"Task(title='{self.title}', status='{self.status}', "
                f"person_in_charge={self.person_in_charge}, due_date='{self.due_date}')")
    
    def __eq__(self, other) -> bool:
        """Equality comparison based on task ID"""
        if not isinstance(other, Task):
            return False
        return self.task_id is not None and self.task_id == other.task_id
    
    def get_time_until_due(self) -> Optional[str]:
        """Get human-readable time until due date"""
        try:
            due_date = datetime.strptime(self.due_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            delta = due_date - today
            
            if delta.days < 0:
                return f"Overdue by {-delta.days} days"
            elif delta.days == 0:
                return "Due today"
            elif delta.days == 1:
                return "Due tomorrow"
            elif delta.days < 7:
                return f"Due in {delta.days} days"
            elif delta.days < 30:
                weeks = delta.days // 7
                return f"Due in {weeks} week{'s' if weeks > 1 else ''}"
            else:
                months = delta.days // 30
                return f"Due in {months} month{'s' if months > 1 else ''}"
        except ValueError:
            return None


class KanbanBoard:
    """
    Enhanced Kanban board with improved performance, error handling, and architecture
    """
    
    def __init__(self, auto_init_db: bool = True):
        """
        Initialize Kanban board
        
        Args:
            auto_init_db: Whether to automatically initialize database
        """
        if auto_init_db:
            kdb.InitDB()
        
        self._valid_statuses = TaskStatus.get_valid_statuses()
        self._tasks_cache = None  # Cache for performance
        self._cache_dirty = True  # Flag to indicate cache needs refresh
    
    @property
    def valid_statuses(self) -> List[str]:
        """Get list of valid status values"""
        return self._valid_statuses.copy()
    
    def add_task(self, title: str, status: str, person_in_charge: int, 
                 due_date: str, creator: int, additional_info: str = "") -> bool:
        """
        Add a new task to the kanban board with comprehensive validation
        
        Args:
            title: Task title
            status: Task status
            person_in_charge: Responsible person's phone number
            due_date: Due date in YYYY-MM-DD format
            creator: Creator's phone number
            additional_info: Additional task information
            
        Returns:
            True if task was added successfully, False otherwise
        """
        try:
            # Validate inputs
            if not self._is_valid_status(status):
                print("Add Task Failed: Status is not valid")
                return False
            
            if not kdb.CheckUserExist(person_in_charge):
                print(f"Add Task Failed: Person in charge {person_in_charge} does not exist")
                return False
            
            if not kdb.CheckUserExist(creator):
                print(f"Add Task Failed: Creator {creator} does not exist")
                return False
            
            # Create and validate task
            task = Task(title, status, person_in_charge, due_date, creator, additional_info)
            
            # Persist to database
            kdb.AddTask(
                task.title, task.status, task.person_in_charge, 
                task.creation_date, task.due_date, task.creator, task.additional_info
            )
            
            print(f"✓ Added: {title}")
            self._invalidate_cache()
            return True
            
        except Exception as e:
            print(f"✗ Add Task Failed: {e}")
            return False
    
    def edit_task(self, task_id: int, editor: int, **updates) -> bool:
        """
        Edit task with partial updates and validation
        
        Args:
            task_id: ID of task to edit
            editor: Phone number of editor
            **updates: Field updates (NewTitle, NewStatus, NewPersonInCharge, etc.)
            
        Returns:
            True if edit successful, False otherwise
        """
        try:
            # Verify task exists
            task_data = kdb.GetTaskByID(task_id)
            if not task_data:
                print("Edit Task Failed: Task not found")
                return False
            
            # Verify editor exists
            if not kdb.CheckUserExist(editor):
                print(f"Edit Task Failed: Editor {editor} does not exist")
                return False
            
            # Create task object from current data
            current_task = Task.from_database_row(task_data)
            
            # Apply updates with validation
            updated_fields = self._apply_task_updates(current_task, updates, editor)
            if not updated_fields:
                print("No valid changes specified")
                return True  # No changes needed, but not an error
            
            # Persist changes
            kdb.EditTask(
                task_id, 
                current_task.title, 
                current_task.status, 
                current_task.person_in_charge, 
                current_task.due_date, 
                current_task.editors, 
                current_task.additional_info
            )
            
            print(f"✓ Updated task {task_id}: {', '.join(updated_fields)}")
            self._invalidate_cache()
            return True
            
        except Exception as e:
            print(f"✗ Edit Task Failed: {e}")
            return False
    
    def _apply_task_updates(self, task: Task, updates: Dict[str, Any], editor: int) -> List[str]:
        """Apply updates to task with validation, return list of changed fields"""
        updated_fields = []
        
        if 'NewTitle' in updates and updates['NewTitle'] is not None:
            task.title = updates['NewTitle']
            updated_fields.append('title')
        
        if 'NewStatus' in updates and updates['NewStatus'] is not None:
            if not self._is_valid_status(updates['NewStatus']):
                raise ValueError(f"Invalid status: {updates['NewStatus']}")
            task.status = updates['NewStatus']
            updated_fields.append('status')
        
        if 'NewPersonInCharge' in updates and updates['NewPersonInCharge'] is not None:
            task.person_in_charge = updates['NewPersonInCharge']
            updated_fields.append('person_in_charge')
        
        if 'NewDueDate' in updates and updates['NewDueDate'] is not None:
            task.due_date = updates['NewDueDate']
            updated_fields.append('due_date')
        
        if 'NewAdditionalInfo' in updates and updates['NewAdditionalInfo'] is not None:
            task.additional_info = updates['NewAdditionalInfo']
            updated_fields.append('additional_info')
        
        # Always update editor if changes were made
        if updated_fields:
            task.editors = editor
            updated_fields.append('editor')
        
        return updated_fields
    
    def delete_task(self, task_id: int) -> bool:
        """
        Delete a task by ID
        
        Args:
            task_id: ID of task to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            # Verify task exists
            task_data = kdb.GetTaskByID(task_id)
            if not task_data:
                print("Delete Task Failed: Task not found")
                return False
            
            task = Task.from_database_row(task_data)
            kdb.DelTask(task_id)
            
            print(f"✓ Deleted: {task.title}")
            self._invalidate_cache()
            return True
            
        except Exception as e:
            print(f"✗ Delete Task Failed: {e}")
            return False
    
    def delete_tasks_batch(self, task_ids: List[int]) -> Dict[str, Any]:
        """
        Delete multiple tasks with batch operation results
        
        Args:
            task_ids: List of task IDs to delete
            
        Returns:
            Dictionary with results summary
        """
        results = {
            'successful': [],
            'failed': [],
            'not_found': []
        }
        
        for task_id in task_ids:
            try:
                if self.delete_task(task_id):
                    results['successful'].append(task_id)
                else:
                    results['failed'].append(task_id)
            except Exception as e:
                results['failed'].append((task_id, str(e)))
        
        return results
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """Get single task by ID"""
        try:
            task_data = kdb.GetTaskByID(task_id)
            if task_data:
                return Task.from_database_row(task_data)
            return None
        except Exception as e:
            print(f"Error retrieving task {task_id}: {e}")
            return None
    
    def get_all_tasks(self, force_refresh: bool = False) -> List[Task]:
        """Get all tasks with optional caching"""
        if not force_refresh and not self._cache_dirty and self._tasks_cache is not None:
            return self._tasks_cache
        
        try:
            tasks_data = kdb.GetAllTasks()
            tasks = []
            
            for row in tasks_data:
                try:
                    task = Task.from_database_row(row)
                    tasks.append(task)
                except (ValueError, IndexError) as e:
                    print(f"Warning: Skipping invalid task data: {e}")
                    continue
            
            # Cache the results
            self._tasks_cache = tasks
            self._cache_dirty = False
            return tasks
            
        except Exception as e:
            print(f"Error retrieving tasks: {e}")
            return []
    
    def display_board(self, group_by_status: bool = True, sort_by: str = "due_date") -> None:
        """
        Display the kanban board with flexible organization options
        
        Args:
            group_by_status: Whether to group tasks by status
            sort_by: Field to sort by ('due_date', 'title', 'assignee')
        """
        tasks = self.get_all_tasks()
        
        if not tasks:
            print("\n" + "="*50)
            print("No tasks found in the system")
            print("="*50)
            return
        
        # Sort tasks
        sorted_tasks = self._sort_tasks(tasks, sort_by)
        
        print("\n" + "="*50)
        print(f"{'KANBAN BOARD':^50}")
        print("="*50)
        print(f"Total tasks: {len(tasks)}")
        print("-"*50)
        
        if group_by_status:
            self._display_grouped_by_status(sorted_tasks)
        else:
            self._display_flat_list(sorted_tasks)
        
        print("="*50)
    
    def _sort_tasks(self, tasks: List[Task], sort_by: str) -> List[Task]:
        """Sort tasks by specified field"""
        if sort_by == "due_date":
            return sorted(tasks, key=lambda x: (x.due_date, x.title))
        elif sort_by == "title":
            return sorted(tasks, key=lambda x: x.title.lower())
        elif sort_by == "assignee":
            return sorted(tasks, key=lambda x: (self._get_user_name(x.person_in_charge), x.due_date))
        else:
            return sorted(tasks, key=lambda x: x.due_date)  # Default sort
    
    def _display_grouped_by_status(self, tasks: List[Task]) -> None:
        """Display tasks grouped by status"""
        grouped_tasks = {status: [] for status in self.valid_statuses}
        
        for task in tasks:
            if task.status in grouped_tasks:
                grouped_tasks[task.status].append(task)
            else:
                # Handle tasks with invalid status
                if "Invalid" not in grouped_tasks:
                    grouped_tasks["Invalid"]
