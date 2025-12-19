import Database
import CLI
import Notification
import KanbanInfoDatabase as kdb

LOGIN_PAGE = """
Kanban System Login Page
Choose an option by number:
  1) Log in
  2) Register
  h) Help
  0) Exit
"""

HELP_TEXT = """
Quick help:
- Register: enter your phone, name, position, and a password (typed twice).
- Log in: use your phone number and password.
"""

def Login():

    Database.InitDB()
    printnoti = True
    
    while True:
        print(LOGIN_PAGE.strip())
        choice = input("> ").strip()

        if choice == "0":
            print("Thank you for using our system.")
            return

        elif choice == "1":
            # Login
            try:
                PhoneNo = int(input("Phone number: ").strip())
            except (ValueError, TypeError):
                print("Please enter a valid phone number")
                continue
            Password = input("Password: ").strip()
            User = Database.ValidateLogin(PhoneNo, Password)
            if User:
                print(f"\nLogin successfully.\n")
                if User.get("Position") == "Admin":
                    if printnoti:
                        Notification.PrintNotification()
                        printnoti = False
                    CLI.InteractiveMenuAdmin("~/.kanban/board.json")
                else: 
                    if printnoti:
                        Notification.PrintNotification()
                        printnoti = False
                    CLI.interactive_menu("~/.kanban/board.json")
            else:
                print("Invalid phone number or password, or your account is inactive.")

        elif choice == "2":
            # Register
            try:
                PhoneNo = int(input("Phone number: ").strip())
                if kdb.CheckUserExist(PhoneNo):
                    print("Phone number already exists.")
                    continue
            except (ValueError, TypeError):
                print("Please enter a valid phone number")
                continue
            Name = input("Name: ").strip()
            while True:
                Position = input("Position (Admin / User): ").strip().capitalize()
                if Position == "User":
                    break
                elif Position == "Admin":
                    try:
                        ValidationKey = int(input("Validation key: ").strip())
                        if ValidationKey == 3100:  
                            break
                    except (ValueError, TypeError):
                        print("Invalid key")
                    print("Validation key mismatch.")
                else: print("Invalid position.")
            Password = PasswordInput()
            Database.CreateUser(PhoneNo, Name, Position, Password)
            print("\nYou have registered the following account:")
            print(Database.GetUserByPhone(PhoneNo))
            print("")

        elif choice == "h":
            print(HELP_TEXT.strip())

        else:
            print("Invalid choice. Please enter a number from the menu.")

def PasswordInput():
    while True:
        pw1 = input("Password: ").strip()
        pw2 = input("Confirm password: ").strip()
        if pw1 != pw2:
            print("Passwords do not match. Please try again.")
            continue
        if len(pw1) < 8:
            print("Password too short (min 8 chars). Please try again.")
            continue
        return pw1    

# """
def main(argv=None):
        try:
            Login()
        except KeyboardInterrupt:
            print("\nBye.")
        return

if __name__ == "__main__":
    main()
# """
