# -*- coding: utf-8 -*-
"""
PDF 보고서 생성 모듈
"""

import os
import base64
import logging
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Environment, FileSystemLoader
import plotly.graph_objects as go
import plotly.io as pio

from config import COLORS, REPORT_OUTPUT_DIR, REPORT_TEMPLATE_DIR

logger = logging.getLogger(__name__)


class PDFReportGenerator:
    """PDF 보고서 생성기"""
    
    def __init__(self):
        self.output_dir = REPORT_OUTPUT_DIR
        self.template_dir = REPORT_TEMPLATE_DIR
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
    
    def _create_line_chart_image(self, timestamps: List[str], data: List[float], 
                                  title: str, color: str, y_label: str = '') -> str:
        """라인 차트 이미지 생성 (base64)"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=data,
            mode='lines+markers',
            name=title,
            line=dict(color=color, width=2),
            fill='tozeroy',
            fillcolor=f'{color}33',
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=14)),
            xaxis_title='시간',
            yaxis_title=y_label,
            paper_bgcolor='white',
            plot_bgcolor='#f8f9fa',
            margin=dict(l=50, r=30, t=50, b=50),
            width=700,
            height=300,
            xaxis=dict(gridcolor='#dee2e6', showgrid=True),
            yaxis=dict(gridcolor='#dee2e6', showgrid=True),
        )
        
        # 이미지를 base64로 인코딩
        img_bytes = pio.to_image(fig, format='png', scale=2)
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        return f'data:image/png;base64,{img_base64}'
    
    def _create_bar_chart_image(self, labels: List[str], values: List[float], 
                                 title: str, color: str) -> str:
        """바 차트 이미지 생성 (base64)"""
        colors = [
            '#48bb78' if v < 70 else '#ed8936' if v < 90 else '#f56565'
            for v in values
        ]
        
        fig = go.Figure(go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=[f'{v:.1f}%' for v in values],
            textposition='outside',
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=14)),
            yaxis_title='사용률 (%)',
            paper_bgcolor='white',
            plot_bgcolor='#f8f9fa',
            margin=dict(l=50, r=30, t=50, b=50),
            width=700,
            height=300,
            yaxis=dict(range=[0, 110], gridcolor='#dee2e6'),
        )
        
        img_bytes = pio.to_image(fig, format='png', scale=2)
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        return f'data:image/png;base64,{img_base64}'
    
    def _create_dual_line_chart_image(self, timestamps: List[str], 
                                       data1: List[float], label1: str, color1: str,
                                       data2: List[float], label2: str, color2: str,
                                       title: str, y_label: str = '') -> str:
        """이중 라인 차트 이미지 생성"""
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=data1,
            mode='lines',
            name=label1,
            line=dict(color=color1, width=2),
        ))
        
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=data2,
            mode='lines',
            name=label2,
            line=dict(color=color2, width=2),
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=14)),
            xaxis_title='시간',
            yaxis_title=y_label,
            paper_bgcolor='white',
            plot_bgcolor='#f8f9fa',
            margin=dict(l=50, r=30, t=50, b=50),
            width=700,
            height=300,
            xaxis=dict(gridcolor='#dee2e6', showgrid=True),
            yaxis=dict(gridcolor='#dee2e6', showgrid=True),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        )
        
        img_bytes = pio.to_image(fig, format='png', scale=2)
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        
        return f'data:image/png;base64,{img_base64}'
    
    def generate_report(self, system_info: Dict[str, Any], statistics: Dict[str, Any],
                        time_series: Dict[str, List[Any]], timestamps: List[str]) -> str:
        """PDF 보고서 생성"""
        try:
            logger.info(f"PDF 보고서 생성 시작: {len(timestamps)} 데이터 포인트")

            # 타임스탐프 샘플링 (너무 많으면 줄이기)
            sample_rate = max(1, len(timestamps) // 60)
            sampled_timestamps = timestamps[::sample_rate]

            def sample_data(data):
                return data[::sample_rate] if data else []

            # 차트 이미지 생성
            logger.debug("CPU 차트 생성 중...")
            cpu_chart = self._create_line_chart_image(
                sampled_timestamps,
                sample_data(time_series.get('cpu_usage', [])),
                'CPU 사용률 추이', COLORS['cpu'], '사용률 (%)'
            )

            memory_chart = self._create_line_chart_image(
                sampled_timestamps,
                sample_data(time_series.get('memory_percent', [])),
                '메모리 사용률 추이', COLORS['memory'], '사용률 (%)'
            )

            network_chart = self._create_dual_line_chart_image(
                sampled_timestamps,
                sample_data(time_series.get('network_upload_speed', [])), '업로드', COLORS['network_up'],
                sample_data(time_series.get('network_download_speed', [])), '다운로드', COLORS['network_down'],
                '네트워크 트래픽', 'KB/s'
            )

            disk_io_chart = self._create_dual_line_chart_image(
                sampled_timestamps,
                sample_data(time_series.get('disk_read_speed', [])), '읽기', COLORS['info'],
                sample_data(time_series.get('disk_write_speed', [])), '쓰기', COLORS['warning'],
                '디스크 I/O', 'MB/s'
            )

            # 디스크 파티션 차트
            disk_partitions = system_info.get('disk', [])
            if disk_partitions:
                partition_labels = [p['mountpoint'] for p in disk_partitions]
                partition_values = [p['percent'] for p in disk_partitions]
                disk_partition_chart = self._create_bar_chart_image(
                    partition_labels, partition_values, '디스크 파티션별 사용량', COLORS['disk']
                )
            else:
                disk_partition_chart = None

            # GPU 차트 (데이터가 있는 경우)
            gpu_usage = time_series.get('gpu_usage', [])
            if gpu_usage and any(v > 0 for v in gpu_usage if v is not None):
                gpu_chart = self._create_line_chart_image(
                    sampled_timestamps,
                    sample_data(gpu_usage),
                    'GPU 사용률 추이', COLORS['gpu'], '사용률 (%)'
                )
            else:
                gpu_chart = None

            # 온도 차트
            cpu_temp = time_series.get('cpu_temperature', [])
            gpu_temp = time_series.get('gpu_temperature', [])
            if any(t is not None for t in cpu_temp) or any(t is not None for t in gpu_temp):
                # None 값을 0으로 대체
                cpu_temp_clean = [t if t is not None else 0 for t in sample_data(cpu_temp)]
                gpu_temp_clean = [t if t is not None else 0 for t in sample_data(gpu_temp)]

                temp_chart = self._create_dual_line_chart_image(
                    sampled_timestamps,
                    cpu_temp_clean, 'CPU', COLORS['cpu'],
                    gpu_temp_clean, 'GPU', COLORS['gpu'],
                    '시스템 온도 추이', '온도 (°C)'
                )
            else:
                temp_chart = None

            # 보고서 데이터 준비
            report_data = {
                'title': '시스템 리소스 모니터링 보고서',
                'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'monitoring_duration': '5분 (300초)',
                'data_points': len(timestamps),

                # 시스템 정보
                'cpu_info': system_info.get('cpu', {}),
                'gpu_info': system_info.get('gpu', []),
                'memory_info': system_info.get('memory', {}),
                'disk_info': system_info.get('disk', []),

                # 통계
                'statistics': statistics,

                # 차트 이미지
                'cpu_chart': cpu_chart,
                'memory_chart': memory_chart,
                'network_chart': network_chart,
                'disk_io_chart': disk_io_chart,
                'disk_partition_chart': disk_partition_chart,
                'gpu_chart': gpu_chart,
                'temp_chart': temp_chart,
            }

            # HTML 템플릿 렌더링
            env = Environment(loader=FileSystemLoader(self.template_dir))
            template = env.get_template('report_template.html')
            html_content = template.render(**report_data)

            # PDF 생성
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            pdf_filename = f'system_report_{timestamp}.pdf'
            pdf_path = os.path.join(self.output_dir, pdf_filename)

            try:
                from weasyprint import HTML
                logger.info(f"PDF 파일 생성 중: {pdf_filename}")
                HTML(string=html_content).write_pdf(pdf_path)
                logger.info(f"PDF 보고서 생성 완료: {pdf_path}")
            except ImportError:
                # WeasyPrint가 없으면 HTML로 저장
                logger.warning("WeasyPrint가 없어서 HTML 형식으로 저장합니다.")
                html_path = os.path.join(self.output_dir, f'system_report_{timestamp}.html')
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"HTML 보고서 생성 완료: {html_path}")
                return html_path

            return pdf_path

        except Exception as e:
            logger.error(f"보고서 생성 중 오류 발생: {e}", exc_info=True)
            raise
