# -*- coding: utf-8 -*-
"""
GPU 모니터링 모듈
"""

import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class GPUMonitor:
    """GPU 리소스 모니터링 클래스"""
    
    def __init__(self):
        self._gputil_available = False
        self._init_gputil()
    
    def _init_gputil(self):
        """GPUtil 초기화"""
        try:
            import GPUtil
            self._gputil_available = True
            logger.info("GPUtil을 통한 GPU 모니터링 활성화")
        except ImportError:
            logger.warning("GPUtil이 설치되어 있지 않습니다. GPU 모니터링이 비활성화됩니다.")
            self._gputil_available = False
    
    def get_gpu_info(self) -> List[Dict[str, Any]]:
        """GPU 기본 정보 반환"""
        if not self._gputil_available:
            return []

        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            return [
                {
                    'id': gpu.id,
                    'name': gpu.name,
                    'driver': gpu.driver,
                    'memory_total': gpu.memoryTotal,
                }
                for gpu in gpus
            ]
        except Exception as e:
            logger.error(f"GPU 정보를 가져올 수 없습니다: {e}")
            return []
    
    def get_gpu_usage(self) -> List[Dict[str, Any]]:
        """GPU 사용량 반환"""
        if not self._gputil_available:
            return []

        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            return [
                {
                    'id': gpu.id,
                    'name': gpu.name,
                    'load_percent': gpu.load * 100,
                    'memory_used': gpu.memoryUsed,
                    'memory_total': gpu.memoryTotal,
                    'memory_percent': (gpu.memoryUsed / gpu.memoryTotal * 100) if gpu.memoryTotal > 0 else 0,
                    'temperature': gpu.temperature,
                }
                for gpu in gpus
            ]
        except Exception as e:
            logger.error(f"GPU 사용량을 가져올 수 없습니다: {e}")
            return []
    
    def get_primary_gpu_data(self) -> Dict[str, Any]:
        """주 GPU 데이터 반환"""
        gpus = self.get_gpu_usage()
        
        if gpus:
            gpu = gpus[0]
            return {
                'available': True,
                'name': gpu['name'],
                'usage_percent': gpu['load_percent'],
                'memory_used': gpu['memory_used'],
                'memory_total': gpu['memory_total'],
                'memory_percent': gpu['memory_percent'],
                'temperature': gpu['temperature'],
            }
        
        return {
            'available': False,
            'name': 'N/A',
            'usage_percent': 0,
            'memory_used': 0,
            'memory_total': 0,
            'memory_percent': 0,
            'temperature': None,
        }
    
    def get_all_data(self) -> Dict[str, Any]:
        """모든 GPU 데이터 반환"""
        return self.get_primary_gpu_data()
