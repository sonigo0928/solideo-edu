# -*- coding: utf-8 -*-
"""
메모리 모니터링 모듈
"""

import psutil
from typing import Dict, Any


class MemoryMonitor:
    """메모리 리소스 모니터링 클래스"""
    
    @staticmethod
    def bytes_to_gb(bytes_value: int) -> float:
        """바이트를 GB로 변환"""
        return round(bytes_value / (1024 ** 3), 2)
    
    def get_memory_info(self) -> Dict[str, Any]:
        """메모리 정보 반환"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            # RAM 정보
            'ram_total': self.bytes_to_gb(mem.total),
            'ram_available': self.bytes_to_gb(mem.available),
            'ram_used': self.bytes_to_gb(mem.used),
            'ram_percent': mem.percent,
            'ram_free': self.bytes_to_gb(mem.free),
            
            # Swap/페이지 파일 정보
            'swap_total': self.bytes_to_gb(swap.total),
            'swap_used': self.bytes_to_gb(swap.used),
            'swap_free': self.bytes_to_gb(swap.free),
            'swap_percent': swap.percent,
        }
    
    def get_all_data(self) -> Dict[str, Any]:
        """모든 메모리 데이터 반환"""
        info = self.get_memory_info()
        
        return {
            'total_gb': info['ram_total'],
            'used_gb': info['ram_used'],
            'available_gb': info['ram_available'],
            'percent': info['ram_percent'],
            'swap_total_gb': info['swap_total'],
            'swap_used_gb': info['swap_used'],
            'swap_percent': info['swap_percent'],
        }
