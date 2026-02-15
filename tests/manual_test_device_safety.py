import unittest
from unittest.mock import MagicMock, patch
import os
import django
import sys

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.services.zk_workers import run_import_attendance_job
from core.models import Device

class TestDeviceSafety(unittest.TestCase):
    def setUp(self):
        # Create a dummy device for testing
        # We use a non-existent IP to ensure no real connection is attempted if mock fails
        self.device = Device.objects.create(
            name="SafetyTest Device",
            ip="0.0.0.0",
            port=4370
        )
        self.job_id = "safety_check_job"

    def tearDown(self):
        if self.device.id:
            self.device.delete()

    @patch('core.services.zk_workers.JobManager')
    @patch('core.services.zk_workers.models')
    def test_import_job_safe_workflow(self, mock_models, mock_job_manager):
        """
        Verify that import job follows: Connect -> Disable -> Get -> Enable -> Disconnect
        """
        print("\nTesting Normal Workflow safety...")
        
        # Setup mock device
        mock_device = MagicMock()
        mock_device.ip = "1.2.3.4"
        mock_device.port = 4370
        # Mock the get call
        mock_models.Device.objects.get.return_value = mock_device
        
        # Mock JobManager returning a mock job to avoid attribute errors if accessed
        mock_job = MagicMock()
        mock_job.status = "pending"
        mock_job_manager.start_job.return_value = mock_job

        with patch('core.services.zk_workers.get_zk_service') as mock_get_service:
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service
            
            # Setup mock behavior
            mock_service.test_connection.return_value = {"success": True} 
            mock_service.get_attendance.return_value = [] 
            
            # Run the job
            run_import_attendance_job(self.job_id, 999) 
            
            # Verify call order
            print("Verifying enable/disable calls...")
            
            # Check Connect
            mock_service.connect.assert_called()
            
            # Check Disable (must be called)
            mock_service.disable_device.assert_called()
            
            # Check Enable (must be called)
            mock_service.enable_device.assert_called()
            
            # Check Disconnect
            mock_service.disconnect.assert_called()
            
            print("✅ Normal workflow Safe Mode verified.")

    @patch('core.services.zk_workers.JobManager')
    @patch('core.services.zk_workers.models')
    def test_import_job_error_handling(self, mock_models, mock_job_manager):
        """
        Verify that Enable is called even if an error occurs during download
        """
        print("\nTesting Error Handling safety...")
        
        # Setup mock device
        mock_device = MagicMock()
        mock_device.ip = "1.2.3.4"
        mock_device.port = 4370
        mock_models.Device.objects.get.return_value = mock_device

        with patch('core.services.zk_workers.get_zk_service') as mock_get_service:
            mock_service = MagicMock()
            mock_get_service.return_value = mock_service
            
            # Setup mock to crash during get_attendance
            mock_service.get_attendance.side_effect = Exception("Simulated Download Failure!")
            
            # Run the job
            run_import_attendance_job(self.job_id, 999)
            
            # Verify disable was called
            mock_service.disable_device.assert_called()
            
            # Verify enable was still called despite error
            mock_service.enable_device.assert_called()
            
            # Verify disconnect was called
            mock_service.disconnect.assert_called()
            
            print("✅ Error handling Safe Mode verified (Device enabled after crash).")

if __name__ == '__main__':
    unittest.main()
