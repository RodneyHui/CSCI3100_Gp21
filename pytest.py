# tests/test_database.py
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path

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


class TestDatabaseErrorConditions:
    """Tests for error conditions and edge cases in the Database module."""
    
    def test_database_initialization_creates_required_tables(self, temp_database):
        """Test that database initialization creates the necessary table structure."""
        import Database
        
        # Verify the USER table was created
        conn = sqlite3.connect(temp_database)
        cursor = conn.cursor()
        
        # Check that USER table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='USER'")
        result = cursor.fetchone()
        assert result is not None
        assert result[0] == 'USER'
        
        # Verify table has correct columns
        cursor.execute("PRAGMA table_info(USER)")
        columns = [col[1] for col in cursor.fetchall()]
        expected_columns = ['ID', 'PhoneNo', 'Name', 'IsActive', 'Position', 'PasswordHash']
        for col in expected_columns:
            assert col in columns
        
        conn.close()
    
    def test_multiple_database_initializations_are_safe(self, temp_database):
        """
        Test that calling InitDB multiple times doesn't cause errors 
        due to IF NOT EXISTS clauses.
        """
        import Database
        
        # First initialization
        Database.InitDB()
        
        # Subsequent initializations should not fail
        Database.InitDB()
        Database.InitDB()
        
        # Database should still be functional
        Database.CreateUser(12345678, "Test User", "User", "password")
        user = Database.GetUserByPhone(12345678)
        assert user is not None
