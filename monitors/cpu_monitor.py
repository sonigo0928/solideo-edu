# -*- coding: utf-8 -*-
"""
CPU 모니터링 모듈
"""

import psutil
import platform
from typing import Dict, Any, List, Optional


class CPUMonitor:
    """CPU 리소스 모니터링 클래스"""
    
    def __init__(self):
        self._wmi = None
        self._init_wmi()
    
    def _init_wmi(self):
        """WMI 초기화 (Windows 온도 모니터링용)"""
        try:
            import wmi
            self._wmi = wmi.WMI(namespace="root\\wmi")
        except Exception:
            self._wmi = None
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """CPU 기본 정보 반환"""
        return {
            'name': platform.processor(),
            'physical_cores': psutil.cpu_count(logical=False),
            'logical_cores': psutil.cpu_count(logical=True),
            'architecture': platform.machine(),
        }
    
    def get_cpu_usage(self) -> Dict[str, Any]:
        """CPU 사용량 반환"""
        # 전체 CPU 사용률
        total_percent = psutil.cpu_percent(interval=None)
        
        # 코어별 사용률
        per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)
        
        # CPU 주파수
        freq = psutil.cpu_freq()
        freq_current = freq.current if freq else 0
        freq_max = freq.max if freq else 0
        freq_min = freq.min if freq else 0
        
        return {
            'total_percent': total_percent,
            'per_cpu_percent': per_cpu_percent,
            'frequency_current': freq_current,
            'frequency_max': freq_max,
            'frequency_min': freq_min,
        }
    
    def get_cpu_temperature(self) -> Optional[float]:
        """CPU 온도 반환 (Windows)"""
        # Windows에서 WMI를 통한 온도 가져오기 시도
        if self._wmi:
            try:
                temperature_info = self._wmi.MSAcpi_ThermalZoneTemperature()
                if temperature_info:
                    # Kelvin에서 Celsius로 변환
                    temp_kelvin = temperature_info[0].CurrentTemperature / 10.0
                    temp_celsius = temp_kelvin - 273.15
                    return round(temp_celsius, 1)
            except Exception:
                pass
        
        # psutil sensors_temperatures 시도 (Linux 주로 작동)
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        if 'cpu' in name.lower() or 'core' in entry.label.lower():
                            return entry.current
        except Exception:
            pass
        
        return None
    
    def get_all_data(self) -> Dict[str, Any]:
        """모든 CPU 데이터 반환"""
        usage = self.get_cpu_usage()
        temperature = self.get_cpu_temperature()
        
        return {
            'usage_percent': usage['total_percent'],
            'per_cpu_percent': usage['per_cpu_percent'],
            'frequency_current': usage['frequency_current'],
            'frequency_max': usage['frequency_max'],
            'temperature': temperature,
        }
