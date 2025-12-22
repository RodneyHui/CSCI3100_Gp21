from MyKanban import Login
from MyKanban import License

def main(argv=None):
        
        if License.LicenseInput():
            try:
                Login.Login()
            except KeyboardInterrupt:
                print("\nKeyboard Interrupt.")
                return
        else:
             print("You have no access to this system.")
             return

if __name__ == "__main__":
    main()