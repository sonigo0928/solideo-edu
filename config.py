# -*- coding: utf-8 -*-
"""
설정 파일 - 시스템 리소스 모니터링 시스템
"""

import os
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# 모니터링 설정 (환경변수로 오버라이드 가능)
MONITORING_INTERVAL_MS = int(os.getenv('MONITORING_INTERVAL_MS', 1000))
MONITORING_DURATION_SECONDS = int(os.getenv('MONITORING_DURATION_SECONDS', 300))
MAX_DATA_POINTS = int(os.getenv('MAX_DATA_POINTS', 300))

# 서버 설정 (환경변수로 오버라이드 가능)
HOST = os.getenv('HOST', '127.0.0.1')
PORT = int(os.getenv('PORT', 8050))
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# PDF 보고서 설정
REPORT_OUTPUT_DIR = "output"
REPORT_TEMPLATE_DIR = "reports/templates"

# 차트 색상 테마
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#48bb78',
    'warning': '#ed8936',
    'danger': '#f56565',
    'info': '#4299e1',
    'dark': '#1a202c',
    'light': '#f7fafc',
    'background': '#0f0f23',
    'card_bg': 'rgba(30, 30, 60, 0.8)',
    'text': '#e2e8f0',
    'cpu': '#667eea',
    'gpu': '#48bb78',
    'memory': '#ed8936',
    'disk': '#f56565',
    'network_up': '#4299e1',
    'network_down': '#9f7aea',
}

# 게이지 차트 색상 범위
GAUGE_STEPS = [
    {'range': [0, 30], 'color': '#48bb78'},    # 녹색 (안전)
    {'range': [30, 70], 'color': '#ed8936'},   # 주황 (보통)
    {'range': [70, 100], 'color': '#f56565'},  # 빨강 (위험)
]
