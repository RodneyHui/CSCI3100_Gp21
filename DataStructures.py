from datetime import datetime as dt
import KanbanInfoDatabase as kdb

class Task:
    def __init__(self, Title, Status, PersonInCharge, DueDate, Creator, AdditionalInfo, CreationDate=None, Editors=None, ID=None):
        self.title = Title
        self.Status = Status
        self.PersonInCharge = PersonInCharge
        self.CreationDate = dt.now() if CreationDate is None else CreationDate
        self.DueDate = DueDate
        self.Creator = Creator
        self.Editors = Editors
        self.AdditionalInfo = AdditionalInfo
        self.ID = ID

    def FormatDate(self, date_obj):
        if isinstance(date_obj, str):
            return date_obj
        if isinstance(date_obj, dt):
            return date_obj.strftime("%Y-%m-%d %H:%M:%S")
        return str(date_obj)
    
    def DisplayTask(self):
        print("\n" + "-"*50)
        print(f"Task {self.ID}: {self.title}")
        print("-"*50)
        
        # Handle None values safely
        assigned_to = kdb.GetUserByPhone(self.PersonInCharge) if self.PersonInCharge else "Unassigned"
        created_by = kdb.GetUserByPhone(self.Creator) if self.Creator else "Unknown"
        editors = kdb.GetUserByPhone(self.Editors) if self.Editors else "None"
        
        print(f"Status: {self.Status}")
        print(f"Assigned to: {assigned_to}")
        print(f"CreationTime: {self.FormatDate(self.CreationDate)}")
        print(f"Due: {self.DueDate}")
        print(f"Created by: {created_by}")
        print(f"Editors: {editors}")
        print(f"Additional Info: {self.AdditionalInfo}")
        print("\n" + "-"*50)
    
    def __str__(self):
        id_str = f"ID: {self.ID}, " if self.ID is not None else ""
        return f"{id_str}Task: {self.title}, Status: {self.Status}, Assigned to: {self.PersonInCharge}, CreationTime: {self.FormatDate(self.CreationDate)}, Due: {self.DueDate}, Created by: {self.Creator}, Editors: {self.Editors}, Additional Info: {self.AdditionalInfo}"

class KanbanBoard:
    def __init__(self):
        kdb.InitDB()
        self.ValidStatus = ["To-Do", "In Progress", "Waiting Review", "Finished"]

    def AddTask(self, Title, Status, PersonInCharge, DueDate, Creator, AdditionalInfo):
        if Status in self.ValidStatus:
            task = Task(Title, Status, PersonInCharge, DueDate, Creator, AdditionalInfo)
            kdb.AddTask(Title, Status, PersonInCharge, task.CreationDate, DueDate, Creator, AdditionalInfo)
            print(f"Added: {Title}")
            return True
        else:
            print(f"Add Task Failed: Status '{Status}' is not valid. Valid statuses: {', '.join(self.ValidStatus)}")
            return False

    def EditTask(self, index, Editor, NewTitle=None, NewStatus=None, NewPersonInCharge=None, NewDueDate=None, NewAdditionalInfo=None):
        try:
            Temp = kdb.GetTaskByID(index)
            if Temp is None:
                print("Task not found.")
                return False
            
            task = Task(
                Temp[1],  # Title
                Temp[2],  # Status
                Temp[3],  # PersonInCharge
                Temp[5],  # DueDate
                Temp[6],  # Creator
                Temp[8],  # AdditionalInfo
                Temp[4],  # CreationDate
                Temp[7],  # Editors
                Temp[0]   # ID
            )
            
            # Update editor
            task.Editors = Editor
            
            # Validate status before applying
            if NewStatus and NewStatus not in self.ValidStatus:
                print(f"Edit Task Failed: Status '{NewStatus}' is not valid.")
                return False
            
            # Apply updates
            if NewTitle:
                task.title = NewTitle
            if NewStatus:
                task.Status = NewStatus
            if NewPersonInCharge:
                task.PersonInCharge = NewPersonInCharge
            if NewDueDate:
                task.DueDate = NewDueDate
            if NewAdditionalInfo:
                task.AdditionalInfo = NewAdditionalInfo
                
            kdb.EditTask(index, task.title, task.Status, task.PersonInCharge, task.DueDate, task.Editors, task.AdditionalInfo)
            print(f"Task updated: {task.title}")
            return True
            
        except (IndexError, TypeError) as e:
            print(f"Task not found. Error: {e}")
            return False

    def DelTask(self, index):
        try:
            Temp = kdb.GetTaskByID(index)
            if Temp is None:
                print("Task not found.")
                return False
    
            removed_task = Task(
                Temp[1],  # Title
                Temp[2],  # Status
                Temp[3],  # PersonInCharge
                Temp[5],  # DueDate
                Temp[6],  # Creator
                Temp[8],  # AdditionalInfo
                Temp[4],  # CreationDate
                Temp[7],  # Editors
                Temp[0]   # ID
            )
            
            kdb.DelTask(index)
            print(f"Deleted: {removed_task.title}")
            return True
            
        except (IndexError, TypeError) as e:
            print(f"Task not found. Error: {e}")
            return False

    def DisplayBoard(self):
        temp = kdb.GetAllTasks()
        tasks = []
        for i in temp:
            # FIXED: Correct parameter order
            tasks.append(Task(i[1], i[2], i[3], i[5], i[6], i[8], i[4], i[7], i[0]))
        
        # Sort tasks by due date (safer string sorting)
        try:
            sorted_tasks = sorted(tasks, key=lambda x: x.DueDate)
        except Exception:
            sorted_tasks = tasks  # Fallback if sorting fails
        
        # Group tasks by status
        grouped_tasks = {status: [] for status in self.ValidStatus}
        for task in sorted_tasks:
            if task.Status in grouped_tasks:
                grouped_tasks[task.Status].append(task)
        
        print("\n" + "-"*50)
        print(f"{'Kanban Board':^50}")
        print("-"*50)
        
        for status in self.ValidStatus:
            if grouped_tasks[status]: 
                print(f"\n{status.upper()}:")
                for task in grouped_tasks[status]:
                    person_info = kdb.GetUserByPhone(task.PersonInCharge)
                    person_name = person_info[0] if person_info and len(person_info) > 0 else "Unknown"
                    print(f" - Task {task.ID}: {task.title} (Due: {task.DueDate}, Assigned to: {person_name})")
        
        print("\n" + "-"*50)
