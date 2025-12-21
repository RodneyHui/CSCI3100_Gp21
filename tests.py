# tests/test_database.py
import pytest
import sqlite3
import tempfile
import os
import bcrypt
import sys
from pathlib import Path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))


class TestDatabaseModule:
    """
    Comprehensive tests for the Database module that handles user authentication 
    and user management functionality.
    """
    
    @pytest.fixture
    def temp_database(self):
        """
        Creates a temporary database file for testing.
        This ensures each test runs with a clean database state.
        """
        # Create a temporary file that will be automatically cleaned up
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Set the global DB_PATH to our temporary file
        import Database
        original_db_path = Database.DB_PATH
        Database.DB_PATH = Path(db_path)
        
        # Initialize the database with required tables
        Database.InitDB()
        
        yield db_path  # This is where the test runs
        
        # Cleanup: restore original path and delete temporary file
        Database.DB_PATH = original_db_path
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_password_hashing_creates_secure_hash(self):
        """
        Test that password hashing function properly hashes passwords 
        using bcrypt algorithm. This is critical for security.
        """
        from Database import HashPassword, VerifyPassword
        
        # Test with a typical password
        test_password = "MySecurePassword123"
        hashed_password = HashPassword(test_password)
        
        # The hashed password should not be the same as plain text
        assert hashed_password != test_password
        assert isinstance(hashed_password, str)
        assert len(hashed_password) > 0
        
        # Verify the password can be checked against the hash
        assert VerifyPassword(test_password, hashed_password) is True
        
        # Wrong passwords should not verify
        assert VerifyPassword("WrongPassword", hashed_password) is False
    
    def test_password_verification_handles_edge_cases(self):
        """Test password verification with edge cases and invalid inputs."""
        from Database import VerifyPassword
        
        # Test with empty strings
        assert VerifyPassword("", "some_hash") is False
        assert VerifyPassword("password", "") is False
        
        # Test with None values (should not crash)
        assert VerifyPassword(None, "hash") is False
        assert VerifyPassword("password", None) is False
    
    def test_user_creation_successfully_adds_new_user(self, temp_database):
        """
        Test that creating a user adds them to the database with correct 
        default values and activation status.
        """
        import Database
        
        # Test data for a new user
        test_phone = 12345678
        test_name = "John Doe"
        test_position = "Developer"
        test_password = "securepassword123"
        
        # Create the user
        Database.CreateUser(test_phone, test_name, test_position, test_password)
        
        # Verify the user exists in the database
        user = Database.GetUserByPhone(test_phone)
        
        assert user is not None
        assert user["Name"] == test_name
        assert user["Position"] == test_position
        assert user["Phone number"] == test_phone
        
        # Regular users should be inactive by default
        assert user["Activation status"] == 0
        
        # Admin users should be active by default
        Database.CreateUser(87654321, "Admin User", "Admin", "adminpass")
        admin_user = Database.GetUserByPhone(87654321)
        assert admin_user["Activation status"] == 1
    
    def test_user_creation_rejects_duplicate_phone_numbers(self, temp_database):
        """
        Test that the system prevents duplicate phone number registration 
        to maintain data integrity.
        """
        import Database
        
        # Create first user
        Database.CreateUser(11111111, "First User", "User", "password1")
        
        # Attempt to create user with same phone number should raise error
        with pytest.raises(ValueError, match="Phone number already exists"):
            Database.CreateUser(11111111, "Second User", "User", "password2")
    
    def test_user_authentication_workflow(self, temp_database):
        """
        Test the complete user authentication flow including successful login, 
        wrong password, and inactive user scenarios.
        """
        import Database
        
        # Create a test user and activate them
        Database.CreateUser(12345678, "Test User", "User", "correctpassword")
        Database.ChangeActivationStatus(12345678, 1)  # Activate user
        
        # Test successful login
        user = Database.ValidateLogin(12345678, "correctpassword")
        assert user is not None
        assert user["Phone number"] == 12345678
        
        # Test wrong password
        user = Database.ValidateLogin(12345678, "wrongpassword")
        assert user is None
        
        # Test non-existent user
        user = Database.ValidateLogin(99999999, "anypassword")
        assert user is None
        
        # Test inactive user
        Database.CreateUser(22222222, "Inactive User", "User", "password")
        # Note: user remains inactive by default
        user = Database.ValidateLogin(22222222, "password")
        assert user is None
    
    def test_user_activation_status_management(self, temp_database):
        """
        Test that admin can activate and deactivate users, and that 
        these changes persist in the database.
        """
        import Database
        
        # Create a test user
        Database.CreateUser(33333333, "Status Test User", "User", "password")
        
        # User should be inactive by default
        user = Database.GetUserByPhone(33333333)
        assert user["Activation status"] == 0
        
        # Activate the user
        Database.ChangeActivationStatus(33333333, 1)
        user = Database.GetUserByPhone(33333333)
        assert user["Activation status"] == 1
        
        # Deactivate the user
        Database.ChangeActivationStatus(33333333, 0)
        user = Database.GetUserByPhone(33333333)
        assert user["Activation status"] == 0
    
    def test_nonexistent_user_returns_none(self, temp_database):
        """Test that querying a non-existent user returns None gracefully."""
        import Database
        
        user = Database.GetUserByPhone(99999999)  # Non-existent phone
        assert user is None

# Mock the DB_PATH before importing Database
import Database

def test_hash_password():
    """Test password hashing function"""
    password = "TestPassword123"
    hashed = Database.HashPassword(password)
    
    # Should return a string
    assert isinstance(hashed, str)
    
    # Should be different from original
    assert hashed != password
    
    # Should verify correctly
    assert Database.VerifyPassword(password, hashed) is True
    assert Database.VerifyPassword("WrongPassword", hashed) is False

def test_create_user_success(temp_db, sample_user_data):
    """Test user creation with valid data"""
    # Temporarily replace DB_PATH
    original_path = Database.DB_PATH
    Database.DB_PATH = temp_db
    
    try:
        Database.InitDB()
        
        # Create user
        Database.CreateUser(
            sample_user_data['phone'],
            sample_user_data['name'],
            sample_user_data['position'],
            sample_user_data['password']
        )
        
        # Verify user was created
        user = Database.GetUserByPhone(sample_user_data['phone'])
        assert user is not None
        assert user['Phone number'] == sample_user_data['phone']
        assert user['Name'] == sample_user_data['name']
        
    finally:
        Database.DB_PATH = original_path

def test_create_user_duplicate(temp_db, sample_user_data):
    """Test duplicate user creation should fail"""
    original_path = Database.DB_PATH
    Database.DB_PATH = temp_db
    
    try:
        Database.InitDB()
        
        # Create first user
        Database.CreateUser(
            sample_user_data['phone'],
            sample_user_data['name'],
            sample_user_data['position'],
            sample_user_data['password']
        )
        
        # Try to create duplicate
        with pytest.raises(ValueError, match="Phone number already exists"):
            Database.CreateUser(
                sample_user_data['phone'],
                "Another Name",
                "User",
                "AnotherPass123"
            )
            
    finally:
        Database.DB_PATH = original_path

def test_validate_login(temp_db, sample_user_data):
    """Test login validation"""
    original_path = Database.DB_PATH
    Database.DB_PATH = temp_db
    
    try:
        Database.InitDB()
        
        # Create active user
        Database.CreateUser(
            sample_user_data['phone'],
            sample_user_data['name'],
            "Admin",  # Admin accounts are auto-activated
            sample_user_data['password']
        )
        
        # Test valid login
        user = Database.ValidateLogin(
            sample_user_data['phone'],
            sample_user_data['password']
        )
        assert user is not None
        assert user['Phone number'] == sample_user_data['phone']
        
        # Test invalid password
        user = Database.ValidateLogin(
            sample_user_data['phone'],
            "WrongPassword"
        )
        assert user is None
        
        # Test non-existent user
        user = Database.ValidateLogin(9999999999, "AnyPassword")
        assert user is None
        
    finally:
        Database.DB_PATH = original_path
7. Data Structures Tests

Create tests/test_datastructures.py:

python
下载
复制
import pytest
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import DataStructures

def test_task_initialization():
    """Test Task object initialization"""
    task = DataStructures.Task(
        title="Test Task",
        status="To-Do",
        person_in_charge=1234567890,
        due_date="2024-12-31",
        creator=9876543210,
        additional_info="Test info"
    )
    
    assert task.title == "Test Task"
    assert task.Status == "To-Do"
    assert task.PersonInCharge == 1234567890
    assert task.DueDate == "2024-12-31"
    assert task.Creator == 9876543210
    assert task.AdditionalInfo == "Test info"
    assert task.ID is None
    assert isinstance(task.CreationDate, datetime)

def test_task_display(capsys):
    """Test task display method (no actual display, just ensure no errors)"""
    task = DataStructures.Task(
        title="Display Test",
        status="In Progress",
        person_in_charge=1234567890,
        due_date="2024-12-31",
        creator=9876543210,
        additional_info="Test display"
    )
    
    # Mock the kdb.GetUserByPhone to avoid database dependency
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr('DataStructures.kdb.GetUserByPhone', lambda x: ["Test User"])
        task.DisplayTask()
    
    captured = capsys.readouterr()
    assert "Display Test" in captured.out
    assert "In Progress" in captured.out

def test_kanban_board_initialization():
    """Test KanbanBoard initialization"""
    board = DataStructures.KanbanBoard()
    
    assert board.ValidStatus == ["To-Do", "In Progress", "Waiting Review", "Finished"]
    assert hasattr(board, 'AddTask')
    assert hasattr(board, 'EditTask')
    assert hasattr(board, 'DelTask')
    assert hasattr(board, 'DisplayBoard')

def test_format_date():
    """Test date formatting in Task class"""
    task = DataStructures.Task("Test", "To-Do", 123, "2024-12-31", 456, "Info")
    
    # Test with datetime object
    dt_obj = datetime(2024, 12, 25, 10, 30, 45)
    formatted = task.FormatDate(dt_obj)
    assert formatted == "2024-12-25 10:30:45"
    
    # Test with string
    assert task.FormatDate("2024-12-31") == "2024-12-31"
    
    # Test with other types
    assert task.FormatDate(123) == "123"
8. CLI Tests

Create tests/test_cli.py:

python
下载
复制
import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import CLI
from unittest.mock import patch, MagicMock

def test_handle_status_input_valid(mock_input):
    """Test status input handling with valid inputs"""
    test_cases = [
        ("1", "To-Do"),
        ("2", "In Progress"),
        ("3", "Waiting Review"),
        ("4", "Finished")
    ]
    
    for input_val, expected in test_cases:
        mock_input.return_value = input_val
        result = CLI.HandleStatusInput(Mandatory=True)
        assert result == expected

def test_handle_status_input_invalid(mock_input, capsys):
    """Test status input handling with invalid input"""
    mock_input.side_effect = ["5", "1"]  # First invalid, then valid
    
    result = CLI.HandleStatusInput(Mandatory=True)
    
    captured = capsys.readouterr()
    assert "Status is not valid" in captured.out
    assert result == "To-Do"  # Should accept second valid input

def test_handle_due_date_input_valid(mock_input):
    """Test due date input with valid future date"""
    with patch('CLI.datetime') as mock_datetime:
        # Mock today as 2024-12-20
        mock_datetime.today.return_value.date.return_value = type('obj', (object,), {'year': 2024, 'month': 12, 'day': 20})()
        mock_datetime.side_effect = datetime
        
        mock_input.return_value = "2024-12-31"
        result = CLI.HandleDueDateInput(Mandatory=True, DefaultResponse=None)
        
        assert result == "2024-12-31"

def test_handle_due_date_input_past(mock_input, capsys):
    """Test due date input with past date"""
    with patch('CLI.datetime') as mock_datetime:
        # Mock today as 2024-12-20
        mock_datetime.today.return_value.date.return_value = type('obj', (object,), {'year': 2024, 'month': 12, 'day': 20})()
        mock_datetime.side_effect = datetime
        
        mock_input.side_effect = ["2024-12-01", "2024-12-31"]
        result = CLI.HandleDueDateInput(Mandatory=True, DefaultResponse=None)
        
        captured = capsys.readouterr()
        assert "Date has already passed" in captured.out
        assert result == "2024-12-31"

def test_handle_person_in_charge_input(mock_input, capsys):
    """Test person in charge input handling"""
    with patch('CLI.kdb') as mock_kdb:
        mock_kdb.CheckUserExist.return_value = True
        mock_kdb.GetUserByPhone.return_value = ["Test User"]
        
        mock_input.return_value = "1234567890"
        result = CLI.HandlePersonInChargeInput(Mandatory=True)
        
        assert result == 1234567890
        
        captured = capsys.readouterr()
        assert "Person in charge: Test User" in captured.out

def test_handle_person_in_charge_input_nonexistent(mock_input, capsys):
    """Test person in charge input with non-existent user"""
    with patch('CLI.kdb') as mock_kdb:
        mock_kdb.CheckUserExist.side_effect = [False, True]  # First call fails, second succeeds
        mock_kdb.GetUserByPhone.return_value = ["Test User"]
        
        mock_input.side_effect = ["1234567890", "9876543210"]
        result = CLI.HandlePersonInChargeInput(Mandatory=True)
        
        captured = capsys.readouterr()
        assert "Person in charge does not exist" in captured.out
        assert result == 9876543210
