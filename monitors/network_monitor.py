# -*- coding: utf-8 -*-
"""
네트워크 모니터링 모듈
"""

import psutil
import time
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class NetworkMonitor:
    """네트워크 리소스 모니터링 클래스"""
    
    def __init__(self):
        self._last_io = None
        self._last_time = None
    
    @staticmethod
    def bytes_to_mb(bytes_value: float) -> float:
        """바이트를 MB로 변환"""
        return round(bytes_value / (1024 ** 2), 2)
    
    @staticmethod
    def bytes_to_kb(bytes_value: float) -> float:
        """바이트를 KB로 변환"""
        return round(bytes_value / 1024, 2)
    
    def get_interfaces(self) -> List[Dict[str, Any]]:
        """네트워크 인터페이스 정보 반환"""
        interfaces = []

        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()

            for name, addr_list in addrs.items():
                stat = stats.get(name)
                interface_info = {
                    'name': name,
                    'is_up': stat.isup if stat else False,
                    'speed': stat.speed if stat else 0,
                    'addresses': [],
                }

                for addr in addr_list:
                    if addr.family.name == 'AF_INET':
                        interface_info['addresses'].append({
                            'type': 'IPv4',
                            'address': addr.address,
                        })
                    elif addr.family.name == 'AF_INET6':
                        interface_info['addresses'].append({
                            'type': 'IPv6',
                            'address': addr.address,
                        })

                interfaces.append(interface_info)
        except Exception as e:
            logger.error(f"네트워크 인터페이스 정보를 가져올 수 없습니다: {e}")

        return interfaces
    
    def get_io_counters(self) -> Dict[str, Any]:
        """네트워크 I/O 카운터 반환"""
        try:
            io = psutil.net_io_counters()
            current_time = time.time()

            # 속도 계산
            upload_speed = 0
            download_speed = 0

            if self._last_io and self._last_time:
                time_delta = current_time - self._last_time
                if time_delta > 0:
                    upload_speed = (io.bytes_sent - self._last_io.bytes_sent) / time_delta
                    download_speed = (io.bytes_recv - self._last_io.bytes_recv) / time_delta

            self._last_io = io
            self._last_time = current_time

            return {
                'bytes_sent': io.bytes_sent,
                'bytes_recv': io.bytes_recv,
                'packets_sent': io.packets_sent,
                'packets_recv': io.packets_recv,
                'errors_in': io.errin,
                'errors_out': io.errout,
                'drops_in': io.dropin,
                'drops_out': io.dropout,
                'upload_speed_kb': self.bytes_to_kb(upload_speed),
                'download_speed_kb': self.bytes_to_kb(download_speed),
                'upload_speed_mb': self.bytes_to_mb(upload_speed),
                'download_speed_mb': self.bytes_to_mb(download_speed),
            }
        except Exception as e:
            logger.error(f"네트워크 I/O 정보를 가져올 수 없습니다: {e}")
            return {
                'bytes_sent': 0,
                'bytes_recv': 0,
                'packets_sent': 0,
                'packets_recv': 0,
                'errors_in': 0,
                'errors_out': 0,
                'drops_in': 0,
                'drops_out': 0,
                'upload_speed_kb': 0,
                'download_speed_kb': 0,
                'upload_speed_mb': 0,
                'download_speed_mb': 0,
            }
    
    def get_connections_count(self) -> Dict[str, int]:
        """네트워크 연결 수 반환"""
        try:
            connections = psutil.net_connections()
            status_count = {}

            for conn in connections:
                status = conn.status
                status_count[status] = status_count.get(status, 0) + 1

            return {
                'total': len(connections),
                'by_status': status_count,
            }
        except (PermissionError, psutil.AccessDenied) as e:
            logger.warning(f"네트워크 연결 정보에 접근할 수 없습니다 (권한 부족): {e}")
            return {'total': 0, 'by_status': {}}
        except Exception as e:
            logger.error(f"네트워크 연결 정보를 가져올 수 없습니다: {e}")
            return {'total': 0, 'by_status': {}}
    
    def get_all_data(self) -> Dict[str, Any]:
        """모든 네트워크 데이터 반환"""
        io = self.get_io_counters()
        
        return {
            'bytes_sent': io['bytes_sent'],
            'bytes_recv': io['bytes_recv'],
            'upload_speed_kb': io['upload_speed_kb'],
            'download_speed_kb': io['download_speed_kb'],
            'upload_speed_mb': io['upload_speed_mb'],
            'download_speed_mb': io['download_speed_mb'],
            'packets_sent': io['packets_sent'],
            'packets_recv': io['packets_recv'],
            'errors_in': io['errors_in'],
            'errors_out': io['errors_out'],
        }
