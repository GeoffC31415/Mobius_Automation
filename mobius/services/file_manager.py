"""
File Manager Module
Handles video file management and cleanup
"""

import os
import glob
import time
import logging
from datetime import datetime, timedelta
from typing import List, Set, Tuple, Optional

from mobius.config import settings


class FileManager:
    """Manages video files for the vivarium"""
    
    def __init__(self):
        """Initialize the file manager"""
        self.logger = logging.getLogger('mobius.services.file_manager')
        self.source_path = settings.DATA_DIR
        self.max_age_days = settings.VIDEO_MAX_AGE_DAYS
        
    def get_mp4s(self) -> Set[str]:
        """Get all MP4 files in the source directory
        
        Returns:
            set: Set of full file paths
        """
        try:
            return set(glob.glob(os.path.join(self.source_path, '*.mp4')))
        except Exception as e:
            self.logger.error(f"Error getting MP4 files: {e}")
            return set()
            
    def get_total_size(self, start_date: datetime, end_date: datetime) -> float:
        """Get total size of files modified between start and end dates
        
        Args:
            start_date: Start datetime
            end_date: End datetime
            
        Returns:
            float: Total size in bytes
        """
        try:
            file_list = self.get_mp4s()
            total_size = 0
            
            for file_path in file_list:
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                if start_date <= file_date <= end_date:
                    total_size += os.path.getsize(file_path)
                    
            return total_size
        except Exception as e:
            self.logger.error(f"Error calculating total size: {e}")
            return 0
            
    def clean_videos(self, min_hour: int, max_hour: int, max_size: float) -> None:
        """Clean up video files based on specified criteria
        
        Args:
            min_hour: Minimum hour for daytime videos (e.g., 6 for 6 AM)
            max_hour: Maximum hour for daytime videos (e.g., 20 for 8 PM)
            max_size: Maximum file size to keep (bytes)
        """
        try:
            remaining_files = self.get_mp4s()
            total_file_count = len(remaining_files)
            
            self.logger.info(f"Checking {total_file_count} videos for cleanup")
            
            # Define filter functions
            filter_functions = [
                {
                    'function': self._filter_by_time,
                    'condition': (min_hour, max_hour),
                    'desc': 'Removing {} during day, {} KB'
                },
                {
                    'function': self._filter_by_size,
                    'condition': (max_size,),
                    'desc': 'Removing {} below size limit, {} KB'
                },
                {
                    'function': self._filter_by_age,
                    'condition': (timedelta(days=self.max_age_days),),
                    'desc': 'Removing {} old files, {} KB'
                }
            ]
            
            log_message = ''
            files_to_remove = []
            
            # Apply each filter
            for filter_obj in filter_functions:
                filtered_files, size_kb = filter_obj['function'](
                    remaining_files, 
                    *filter_obj['condition']
                )
                
                if filtered_files:
                    log_message += f"\n{filter_obj['desc'].format(len(filtered_files), size_kb)}"
                    files_to_remove.extend(filtered_files)
                    remaining_files -= set(filtered_files)
            
            # Log results
            self.logger.info(f"Checked {total_file_count} videos{log_message}")
            
            # Remove files
            self._remove_files(files_to_remove)
            
        except Exception as e:
            self.logger.error(f"Error cleaning videos: {e}", exc_info=True)
            
    def _filter_by_time(self, file_list: Set[str], min_hour: int, max_hour: int) -> Tuple[List[str], float]:
        """Filter files by time of day they were created
        
        Args:
            file_list: Set of file paths
            min_hour: Minimum hour (inclusive)
            max_hour: Maximum hour (exclusive)
            
        Returns:
            tuple: (list of matching files, total size in KB)
        """
        in_time = []
        total_size = 0
        
        for file_path in file_list:
            try:
                # Extract hour from filename (format: xx-YYYYMMDDHHMMSS.mp4)
                # Or use file creation time as fallback
                try:
                    file_name = os.path.basename(file_path)
                    hour = int(file_name[-10:-8])
                except (ValueError, IndexError):
                    # Fallback to file modification time
                    file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                    hour = file_date.hour
                    
                if min_hour <= hour < max_hour:
                    in_time.append(file_path)
                    total_size += os.path.getsize(file_path)
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {e}")
                
        return in_time, total_size / 1024
        
    def _filter_by_size(self, file_list: Set[str], max_size: float) -> Tuple[List[str], float]:
        """Filter files smaller than max_size
        
        Args:
            file_list: Set of file paths
            max_size: Maximum size in bytes
            
        Returns:
            tuple: (list of matching files, total size in KB)
        """
        in_size = []
        total_size = 0
        
        for file_path in file_list:
            try:
                size = os.path.getsize(file_path)
                if size < max_size:
                    in_size.append(file_path)
                    total_size += size
            except Exception as e:
                self.logger.error(f"Error getting size for {file_path}: {e}")
                
        return in_size, total_size / 1024
        
    def _filter_by_age(self, file_list: Set[str], age_limit: timedelta) -> Tuple[List[str], float]:
        """Filter files older than age_limit
        
        Args:
            file_list: Set of file paths
            age_limit: Age limit as timedelta
            
        Returns:
            tuple: (list of matching files, total size in KB)
        """
        old_files = []
        total_size = 0
        
        for file_path in file_list:
            try:
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                if file_date < (datetime.now() - age_limit):
                    old_files.append(file_path)
                    total_size += os.path.getsize(file_path)
            except Exception as e:
                self.logger.error(f"Error checking age for {file_path}: {e}")
                
        return old_files, total_size / 1024
        
    def _remove_files(self, file_list: List[str]) -> None:
        """Remove files from the filesystem
        
        Args:
            file_list: List of file paths to remove
        """
        count = 0
        for file_path in file_list:
            try:
                os.remove(file_path)
                count += 1
            except Exception as e:
                self.logger.error(f"Could not remove file {file_path}: {e}")
                
        self.logger.info(f"Removed {count} files") 