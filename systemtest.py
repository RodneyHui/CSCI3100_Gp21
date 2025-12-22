# Navigate to your project
cd ~/kanban_system
source venv/bin/activate

# Create system test directory
mkdir -p tests/system
touch tests/system/__init__.py

cat > tests/system/conftest.py << 'EOF'
"""
Configuration for system tests (end-to-end testing)
"""
import pytest
import sys
import os
import tempfile
import sqlite3
import bcrypt
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, Mock, MagicMock, call

# Add project root to Python path
sys.path.insert(0, os.path.abspath('.'))

@pytest.fixture
def system_test_env():
    """Create a complete system test environment with all modules."""
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Set up the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create USER table
    cursor.execute("""
        CREATE TABLE USER (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            PhoneNo INTEGER NOT NULL UNIQUE,
            Name VARCHAR2(100) NOT NULL,
            IsActive INTEGER NOT NULL DEFAULT 1,
            Position VARCHAR2(50) NOT NULL,
            PasswordHash TEXT NOT NULL
        )
    """)
    
    # Create KANBAN table
    cursor.execute("""
        CREATE TABLE KANBAN (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Title TEXT NOT NULL,
            Status TEXT NOT NULL,
            PersonInCharge INTEGER NOT NULL,
            CreationDate TEXT NOT NULL,
            DueDate TEXT NOT NULL,           
            Creator INTEGER NOT NULL,
            Editors INTEGER,
            AdditionalInfo TEXT
        )
    """)
    
    # Create test users
    test_users = [
        (1234567890, 'Admin User', 'Admin', 'AdminPass123'),
        (9876543210, 'Regular User', 'User', 'UserPass123'),
        (5555555555, 'Test User 1', 'User', 'TestPass123'),
        (1111111111, 'Test User 2', 'User', 'TestPass123'),
    ]
    
    for phone, name, position, password in test_users:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        is_active = 1 if position == 'Admin' else 1  # All active for testing
        cursor.execute(
            "INSERT INTO USER (PhoneNo, Name, IsActive, Position, PasswordHash) VALUES (?, ?, ?, ?, ?)",
            (phone, name, is_active, position, password_hash)
        )
    
    conn.commit()
    conn.close()
    
    # Create temporary license file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("0000-1111-2222-3333\n1111-2222-3333-4444\n")
        license_path = f.name
    
    yield {
        'db_path': db_path,
        'license_path': license_path,
        'users': test_users
    }
    
    # Cleanup
    for path in [db_path, license_path]:
        if os.path.exists(path):
            os.unlink(path)

@pytest.fixture
def mock_input_output():
    """Fixture to mock input and output for CLI testing."""
    with patch('builtins.input') as mock_input, \
         patch('builtins.print') as mock_print:
        yield {
            'input': mock_input,
            'print': mock_print
        }

@pytest.fixture
def patch_database_paths(system_test_env):
    """Patch database paths for all modules."""
    env = system_test_env
    
    # Import modules
    import Database
    import KanbanInfoDatabase as kdb
    
    # Save original paths
    original_paths = {
        'Database': Database.DB_PATH,
        'kdb': kdb.DB_PATH
    }
    
    # Set temporary paths
    Database.DB_PATH = env['db_path']
    kdb.DB_PATH = env['db_path']
    
    yield env
    
    # Restore original paths
    Database.DB_PATH = original_paths['Database']
    kdb.DB_PATH = original_paths['kdb']

@pytest.fixture
def patch_license_path(system_test_env):
    """Patch license file path."""
    env = system_test_env
    
    import License
    original_path = License.LICENSE_FILE
    
    License.LICENSE_FILE = Path(env['license_path'])
    
    yield env
    
    License.LICENSE_FILE = original_path
EOF

#Create tests/system/test_complete_startup.py:
cat > tests/system/test_complete_startup.py << 'EOF'
"""
System Test 1: Complete Application Startup
Testing: main.py → License.py → Login.py → CLI.py
Steps from image:
1. License validation (valid key)
2. User login (valid credentials)
3. Menu display based on role
4. Initial notifications
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock, MagicMock, call

sys.path.insert(0, os.path.abspath('.'))

class TestCompleteApplicationStartup:
    """Test the complete application startup workflow."""
    
    def test_application_startup_regular_user_flow(self, system_test_env, mock_input_output, patch_database_paths, patch_license_path):
        """Test complete startup flow for regular user."""
        env = system_test_env
        mock_io = mock_input_output
        mock_input = mock_io['input']
        mock_print = mock_io['print']
        
        import main
        import License
        import Login
        import CLI
        import Notification
        
        # Set up input sequence for regular user flow
        input_sequence = [
            '0000-1111-2222-3333',  # Valid license key
            '1',  # Choose login
            '9876543210',  # Regular user phone
            'UserPass123',  # Regular user password
            '0',  # Exit from regular menu
        ]
        
        mock_input.side_effect = input_sequence
        
        # Mock CLI functions
        mock_cli_menu = Mock()
        mock_cli_menu.side_effect = None
        
        with patch('CLI.interactive_menu', mock_cli_menu), \
             patch('Notification.PrintNotification') as mock_notification, \
             patch('Login.Database') as mock_database_module, \
             patch('Login.kdb') as mock_kdb_module:
            
            # Set up mock database responses
            mock_database_module.InitDB = Mock()
            mock_database_module.ValidateLogin.return_value = {
                'ID': 2,
                'Phone number': 9876543210,
                'Name': 'Regular User',
                'Activation status': 1,
                'Position': 'User',
                'PasswordHash': 'hashed'
            }
            
            mock_kdb_module.CheckUserExist.return_value = True
            mock_kdb_module.GetUserByPhone.return_value = ['Regular User']
            
            # Run the main function
            main.main()
            
            # Verify regular CLI menu was called
            mock_cli_menu.assert_called_once()
            
            # Verify notification was displayed
            mock_notification.assert_called_once()
    
    def test_application_startup_invalid_license(self, system_test_env, mock_input_output, patch_database_paths):
        """Test application startup with invalid license."""
        env = system_test_env
        mock_io = mock_input_output
        mock_input = mock_io['input']
        mock_print = mock_io['print']
        
        import main
        import License
        
        # Set up input sequence: 3 invalid license attempts
        input_sequence = [
            'invalid-key-1',
            'invalid-key-2',
            'invalid-key-3',
        ]
        
        mock_input.side_effect = input_sequence
        
        # Create a temporary license file with only valid keys
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("0000-1111-2222-3333\n1111-2222-3333-4444\n")
            license_path = f.name
        
        # Patch the license file path
        with patch('License.LICENSE_FILE', Path(license_path)):
            # Run the main function
            main.main()
            
            # Verify access denied message
            print_calls = [call[0] for call in mock_print.call_args_list if len(call[0]) > 0]
            access_denied_found = any("You have no access to this system" in str(call) for call in print_calls)
            assert access_denied_found, "Access denied message should be displayed"
            
            # Verify license verification failed message
            license_failed_found = any("License verification failed" in str(call) for call in print_calls)
            assert license_failed_found, "License verification failed message should be displayed"
        
        # Cleanup
        if os.path.exists(license_path):
            os.unlink(license_path)
    
    def test_application_startup_invalid_login(self, system_test_env, mock_input_output, patch_database_paths, patch_license_path):
        """Test application startup with invalid login credentials."""
        env = system_test_env
        mock_io = mock_input_output
        mock_input = mock_io['input']
        mock_print = mock_io['print']
        
        import main
        import Login
        import License
        
        # Set up input sequence
        input_sequence = [
            '0000-1111-2222-3333',  # Valid license
            '1',  # Choose login
            '9999999999',  # Invalid phone
            'wrongpass',  # Wrong password
            '0',  # Exit
        ]
        
        mock_input.side_effect = input_sequence
        
        with patch('Login.Database') as mock_database_module:
            mock_database_module.InitDB = Mock()
            mock_database_module.ValidateLogin.return_value = None  # Invalid credentials
            
            # Run the main function
            main.main()
            
            # Verify invalid credentials message
            print_calls = [call[0] for call in mock_print.call_args_list if len(call[0]) > 0]
            invalid_found = any("Invalid phone number or password" in str(call) for call in print_calls)
            assert invalid_found, "Invalid credentials message should be displayed"
    
    def test_complete_flow_with_real_modules(self, system_test_env, mock_input_output):
        """Test complete flow with actual module calls (integration style)."""
        env = system_test_env
        mock_io = mock_input_output
        mock_input = mock_io['input']
        mock_print = mock_io['print']
        
        # Import actual modules
        import Database
        import KanbanInfoDatabase as kdb
        import License
        import Login
        import CLI
        import Notification
        import main
        
        # Set database paths to our test database
        original_db_path = Database.DB_PATH
        original_kdb_path = kdb.DB_PATH
        
        Database.DB_PATH = env['db_path']
        kdb.DB_PATH = env['db_path']
        
        # Set license file path
        original_license_path = License.LICENSE_FILE
        License.LICENSE_FILE = Path(env['license_path'])
        
        try:
            # Initialize databases
            Database.InitDB()
            kdb.InitDB()
            
            # Set up input sequence for admin
            input_sequence = [
                '0000-1111-2222-3333',  # Valid license (from our test file)
                '1',  # Choose login
                '1234567890',  # Admin phone
                'AdminPass123',  # Admin password
                '0',  # Exit admin menu
            ]
            
            mock_input.side_effect = input_sequence
            
            # Mock the CLI menus to prevent infinite loops
            with patch('CLI.InteractiveMenuAdmin') as mock_admin_menu, \
                 patch('CLI.interactive_menu') as mock_regular_menu, \
                 patch('Notification.PrintNotification') as mock_notification:
                
                mock_admin_menu.side_effect = None
                mock_regular_menu.side_effect = None
                
                # Run main
                main.main()
                
                # Verify admin menu was called (not regular menu)
                mock_admin_menu.assert_called_once()
                mock_regular_menu.assert_not_called()
                
                # Verify notification was shown
                mock_notification.assert_called_once()
                
        finally:
            # Restore original paths
            Database.DB_PATH = original_db_path
            kdb.DB_PATH = original_kdb_path
            License.LICENSE_FILE = original_license_path

# Need to import Path and tempfile
import tempfile
from pathlib import Path
EOF

pytest tests/system/test_complete_startup.py -v

#Create tests/system/test_regular_user_task_lifecycle.py
cat > tests/system/test_regular_user_task_lifecycle.py << 'EOF'
"""
System Test 2: Regular User Task Lifecycle
Testing: Login.py → CLI.py → DataStructures.py → kdb.py
Steps from image:
1. User login
2. Add new task
3. Edit task details
4. Move task status
5. Delete task
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock, MagicMock, call
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath('.'))

class TestRegularUserTaskLifecycle:
    """Test complete regular user task lifecycle."""
    
    def test_regular_user_complete_task_lifecycle(self, system_test_env, mock_input_output):
        """Test the complete task lifecycle for a regular user."""
        env = system_test_env
        mock_io = mock_input_output
        mock_input = mock_io['input']
        mock_print = mock_io['print']
        
        # Import modules
        import Database
        import KanbanInfoDatabase as kdb
        import DataStructures
        import CLI
        
        # Set database paths
        original_db_path = Database.DB_PATH
        original_kdb_path = kdb.DB_PATH
        
        Database.DB_PATH = env['db_path']
        kdb.DB_PATH = env['db_path']
        
        try:
            # Initialize databases
            Database.InitDB()
            kdb.InitDB()
            
            # Test user credentials
            test_user_phone = 9876543210  # Regular user from test data
            test_user_password = "UserPass123"
            
            # Step 1: User login (simulated)
            # We'll directly validate login
            login_result = Database.ValidateLogin(test_user_phone, test_user_password)
            assert login_result is not None
            assert login_result["Phone number"] == test_user_phone
            assert login_result["Position"] == "User"
            
            print(f"✓ Step 1: User login successful")
            
            # Step 2: Add new task
            # Create KanbanBoard instance
            board = DataStructures.KanbanBoard()
            
            # Mock kdb functions to track calls
            with patch('DataStructures.kdb.AddTask') as mock_add_task, \
                 patch('DataStructures.kdb.EditTask') as mock_edit_task, \
                 patch('DataStructures.kdb.DelTask') as mock_del_task, \
                 patch('DataStructures.kdb.GetTaskByID') as mock_get_task:
                
                # Setup mock for GetTaskByID to return task data
                mock_get_task.return_value = [
                    1,  # ID
                    "Test Task",  # Title
                    "To-Do",  # Status
                    test_user_phone,  # PersonInCharge
                    "2024-01-15 10:00:00",  # CreationDate
                    "2024-12-31",  # DueDate
                    test_user_phone,  # Creator
                    None,  # Editors
                    "Test info"  # AdditionalInfo
                ]
                
                # Simulate adding a task
                add_result = board.AddTask(
                    Title="Complete Project Documentation",
                    Status="To-Do",
                    PersonInCharge=test_user_phone,
                    DueDate="2024-12-31",
                    Creator=test_user_phone,
                    AdditionalInfo="Document all system features"
                )
                
                assert add_result is True
                mock_add_task.assert_called_once()
                print(f"✓ Step 2: Add new task successful")
                
                # Step 3: Edit task details
                # Simulate editing the task
                edit_result = board.EditTask(
                    index=1,
                    Editor=test_user_phone,
                    NewTitle="Updated Project Documentation",
                    NewStatus="In Progress",
                    NewPersonInCharge=test_user_phone,
                    NewDueDate="2024-11-30",
                    NewAdditionalInfo="Updated: Include API documentation"
                )
                
                assert edit_result is True
                mock_edit_task.assert_called_once()
                print(f"✓ Step 3: Edit task details successful")
                
                # Step 4: Move task status
                # Simulate moving task to different status
                move_result = board.EditTask(
                    index=1,
                    Editor=test_user_phone,
                    NewStatus="Waiting Review"
                )
                
                assert move_result is True
                # edit_task should be called twice (once for edit, once for move)
                assert mock_edit_task.call_count == 2
                print(f"✓ Step 4: Move task status successful")
                
                # Step 5: Delete task
                # Simulate deleting the task
                delete_result = board.DelTask(1)
                
                assert delete_result is True
                mock_del_task.assert_called_once_with(1)
                print(f"✓ Step 5: Delete task successful")
            
            print("\n✅ All 5 steps completed successfully!")
            
        finally:
            # Restore original paths
            Database.DB_PATH = original_db_path
            kdb.DB_PATH = original_kdb_path
    
    def test_task_lifecycle_with_cli_input_simulation(self, system_test_env, mock_input_output):
        """Test task lifecycle with simulated CLI inputs."""
        env = system_test_env
        mock_io = mock_input_output
        mock_input = mock_io['input']
        mock_print = mock_io['print']
        
        import Database
        import KanbanInfoDatabase as kdb
        import DataStructures
        import CLI
        
        # Set database paths
        original_db_path = Database.DB_PATH
        original_kdb_path = kdb.DB_PATH
        
        Database.DB_PATH = env['db_path']
        kdb.DB_PATH = env['db_path']
        
        try:
            # Initialize databases
            Database.InitDB()
            kdb.InitDB()
            
            # Test user
            test_user_phone = 9876543210
            
            # Create a task to work with
            board = DataStructures.KanbanBoard()
            
            # Mock kdb functions
            with patch('DataStructures.kdb.AddTask') as mock_add_task, \
                 patch('DataStructures.kdb.EditTask') as mock_edit_task, \
                 patch('DataStructures.kdb.DelTask') as mock_del_task, \
                 patch('DataStructures.kdb.GetTaskByID') as mock_get_task, \
                 patch('DataStructures.kdb.GetAllTasks') as mock_get_all:
                
                # Setup mocks
                mock_add_task.return_value = None
                mock_edit_task.return_value = None
                mock_del_task.return_value = None
                
                # For GetTaskByID, return different data based on calls
                task_data = [
                    1,  # ID
                    "CLI Simulated Task",  # Title
                    "To-Do",  # Status
                    test_user_phone,  # PersonInCharge
                    "2024-01-15 10:00:00",  # CreationDate
                    "2024-12-31",  # DueDate
                    test_user_phone,  # Creator
                    None,  # Editors
                    "Created via CLI simulation"  # AdditionalInfo
                ]
                mock_get_task.return_value = task_data
                
                mock_get_all.return_value = [task_data]
                
                # Step 1: Simulate CLI inputs for adding a task
                print("\nSimulating CLI inputs for task lifecycle...")
                
                # Simulate the input sequence a user would provide
                # This is a simplified simulation - actual CLI would have menus
                
                # Add task
                board.AddTask(
                    Title="CLI Simulated Task",
                    Status="To-Do",
                    PersonInCharge=test_user_phone,
                    DueDate="2024-12-31",
                    Creator=test_user_phone,
                    AdditionalInfo="Created via CLI simulation"
                )
                
                # Verify task was added
                mock_add_task.assert_called_once()
                print("Task added via simulation")
                
                # Edit task
                board.EditTask(
                    index=1,
                    Editor=test_user_phone,
                    NewTitle="Updated CLI Task",
                    NewStatus="In Progress"
                )
                
                # Verify edit
                assert mock_edit_task.call_count >= 1
                print("Task edited via simulation")
                
                # Display board (to verify task appears)
                with patch('DataStructures.kdb.GetUserByPhone') as mock_get_user:
                    mock_get_user.return_value = ["Regular User"]
                    board.DisplayBoard()
                    print("Board displayed via simulation")
                
                # Delete task
                board.DelTask(1)
                
                # Verify deletion
                mock_del_task.assert_called_once_with(1)
                print("Task deleted via simulation")
                
                print("\n✅ CLI simulation completed successfully!")
            
        finally:
            Database.DB_PATH = original_db_path
            kdb.DB_PATH = original_kdb_path
    
    def test_error_cases_in_task_lifecycle(self, system_test_env, mock_input_output):
        """Test error cases in the task lifecycle."""
        env = system_test_env
        mock_io = mock_input_output
        mock_input = mock_io['input']
        mock_print = mock_io['print']
        
        import DataStructures
        
        # Create board
        board = DataStructures.KanbanBoard()
        
        # Test 1: Add task with invalid status
        with patch('DataStructures.kdb.AddTask') as mock_add_task:
            result = board.AddTask(
                Title="Invalid Status Task",
                Status="Invalid Status",  # Invalid!
                PersonInCharge=1234567890,
                DueDate="2024-12-31",
                Creator=9876543210,
                AdditionalInfo="Should fail"
            )
            
            assert result is False
            mock_add_task.assert_not_called()
            print("✓ Add task with invalid status correctly rejected")
        
        # Test 2: Edit non-existent task
        with patch('DataStructures.kdb.GetTaskByID', return_value=None):
            result = board.EditTask(
                index=999,  # Non-existent
                Editor=9876543210,
                NewTitle="Should not work"
            )
            
            assert result is False
            print("✓ Edit non-existent task correctly rejected")
        
        # Test 3: Edit task with invalid status
        with patch('DataStructures.kdb.GetTaskByID') as mock_get_task, \
             patch('DataStructures.kdb.EditTask') as mock_edit_task:
            
            mock_get_task.return_value = [
                1, "Test", "To-Do", 123, "2024-01-01", "2024-12-31", 456, None, "Info"
            ]
            
            result = board.EditTask(
                index=1,
                Editor=9876543210,
                NewStatus="Invalid Status"  # Invalid!
            )
            
            assert result is False
            mock_edit_task.assert_not_called()
            print("✓ Edit task with invalid status correctly rejected")
        
        # Test 4: Delete non-existent task
        with patch('DataStructures.kdb.GetTaskByID', return_value=None):
            result = board.DelTask(999)
            
            assert result is False
            print("✓ Delete non-existent task correctly rejected")
        
        print("\n✅ All error cases handled correctly!")
EOF

pytest tests/system/test_regular_user_task_lifecycle.py -v

#Create tests/system/test_administrator_workflow.py
cat > tests/system/test_administrator_workflow.py << 'EOF'
"""
System Test 3: Administrator Workflow
Testing: Login.py → CLI.py → Database.py → kdb.py
Steps from image:
1. Admin login
2. Access admin menu
3. Update user activation
4. Use regular features
"""
import pytest
import sys
import os
from unittest.mock import patch, Mock, MagicMock, call

sys.path.insert(0, os.path.abspath('.'))

class TestAdministratorWorkflow:
    """Test complete administrator workflow."""
    
    def test_admin_complete_workflow(self, system_test_env, mock_input_output):
        """Test the complete admin workflow."""
        env = system_test_env
        mock_io = mock_input_output
        mock_input = mock_io['input']
        mock_print = mock_io['print']
        
        import Database
        import KanbanInfoDatabase as kdb
        import CLI
        
        # Set database paths
        original_db_path = Database.DB_PATH
        original_kdb_path = kdb.DB_PATH
        
        Database.DB_PATH = env['db_path']
        kdb.DB_PATH = env['db_path']
        
        try:
            # Initialize databases
            Database.InitDB()
            kdb.InitDB()
            
            # Admin credentials
            admin_phone = 1234567890
            admin_password = "AdminPass123"
            
            # Step 1: Admin login
            login_result = Database.ValidateLogin(admin_phone, admin_password)
            assert login_result is not None
            assert login_result["Phone number"] == admin_phone
            assert login_result["Position"] == "Admin"
            print("✓ Step 1: Admin login successful")
            
            # Step 2: Access admin menu
            # We'll simulate what happens in the admin menu
            # The admin menu has options to update user activation and access regular system
            
            # Test the InteractiveMenuAdmin function with mocked inputs
            with patch('CLI.interactive_menu') as mock_regular_menu:
                # Simulate admin choosing to update user activation (option 1)
                # then accessing regular system (option 2)
                # then exiting (option 0)
                
                input_sequence = [
                    '1',  # Update user activation
                    '9876543210',  # User to update
                    '0',  # Set inactive (0)
                    '2',  # Access regular system
                    '0',  # Exit regular system
                    '0',  # Exit admin menu
                ]
                
                mock_input.side_effect = input_sequence
                
                # Mock Database functions
                with patch('CLI.Database') as mock_db:
                    # Setup mock responses
                    mock_db.GetUserByPhone.return_value = {
                        'ID': 2,
                        'Phone number': 9876543210,
                        'Name': 'Regular User',
                        'Activation status': 1,
                        'Position': 'User',
                        'PasswordHash': 'hashed'
                    }
                    mock_db.ChangeActivationStatus.return_value = None
                    
                    # Run admin menu
                    CLI.InteractiveMenuAdmin("~/.kanban/board.json")
                    
                    # Verify user activation was updated
                    mock_db.ChangeActivationStatus.assert_called_with(9876543210, 0)
                    print("✓ Step 3: Update user activation successful")
                    
                    # Verify regular system was accessed
                    mock_regular_menu.assert_called_once_with("~/.kanban/board.json")
                    print("✓ Step 4: Use regular features successful")
            
            print("\n✅ All admin workflow steps completed!")
            
        finally:
            Database.DB_PATH = original_db_path
            kdb.DB_PATH = original_kdb_path
    
    
    def test_admin_regular_features_access(self, system_test_env, mock_input_output):
        """Test that admin can access regular features."""
        env = system_test_env
        mock_io = mock_input_output
        mock_input = mock_io['input']
        mock_print = mock_io['print']
        
        import Database
        import KanbanInfoDatabase as kdb
        import DataStructures
        import CLI
        
        # Set database paths
        original_db_path = Database.DB_PATH
        original_kdb_path = kdb.DB_PATH
        
        Database.DB_PATH = env['db_path']
        kdb.DB_PATH = env['db_path']
        
        try:
            # Initialize databases
            Database.InitDB()
            kdb.InitDB()
            
            # Admin credentials
            admin_phone = 1234567890
            
            # Test that admin can use regular features
            # Create a board and add a task as admin
            board = DataStructures.KanbanBoard()
            
            with patch('DataStructures.kdb.AddTask') as mock_add_task:
                # Admin adds a task
                result = board.AddTask(
                    Title="Admin Created Task",
                    Status="To-Do",
                    PersonInCharge=9876543210,  # Assign to regular user
                    DueDate="2024-12-31",
                    Creator=admin_phone,  # Admin is creator
                    AdditionalInfo="Task created by admin"
                )
                
                assert result is True
                mock_add_task.assert_called_once()
                print("✓ Admin can add tasks")
            
            # Test admin can edit tasks
            with patch('DataStructures.kdb.GetTaskByID') as mock_get_task, \
                 patch('DataStructures.kdb.EditTask') as mock_edit_task:
                
                mock_get_task.return_value = [
                    1, "Task", "To-Do", 9876543210, "2024-01-01", "2024-12-31", admin_phone, None, "Info"
                ]
                
                result = board.EditTask(
                    index=1,
                    Editor=admin_phone,
                    NewStatus="In Progress"
                )
                
                assert result is True
                mock_edit_task.assert_called_once()
                print("✓ Admin can edit tasks")
            
            # Test admin can delete tasks
            with patch('DataStructures.kdb.GetTaskByID') as mock_get_task, \
                 patch('DataStructures.kdb.DelTask') as mock_del_task:
                
                mock_get_task.return_value = [
                    1, "Task", "To-Do", 9876543210, "2024-01-01", "2024-12-31", admin_phone, None, "Info"
                ]
                
                result = board.DelTask(1)
                
                assert result is True
                mock_del_task.assert_called_once_with(1)
                print("✓ Admin can delete tasks")
            
            print("\n✅ Admin can use all regular features!")
            
        finally:
            Database.DB_PATH = original_db_path
            kdb.DB_PATH = original_kdb_path
    

EOF

pytest tests/system/test_administrator_workflow.py -v

#Create tests/system/test_notification_system_flow.py
cat > tests/system/test_notification_system_flow.py << 'EOF'
"""
System Test 4: Notification System Flow
Testing: Login.py → Notification.py → kdb.py → CLI.py
Steps from image:
1. Create task with near due date
2. Login as assigned user
3. Trigger notification display
4. View task details
"""
import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch, Mock, MagicMock, call

sys.path.insert(0, os.path.abspath('.'))

class TestNotificationSystemFlow:
    """Test complete notification system workflow."""
    def test_notification_display_on_login(self, system_test_env, mock_input_output):
        """Test that notifications are displayed when user logs in."""
        env = system_test_env
        mock_io = mock_input_output
        mock_input = mock_io['input']
        mock_print = mock_io['print']
        
        import Login
        import Notification
        
        # Set up the Login module to use our test database
        original_db_path = Login.Database.DB_PATH
        original_kdb_path = Login.kdb.DB_PATH
        
        Login.Database.DB_PATH = env['db_path']
        Login.kdb.DB_PATH = env['db_path']
        
        try:
            # Initialize database
            Login.Database.InitDB()
            
            # Create a task with near due date for a specific user
            test_user_phone = 9876543210
            
            # We need to add a task to the database
            # Let's use the actual kdb module
            import KanbanInfoDatabase as kdb
            kdb.DB_PATH = env['db_path']
            kdb.InitDB()
            
            # Add a task due tomorrow
            from datetime import datetime, timedelta
            today = datetime.now().date()
            tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
            
            kdb.AddTask(
                "Login Notification Test",
                "To-Do",
                test_user_phone,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                tomorrow,
                1234567890,  # Admin creator
                "Test notification on login"
            )
            
            # Now test the login flow
            # Mock the CLI and other dependencies
            with patch('Login.CLI') as mock_cli, \
                 patch('Login.Notification') as mock_notification_module, \
                 patch('Login.License', Mock()):
                
                # Setup mocks
                mock_cli.interactive_menu = Mock()
                mock_cli.InteractiveMenuAdmin = Mock()
                
                # Mock PrintNotification to track calls
                mock_notification = Mock()
                mock_notification_module.PrintNotification = mock_notification
                
                # Set up input for login
                mock_input.side_effect = [
                    '1',  # Choose login
                    str(test_user_phone),
                    'UserPass123',
                    '0',  # Exit
                ]
                
                # Mock database responses
                with patch('Login.Database.ValidateLogin') as mock_validate:
                    mock_validate.return_value = {
                        'ID': 2,
                        'Phone number': test_user_phone,
                        'Name': 'Regular User',
                        'Activation status': 1,
                        'Position': 'User',
                        'PasswordHash': 'hashed'
                    }
                    
                    # Run login
                    try:
                        Login.Login()
                    except SystemExit:
                        pass
                    
                    # Verify notification was displayed
                    mock_notification.assert_called_once()
                    print("✓ Notifications displayed on login")
            
        finally:
            Login.Database.DB_PATH = original_db_path
            Login.kdb.DB_PATH = original_kdb_path
    
    
    def test_notification_formatting(self, system_test_env, capsys):
        """Test that notifications are formatted correctly."""
        import Notification
        
        # Create sample notifications
        notifications = [
            "\n" + "-"*50 + "\n",
            "[Task due in 2d 06h 30m]\n",
            "Task ID: 1\n",
            "Title: Test Task\n",
            "Status: To-Do\n",
            "Person in charge: Test User\n",
            "Creation date: 2024-01-15 10:00:00\n",
            "Due date: 2024-01-17\n",
            "Creator: Admin User\n",
            "Editor: None\n",
            "Additional information: Test info\n",
            "\n" + "-"*50 + "\n"
        ]
        
        # Mock UpcomingTask to return our sample
        with patch('Notification.UpcomingTask', return_value=notifications):
            # Call PrintNotification
            Notification.PrintNotification()
            
            # Capture output
            captured = capsys.readouterr()
            output = captured.out
            
            # Check formatting elements
            assert "Task ID: 1" in output
            assert "Title: Test Task" in output
            assert "Status: To-Do" in output
            assert "Person in charge: Test User" in output
            assert "Due date: 2024-01-17" in output
            assert "[Task due in" in output
            assert "-"*50 in output  # Separator line
            
            print("✓ Notifications are formatted correctly")
EOF

pytest tests/system/test_notification_system_flow.py -v
