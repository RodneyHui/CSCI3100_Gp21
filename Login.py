import Database


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

"""

def Login():

    while True:
        print(LOGIN_PAGE.strip())
        choice = input("> ").strip()

        if choice == "0":
            print("Thank you for using our system.")
            return

        elif choice == "1":
            # Login
            PhoneNo = int(input("Phone number: ").strip())

        elif choice == "2":
            # Register
            PhoneNo = int(input("Phone number: ").strip())
            Name = input("Name: ").strip()
            Position = input("Position: ").strip()
            Database.CreateUser(PhoneNo, Name, Position)
            print(Database.GetUserByPhone(PhoneNo))

        elif choice == "h":
            print(HELP_TEXT.strip())

        else:
            print("Invalid choice. Please enter a number from the menu.")


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
