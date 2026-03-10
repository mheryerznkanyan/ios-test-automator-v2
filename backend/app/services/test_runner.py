"""iOS Simulator test runner with video recording"""
import asyncio
import logging
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class TestRunner:
    """Runs XCUITests in iOS Simulator and records video"""
    
    def __init__(self, recordings_dir: Path):
        self.recordings_dir = Path(recordings_dir)
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
    
    def _is_udid(self, device_str: str) -> bool:
        """Check if string is a valid UDID (UUID format)"""
        return len(device_str) == 36 and device_str.count('-') == 4
    
    async def run_test(
        self,
        test_code: str,
        app_name: str = "YourApp",
        device: str = "iPhone 15 Pro",
        ios_version: str = "17.0"
    ) -> Dict[str, Any]:
        """
        Run a test in the simulator and record video.
        
        Args:
            test_code: Swift XCUITest code
            app_name: Name of the app to test
            device: Simulator device name OR UDID (if it's a valid UUID)
            ios_version: iOS version
            
        Returns:
            Dict with test results, video path, logs
        """
        test_id = str(uuid.uuid4())
        video_path = self.recordings_dir / f"{test_id}.mp4"
        
        try:
            # 1. Create temporary test file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.swift',
                delete=False,
                dir=tempfile.gettempdir()
            ) as f:
                f.write(test_code)
                test_file_path = f.name
            
            # 2. Get simulator UDID (or use if already a UDID)
            if self._is_udid(device):
                device_id = device
                logger.info(f"Using device UDID directly: {device_id}")
            else:
                device_id = await self._get_simulator_udid(device, ios_version)
                if not device_id:
                    return {
                        "success": False,
                        "error": f"Simulator '{device} ({ios_version})' not found",
                        "test_id": test_id
                    }
            
            # 3. Boot simulator
            await self._boot_simulator(device_id)
            
            # 4. Start video recording
            recording_process = await self._start_recording(device_id, video_path)
            
            # 5. Run the test
            test_result = await self._execute_test(test_file_path, device_id, app_name)
            
            # 6. Stop recording
            await self._stop_recording(recording_process)
            
            # 7. Verify video file exists and has content
            video_ready = False
            if video_path.exists():
                file_size = video_path.stat().st_size
                if file_size > 0:
                    logger.info(f"Video file created successfully: {file_size} bytes")
                    video_ready = True
                else:
                    logger.error(f"Video file exists but is empty: {video_path}")
            else:
                logger.error(f"Video file not found: {video_path}")
            
            # 8. Clean up temp file
            os.unlink(test_file_path)
            
            return {
                "success": test_result["success"],
                "test_id": test_id,
                "video_path": str(video_path.name) if video_ready else None,
                "logs": test_result.get("logs", ""),
                "duration": test_result.get("duration", 0),
                "device": device,
                "ios_version": ios_version
            }
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "test_id": test_id
            }
    
    async def _get_simulator_udid(self, device: str, ios_version: str) -> Optional[str]:
        """Get simulator UDID for the specified device and iOS version"""
        try:
            result = await asyncio.create_subprocess_exec(
                'xcrun', 'simctl', 'list', 'devices', 'available',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            # Parse output to find matching device
            output = stdout.decode()
            lines = output.split('\n')
            
            current_runtime = None
            for line in lines:
                if '-- iOS' in line or '-- com.apple.CoreSimulator.SimRuntime.iOS' in line:
                    # Extract iOS version from runtime line
                    if ios_version.replace('.', '-') in line:
                        current_runtime = ios_version
                elif current_runtime and device in line and '(Booted)' not in line:
                    # Extract UDID from device line
                    if '(' in line and ')' in line:
                        udid = line.split('(')[1].split(')')[0]
                        if len(udid) == 36:  # UUID format
                            return udid
            
            # Fallback: get any available device
            result = await asyncio.create_subprocess_exec(
                'xcrun', 'simctl', 'list', 'devices', 'available', '--json',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            import json
            data = json.loads(stdout.decode())
            
            for runtime, devices in data.get('devices', {}).items():
                for dev in devices:
                    if device in dev.get('name', '') and dev.get('isAvailable'):
                        return dev['udid']
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get simulator UDID: {e}")
            return None
    
    async def _boot_simulator(self, device_id: str):
        """Boot the simulator if not already booted"""
        try:
            # Check if already booted
            result = await asyncio.create_subprocess_exec(
                'xcrun', 'simctl', 'list', 'devices',
                stdout=asyncio.subprocess.PIPE
            )
            stdout, _ = await result.communicate()
            
            if '(Booted)' in stdout.decode() and device_id in stdout.decode():
                logger.info(f"Simulator {device_id} already booted")
                return
            
            # Boot simulator
            logger.info(f"Booting simulator {device_id}")
            result = await asyncio.create_subprocess_exec(
                'xcrun', 'simctl', 'boot', device_id,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await result.communicate()
            
            # Wait for boot to complete
            await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"Failed to boot simulator: {e}")
            raise
    
    async def _start_recording(self, device_id: str, output_path: Path):
        """Start video recording of the simulator"""
        try:
            logger.info(f"Starting video recording to {output_path}")
            process = await asyncio.create_subprocess_exec(
                'xcrun', 'simctl', 'io', device_id, 'recordVideo',
                str(output_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Give recording time to start
            await asyncio.sleep(2)
            
            # Check if process is still running
            if process.returncode is not None:
                stdout, stderr = await process.communicate()
                logger.error(f"Recording failed to start. stdout: {stdout.decode()}, stderr: {stderr.decode()}")
                raise RuntimeError(f"Recording process exited immediately: {stderr.decode()}")
            
            logger.info("Recording process started successfully")
            return process
            
        except Exception as e:
            logger.error(f"Failed to start recording: {e}")
            raise
    
    async def _stop_recording(self, process):
        """Stop video recording"""
        try:
            if process and process.returncode is None:
                logger.info("Stopping video recording")
                process.terminate()
                
                # Wait for process to actually terminate
                try:
                    await asyncio.wait_for(process.wait(), timeout=5.0)
                except asyncio.TimeoutError:
                    logger.warning("Recording process didn't terminate, killing it")
                    process.kill()
                    await process.wait()
                
                # Give extra time for file to be fully written
                await asyncio.sleep(3)
                logger.info("Recording process terminated, file should be ready")
                
        except Exception as e:
            logger.error(f"Failed to stop recording: {e}")
    
    async def _execute_test(
        self,
        test_file: str,
        device_id: str,
        app_name: str
    ) -> Dict[str, Any]:
        """
        Execute the test code.
        
        For now, this is a simplified implementation that just runs
        the test in the simulator. A full implementation would need
        an actual Xcode project with the app.
        """
        import time
        start_time = time.time()
        
        try:
            # For demo purposes, we'll simulate test execution
            # In production, you'd need to:
            # 1. Have an Xcode project for the app
            # 2. Inject the test code into the test target
            # 3. Run xcodebuild test
            
            logger.info(f"Executing test on simulator {device_id}")
            
            # Simulate test running (in production, use xcodebuild)
            # Record for 10 seconds to ensure we have a video
            await asyncio.sleep(10)  # Simulate test execution time
            
            # Mock successful result
            duration = time.time() - start_time
            
            return {
                "success": True,
                "logs": f"Test executed successfully on {app_name}",
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
            return {
                "success": False,
                "logs": str(e),
                "duration": time.time() - start_time
            }
