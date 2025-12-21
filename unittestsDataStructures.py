import pytest
from datetime import datetime
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.abspath('.'))

# We'll use mocking to avoid dependencies
from unittest.mock import Mock, patch, MagicMock

class TestTaskClass:
    """Test the Task class from DataStructures.py"""
    
    def test_task_creation_basic(self):
        """Test creating a Task with minimal parameters."""
        # First, we need to mock the kdb module
        mock_kdb = Mock()
        mock_kdb.GetUserByPhone = Mock(return_value=["Test User"])
        
        # Mock the module import
        with patch.dict('sys.modules', {'KanbanInfoDatabase': mock_kdb}):
            # Now import DataStructures
            import DataStructures
            
            # Create a task
            task = DataStructures.Task(
                Title="Test Task",
                Status="To-Do",
                PersonInCharge=1234567890,
                DueDate="2024-12-31",
                Creator=9876543210,
                AdditionalInfo="Test info"
            )
            
            # Verify basic attributes
            assert task.title == "Test Task"
            assert task.Status == "To-Do"
            assert task.PersonInCharge == 1234567890
            assert task.DueDate == "2024-12-31"
            assert task.Creator == 9876543210
            assert task.AdditionalInfo == "Test info"
            assert task.ID is None
            assert isinstance(task.CreationDate, datetime)
    
    def test_task_creation_full(self):
        """Test creating a Task with all parameters."""
        mock_kdb = Mock()
        mock_kdb.GetUserByPhone = Mock(return_value=["Test User"])
        
        with patch.dict('sys.modules', {'KanbanInfoDatabase': mock_kdb}):
            import DataStructures
            
            fixed_date = datetime(2024, 1, 1, 10, 30, 0)
            task = DataStructures.Task(
                Title="Complete Task",
                Status="In Progress",
                PersonInCharge=1111111111,
                DueDate="2024-06-30",
                Creator=2222222222,
                AdditionalInfo="Important task",
                CreationDate=fixed_date,
                Editors=3333333333,
                ID=42
            )
            
            assert task.title == "Complete Task"
            assert task.Status == "In Progress"
            assert task.PersonInCharge == 1111111111
            assert task.DueDate == "2024-06-30"
            assert task.Creator == 2222222222
            assert task.AdditionalInfo == "Important task"
            assert task.CreationDate == fixed_date
            assert task.Editors == 3333333333
            assert task.ID == 42
    
    def test_format_date_datetime(self):
        """Test FormatDate with datetime object."""
        mock_kdb = Mock()
        mock_kdb.GetUserByPhone = Mock(return_value=["Test User"])
        
        with patch.dict('sys.modules', {'KanbanInfoDatabase': mock_kdb}):
            import DataStructures
            
            task = DataStructures.Task("Test", "To-Do", 123, "2024-12-31", 456, "Info")
            
            # Test with datetime
            test_dt = datetime(2024, 3, 15, 14, 30, 45)
            result = task.FormatDate(test_dt)
            
            assert result == "2024-03-15 14:30:45"
    
    def test_format_date_string(self):
        """Test FormatDate with string (should return unchanged)."""
        mock_kdb = Mock()
        mock_kdb.GetUserByPhone = Mock(return_value=["Test User"])
        
        with patch.dict('sys.modules', {'KanbanInfoDatabase': mock_kdb}):
            import DataStructures
            
            task = DataStructures.Task("Test", "To-Do", 123, "2024-12-31", 456, "Info")
            
            # Test with string
            date_string = "2024-03-15"
            result = task.FormatDate(date_string)
            
            assert result == date_string
    
    def test_format_date_other_types(self):
        """Test FormatDate with None and integer."""
        mock_kdb = Mock()
        mock_kdb.GetUserByPhone = Mock(return_value=["Test User"])
        
        with patch.dict('sys.modules', {'KanbanInfoDatabase': mock_kdb}):
            import DataStructures
            
            task = DataStructures.Task("Test", "To-Do", 123, "2024-12-31", 456, "Info")
            
            # Test with None
            assert task.FormatDate(None) == "None"
            
            # Test with integer
            assert task.FormatDate(12345) == "12345"
    
    def test_str_representation(self):
        """Test the __str__ method."""
        mock_kdb = Mock()
        mock_kdb.GetUserByPhone = Mock(return_value=["Test User"])
        
        with patch.dict('sys.modules', {'KanbanInfoDatabase': mock_kdb}):
            import DataStructures
            
            fixed_date = datetime(2024, 1, 15, 10, 30, 0)
            task = DataStructures.Task(
                Title="String Test",
                Status="Finished",
                PersonInCharge=1234567890,
                DueDate="2024-12-31",
                Creator=9876543210,
                AdditionalInfo="String test info",
                CreationDate=fixed_date,
                Editors=5555555555,
                ID=7
            )
            
            result = str(task)
            
            # Check string contains all important information
            assert "ID: 7" in result
            assert "Task: String Test" in result
            assert "Status: Finished" in result
            assert "Assigned to: 1234567890" in result
            assert "CreationTime: 2024-01-15 10:30:00" in result
            assert "Due: 2024-12-31" in result
            assert "Created by: 9876543210" in result
            assert "Editors: 5555555555" in result
            assert "Additional Info: String test info" in result
    
    def test_str_representation_no_id(self):
        """Test __str__ method when task has no ID."""
        mock_kdb = Mock()
        mock_kdb.GetUserByPhone = Mock(return_value=["Test User"])
        
        with patch.dict('sys.modules', {'KanbanInfoDatabase': mock_kdb}):
            import DataStructures
            
            task = DataStructures.Task(
                Title="No ID Task",
                Status="To-Do",
                PersonInCharge=1234567890,
                DueDate="2024-12-31",
                Creator=9876543210,
                AdditionalInfo="No ID"
            )
            
            result = str(task)
            
            # Should not contain "ID: None" or "ID: "
            assert "ID:" not in result
            assert "Task: No ID Task" in result
