from pathlib import Path

LICENSE_FILE = Path("license_keys.txt")

def LicenseInput() -> bool:
    Trial = 3
    for i in range(Trial):
        try:
            key = input("Enter license key: ").strip()
        except EOFError:
            return ""
        

        if ValidateLicense(key):
            print("License verified.")
            return True
        else: print("Invalid license key. Please try again.")
    print("License verification failed.")
    return False

def LoadLicenseKeys() -> set[str]:
    if not LICENSE_FILE.exists():
        return None
    keys = []
    with LICENSE_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            keys.append(s)
    return keys

def ValidateLicense(key: str) -> bool:
    if key is None:
        return False
    keys = LoadLicenseKeys()
    match = key in keys
    return match