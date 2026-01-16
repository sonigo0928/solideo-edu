# -*- coding: utf-8 -*-
"""
시계열 데이터 저장 및 관리 모듈
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import deque
import statistics
import threading
import logging

logger = logging.getLogger(__name__)


class DataStore:
    """시계열 데이터 저장소"""
    
    def __init__(self, max_points: int = 300):
        self.max_points = max_points
        self._data = {
            'timestamps': deque(maxlen=max_points),
            'cpu_usage': deque(maxlen=max_points),
            'cpu_temperature': deque(maxlen=max_points),
            'gpu_usage': deque(maxlen=max_points),
            'gpu_temperature': deque(maxlen=max_points),
            'gpu_memory_percent': deque(maxlen=max_points),
            'memory_percent': deque(maxlen=max_points),
            'memory_used_gb': deque(maxlen=max_points),
            'disk_percent': deque(maxlen=max_points),
            'disk_read_speed': deque(maxlen=max_points),
            'disk_write_speed': deque(maxlen=max_points),
            'network_upload_speed': deque(maxlen=max_points),
            'network_download_speed': deque(maxlen=max_points),
        }
        self._lock = threading.Lock()
        self._monitoring_active = False
        self._monitoring_start_time = None
    
    def add_data_point(self, data: Dict[str, Any]):
        """데이터 포인트 추가"""
        with self._lock:
            timestamp = datetime.now()
            self._data['timestamps'].append(timestamp)
            
            # CPU 데이터
            self._data['cpu_usage'].append(data.get('cpu_usage', 0))
            self._data['cpu_temperature'].append(data.get('cpu_temperature'))
            
            # GPU 데이터
            self._data['gpu_usage'].append(data.get('gpu_usage', 0))
            self._data['gpu_temperature'].append(data.get('gpu_temperature'))
            self._data['gpu_memory_percent'].append(data.get('gpu_memory_percent', 0))
            
            # 메모리 데이터
            self._data['memory_percent'].append(data.get('memory_percent', 0))
            self._data['memory_used_gb'].append(data.get('memory_used_gb', 0))
            
            # 디스크 데이터
            self._data['disk_percent'].append(data.get('disk_percent', 0))
            self._data['disk_read_speed'].append(data.get('disk_read_speed', 0))
            self._data['disk_write_speed'].append(data.get('disk_write_speed', 0))
            
            # 네트워크 데이터
            self._data['network_upload_speed'].append(data.get('network_upload_speed', 0))
            self._data['network_download_speed'].append(data.get('network_download_speed', 0))
    
    def get_data(self, key: str) -> List[Any]:
        """특정 키의 데이터 반환"""
        with self._lock:
            return list(self._data.get(key, []))
    
    def get_all_data(self) -> Dict[str, List[Any]]:
        """모든 데이터 반환"""
        with self._lock:
            return {key: list(values) for key, values in self._data.items()}
    
    def get_timestamps_str(self) -> List[str]:
        """타임스탬프를 문자열 리스트로 반환"""
        with self._lock:
            return [ts.strftime('%H:%M:%S') for ts in self._data['timestamps']]
    
    def get_statistics(self, key: str) -> Dict[str, Optional[float]]:
        """특정 키의 통계 반환"""
        try:
            data = self.get_data(key)
            # None 값 필터링
            valid_data = [x for x in data if x is not None]

            if not valid_data:
                return {
                    'min': None,
                    'max': None,
                    'mean': None,
                    'stdev': None,
                    'count': 0,
                }

            return {
                'min': round(min(valid_data), 2),
                'max': round(max(valid_data), 2),
                'mean': round(statistics.mean(valid_data), 2),
                'stdev': round(statistics.stdev(valid_data), 2) if len(valid_data) > 1 else 0,
                'count': len(valid_data),
            }
        except Exception as e:
            logger.error(f"통계 계산 오류 (키: {key}): {e}")
            return {
                'min': None,
                'max': None,
                'mean': None,
                'stdev': None,
                'count': 0,
            }
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Optional[float]]]:
        """모든 키의 통계 반환"""
        result = {}
        for key in self._data.keys():
            if key != 'timestamps':
                result[key] = self.get_statistics(key)
        return result
    
    def clear(self):
        """모든 데이터 클리어"""
        with self._lock:
            for key in self._data:
                self._data[key].clear()
    
    def start_monitoring(self):
        """모니터링 시작"""
        self.clear()
        self._monitoring_active = True
        self._monitoring_start_time = datetime.now()
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self._monitoring_active = False
    
    def is_monitoring_active(self) -> bool:
        """모니터링 활성 상태 반환"""
        return self._monitoring_active
    
    def get_monitoring_elapsed_seconds(self) -> int:
        """모니터링 경과 시간(초) 반환"""
        if self._monitoring_start_time and self._monitoring_active:
            elapsed = datetime.now() - self._monitoring_start_time
            return int(elapsed.total_seconds())
        return 0
    
    def get_data_count(self) -> int:
        """저장된 데이터 포인트 수 반환"""
        with self._lock:
            return len(self._data['timestamps'])


# 전역 데이터 저장소 인스턴스
data_store = DataStore()
