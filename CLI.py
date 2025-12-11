import DataStructures
from pathlib import Path
import Database


MENU_SCREENS = """
Kanban - Main Menu
Choose an option by number:
  1) List tasks
  2) Add task
  3) Move task
  4) Edit task
  5) Delete task
  6) Show task
  7) Advice
  h) Help
  0) Exit
"""

ADMIN_MENU_SCREENS = """
Kanban - Administrative Menu
Choose an option by number:
  1) Update user activation status
  2) Access Kanban system
  h) Help
  0) Exit
"""

HELP_TEXT = """
Quick help:

"""

ADMIN_HELP_TEXT = """
Quick help:

"""

def interactive_menu(store: str):
    store_path = Path(store)
    store_path.parent.mkdir(parents=True, exist_ok=True)
    board = DataStructures.KanbanBoard()

    while True:
        print(MENU_SCREENS.strip())
        choice = input("> ").strip()

        if choice == "0":
            print("Logged out.")
            break
            # return

        elif choice == "1":
            #List tasks
            board.DisplayBoard()

        elif choice == "2":
            #Add task
            Title = input("Title: ").strip()
            if not Title:
                print("Title cannot be empty.")
                continue
            try:
                StatusInput = int(input("Status (1: To-Do 2: In Progress 3: Waiting Review 4: Finished): ").strip())
                if StatusInput == 1:
                    Status = "To-Do"
                elif StatusInput == 2:
                    Status = "In Progress"
                elif StatusInput == 3:
                    Status = "Waiting Review"
                elif StatusInput == 4:
                    Status = "Finished"
                else:
                    print("Status is not valid")
                    continue
            except(ValueError):
                print("Please enter a valid number.")
                continue
            PersonInCharge = input("Person in charge: ").strip()
            DueDateInput = input("Due date (YYYY-MM-DD): ").strip() 
            if DueDateInput:
                parts = DueDateInput.split("-")
                if (len(parts) == 3 and
                    parts[0].isdigit() and len(parts[0]) == 4 and  # Year
                    parts[1].isdigit() and len(parts[1]) == 2 and  # Month
                    parts[2].isdigit() and len(parts[2]) == 2):    # Day
                    DueDate = DueDateInput
                else:
                    print("Invalid date format.")
                    continue
            Creator = input("Creator: ").strip()
            if not Creator or not str(Creator).strip():
                print("Creator cannot be empty.")
                continue
            AdditionalInfo = input("Additional information: ").strip()
            board.AddTask(Title, Status, PersonInCharge, DueDate, Creator, AdditionalInfo)

        elif choice == "3":
            #Move task
            try:
                TaskID = int(input("Task ID: ").strip()) - 1
            except(ValueError):
                print("Please enter a valid number.")
                continue
            Editor = input("Name of Editor: ").strip()
            if not Editor or not str(Editor).strip():
                print("Editor cannot be empty.")
                continue
            StatusInput = (input("New status (1: To-Do 2: In Progress 3: Waiting Review 4: Finished Blank: Cancel): ").strip()) or None
            if StatusInput == None:
                Status = None
            else:
                try:
                    StatusInput = int(StatusInput)
                    if StatusInput == 1:
                        Status = "To-Do"
                    elif StatusInput == 2:
                        Status = "In Progress"
                    elif StatusInput == 3:
                        Status = "Waiting Review"
                    elif StatusInput == 4:
                        Status = "Finished"
                    else:
                        print("Status is not valid")
                        continue
                except(ValueError):
                    print("Please enter a valid number.")
                    continue
            board.EditTask(TaskID, Editor, NewStatus=Status)

        elif choice == "4":
            #Edit task

            TaskID = int(input("Task ID: ").strip()) - 1
            Editor = input("Name of Editor: ").strip()
            if not Editor or not str(Editor).strip():
                print("Editor cannot be empty.")
                continue
            Title = input("New title (blank to skip): ").strip() or None
            StatusInput = (input("New status (1: To-Do 2: In Progress 3: Waiting Review 4: Finished Blank: Skip): ").strip()) or None
            if StatusInput == None:
                Status = None
            else:
                try:
                    StatusInput = int(StatusInput)
                    if StatusInput == 1:
                        Status = "To-Do"
                    elif StatusInput == 2:
                        Status = "In Progress"
                    elif StatusInput == 3:
                        Status = "Waiting Review"
                    elif StatusInput == 4:
                        Status = "Finished"
                    else:
                        print("Status is not valid")
                        continue
                except(ValueError):
                    print("Please enter a valid number.")
                    continue
            PersonInCharge = input("New person in charge (blank to skip): ").strip() or None
            DueDateInput = input("New due date (YYYY-MM-DD) (blank to skip): ").strip() or None
            if DueDateInput == None:
                DueDate = None
            else:
                parts = DueDateInput.split("-")
                if (len(parts) == 3 and
                    parts[0].isdigit() and len(parts[0]) == 4 and  # Year
                    parts[1].isdigit() and len(parts[1]) == 2 and  # Month
                    parts[2].isdigit() and len(parts[2]) == 2):    # Day
                    DueDate = DueDateInput
                else:
                    print("Invalid date format.")
                    continue
            AdditionalInfo = input("New additional information (blank to skip): ").strip() or None
            
            #Increment TaskID to be more consistent to the display (ID displayed in List tasks: 1, actual internal ID: 0)
            board.EditTask(TaskID, Editor, NewTitle=Title, NewStatus=Status, NewPersonInCharge=PersonInCharge, NewDueDate=DueDate, NewAdditionalInfo=AdditionalInfo)

        elif choice == "5":
            #Delete task
            try:
              TaskID = int(input("Task ID: ").strip()) - 1
            except(ValueError):
                print("Please enter a valid number")
                continue
            Confirm = input(f"Confirm remove {TaskID}? (y/N): ").strip().lower()
            if Confirm == "y":
                board.DelTask(TaskID)
            else: print("Cancelled.")

        elif choice == "6":
            #Show task
            try:
                TaskID = int(input("Task ID: ").strip()) - 1
            except(ValueError):
                print("Please enter a valid number")
                continue
            try:
                board.tasks[TaskID].DisplayTask()
            except(IndexError):
                print("Task not found.")
        
        elif choice == "7":
            #Advise
            return

        elif choice == "h":
            print(HELP_TEXT.strip())

        else:
            print("Invalid choice. Please enter a number from the menu.")

def InteractiveMenuAdmin(store: str):

    while True:
        print(ADMIN_MENU_SCREENS.strip())
        choice = input("> ").strip()

        if choice == "0":
            print("Logged out.")
            break
            # return

        elif choice == "1":
            #Update user activation status
            print("Please enter the phone number of the user.")
            PhoneNo = int(input("Phone number: ").strip())
            print("The information of the user is as follow:")
            print(Database.GetUserByPhone(PhoneNo))
            while True:
                IsActive = int(input("Please set the activation status of the user (1 for active, 0 otherwise) :").strip())
                if IsActive == 1 or IsActive == 0:
                    break
                print("Invalid input.")
            Database.ChangeActivationStatus(PhoneNo, IsActive)
            print("The information has been updated.")
            print(Database.GetUserByPhone(PhoneNo))

            
        elif choice == "2":
            #Access Kanban system
            interactive_menu(store)

        elif choice == "h":
            print(ADMIN_HELP_TEXT.strip())

        else:
            print("Invalid choice. Please enter a number from the menu.")

"""
def main(argv=None):
        try:
            interactive_menu("~/.kanban/board.json")
        except KeyboardInterrupt:
            print("\nBye.")
        return

if __name__ == "__main__":
    main()
"""
