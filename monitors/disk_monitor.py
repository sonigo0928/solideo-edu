# -*- coding: utf-8 -*-
"""
디스크 모니터링 모듈
"""

import psutil
import time
from typing import Dict, Any, List


class DiskMonitor:
    """디스크 리소스 모니터링 클래스"""
    
    def __init__(self):
        self._last_io = None
        self._last_time = None
    
    @staticmethod
    def bytes_to_gb(bytes_value: int) -> float:
        """바이트를 GB로 변환"""
        return round(bytes_value / (1024 ** 3), 2)
    
    @staticmethod
    def bytes_to_mb(bytes_value: float) -> float:
        """바이트를 MB로 변환"""
        return round(bytes_value / (1024 ** 2), 2)
    
    def get_partitions(self) -> List[Dict[str, Any]]:
        """디스크 파티션 정보 반환"""
        partitions = []
        
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_gb': self.bytes_to_gb(usage.total),
                    'used_gb': self.bytes_to_gb(usage.used),
                    'free_gb': self.bytes_to_gb(usage.free),
                    'percent': usage.percent,
                })
            except (PermissionError, OSError):
                continue
        
        return partitions
    
    def get_io_counters(self) -> Dict[str, Any]:
        """디스크 I/O 카운터 반환"""
        io = psutil.disk_io_counters()
        current_time = time.time()
        
        # 속도 계산
        read_speed = 0
        write_speed = 0
        
        if self._last_io and self._last_time:
            time_delta = current_time - self._last_time
            if time_delta > 0:
                read_speed = (io.read_bytes - self._last_io.read_bytes) / time_delta
                write_speed = (io.write_bytes - self._last_io.write_bytes) / time_delta
        
        self._last_io = io
        self._last_time = current_time
        
        return {
            'read_bytes': io.read_bytes,
            'write_bytes': io.write_bytes,
            'read_count': io.read_count,
            'write_count': io.write_count,
            'read_speed_mb': self.bytes_to_mb(read_speed),
            'write_speed_mb': self.bytes_to_mb(write_speed),
        }
    
    def get_all_data(self) -> Dict[str, Any]:
        """모든 디스크 데이터 반환"""
        partitions = self.get_partitions()
        io = self.get_io_counters()
        
        # 총 사용량 계산
        total_space = sum(p['total_gb'] for p in partitions)
        used_space = sum(p['used_gb'] for p in partitions)
        total_percent = (used_space / total_space * 100) if total_space > 0 else 0
        
        return {
            'partitions': partitions,
            'total_gb': round(total_space, 2),
            'used_gb': round(used_space, 2),
            'percent': round(total_percent, 1),
            'read_speed_mb': io['read_speed_mb'],
            'write_speed_mb': io['write_speed_mb'],
            'read_count': io['read_count'],
            'write_count': io['write_count'],
        }
