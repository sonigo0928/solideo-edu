# -*- coding: utf-8 -*-
"""
대시보드 콜백 모듈 - 실시간 업데이트 로직
"""

from dash import callback, Output, Input, State, no_update, ctx
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
from datetime import datetime
import os

from config import COLORS, GAUGE_STEPS, MONITORING_DURATION_SECONDS, REPORT_OUTPUT_DIR
from monitors import CPUMonitor, GPUMonitor, MemoryMonitor, DiskMonitor, NetworkMonitor
from data.data_store import data_store
from reports.generator import PDFReportGenerator

# 모니터 인스턴스 생성
cpu_monitor = CPUMonitor()
gpu_monitor = GPUMonitor()
memory_monitor = MemoryMonitor()
disk_monitor = DiskMonitor()
network_monitor = NetworkMonitor()


def create_gauge_figure(value: float, title: str = '') -> go.Figure:
    """게이지 차트 생성"""
    fig = go.Figure(go.Indicator(
        mode='gauge+number',
        value=value,
        number={'suffix': '%', 'font': {'size': 36, 'color': COLORS['text']}},
        gauge={
            'axis': {
                'range': [0, 100],
                'tickwidth': 1,
                'tickcolor': COLORS['text'],
                'tickfont': {'color': COLORS['text']},
            },
            'bar': {'color': COLORS['primary']},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 0,
            'steps': GAUGE_STEPS,
            'threshold': {
                'line': {'color': COLORS['danger'], 'width': 2},
                'thickness': 0.75,
                'value': 90,
            },
        },
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': COLORS['text']},
        margin=dict(l=20, r=20, t=30, b=10),
        height=180,
    )
    
    return fig


def create_line_chart(x_data: list, y_data: list, name: str, color: str, 
                      y_data2: list = None, name2: str = None, color2: str = None) -> go.Figure:
    """라인 차트 생성"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='lines',
        name=name,
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f'{color}22',
    ))
    
    if y_data2 is not None:
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data2,
            mode='lines',
            name=name2,
            line=dict(color=color2, width=2),
            fill='tozeroy',
            fillcolor=f'{color2}22',
        ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': COLORS['text']},
        margin=dict(l=40, r=20, t=10, b=40),
        xaxis=dict(
            gridcolor=f'{COLORS["text"]}22',
            showgrid=True,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=f'{COLORS["text"]}22',
            showgrid=True,
            zeroline=False,
            range=[0, 100] if 'percent' in name.lower() or '사용률' in name else None,
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
        ),
        showlegend=y_data2 is not None,
    )
    
    return fig


def create_bar_chart(labels: list, values: list, colors: list = None) -> go.Figure:
    """바 차트 생성"""
    if colors is None:
        colors = [COLORS['primary']] * len(labels)
    
    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=[f'{v:.1f}%' for v in values],
        textposition='outside',
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': COLORS['text']},
        margin=dict(l=40, r=20, t=10, b=60),
        xaxis=dict(
            gridcolor=f'{COLORS["text"]}22',
            showgrid=False,
        ),
        yaxis=dict(
            gridcolor=f'{COLORS["text"]}22',
            showgrid=True,
            range=[0, 100],
        ),
    )
    
    return fig


def register_callbacks(app):
    """콜백 등록"""
    
    @app.callback(
        [
            Output('monitoring-state', 'data'),
            Output('start-monitoring-btn', 'children'),
            Output('start-monitoring-btn', 'disabled'),
            Output('generate-pdf-btn', 'disabled'),
            Output('alert-container', 'children'),
        ],
        [
            Input('start-monitoring-btn', 'n_clicks'),
            Input('interval-component', 'n_intervals'),
        ],
        [State('monitoring-state', 'data')],
        prevent_initial_call=True,
    )
    def handle_monitoring_control(n_clicks, n_intervals, state):
        """모니터링 제어 및 상태 업데이트"""
        from dash import html
        import dash_bootstrap_components as dbc
        
        triggered_id = ctx.triggered_id
        alert = None
        
        if triggered_id == 'start-monitoring-btn' and n_clicks:
            # 모니터링 시작
            data_store.start_monitoring()
            state = {'active': True, 'elapsed': 0}
            btn_content = [html.Span('⏹️', style={'marginRight': '8px'}), '모니터링 중...']
            alert = dbc.Alert(
                [html.Span('✅', style={'marginRight': '10px'}), '5분 모니터링을 시작합니다.'],
                color='success',
                dismissable=True,
                duration=3000,
            )
            return state, btn_content, True, True, alert
        
        elif triggered_id == 'interval-component' and state.get('active'):
            elapsed = data_store.get_monitoring_elapsed_seconds()
            state['elapsed'] = elapsed
            
            if elapsed >= MONITORING_DURATION_SECONDS:
                # 모니터링 완료
                data_store.stop_monitoring()
                state['active'] = False
                btn_content = [html.Span('▶️', style={'marginRight': '8px'}), '5분 모니터링 시작']
                alert = dbc.Alert(
                    [html.Span('🎉', style={'marginRight': '10px'}), '모니터링이 완료되었습니다! PDF 보고서를 생성할 수 있습니다.'],
                    color='info',
                    dismissable=True,
                    duration=5000,
                )
                return state, btn_content, False, False, alert
            
            return state, no_update, no_update, no_update, None
        
        return state, no_update, no_update, no_update, None
    
    @app.callback(
        Output('timer-display', 'children'),
        Input('interval-component', 'n_intervals'),
        State('monitoring-state', 'data'),
    )
    def update_timer(n_intervals, state):
        """타이머 업데이트"""
        if state and state.get('active'):
            elapsed = data_store.get_monitoring_elapsed_seconds()
            minutes = elapsed // 60
            seconds = elapsed % 60
            return f'{minutes:02d}:{seconds:02d}'
        return '00:00'
    
    @app.callback(
        [
            Output('download-pdf', 'data'),
            Output('alert-container', 'children', allow_duplicate=True),
        ],
        Input('generate-pdf-btn', 'n_clicks'),
        prevent_initial_call=True,
    )
    def generate_pdf_report(n_clicks):
        """PDF 보고서 생성"""
        from dash import html
        import dash_bootstrap_components as dbc
        
        if not n_clicks:
            raise PreventUpdate
        
        try:
            # PDF 생성
            generator = PDFReportGenerator()
            
            # 시스템 정보 수집
            system_info = {
                'cpu': cpu_monitor.get_cpu_info(),
                'gpu': gpu_monitor.get_gpu_info(),
                'memory': memory_monitor.get_memory_info(),
                'disk': disk_monitor.get_partitions(),
            }
            
            # 통계 데이터
            statistics = data_store.get_all_statistics()
            
            # 시계열 데이터
            time_series = data_store.get_all_data()
            timestamps = data_store.get_timestamps_str()
            
            # PDF 생성
            pdf_path = generator.generate_report(
                system_info=system_info,
                statistics=statistics,
                time_series=time_series,
                timestamps=timestamps,
            )
            
            alert = dbc.Alert(
                [html.Span('✅', style={'marginRight': '10px'}), f'PDF 보고서가 생성되었습니다: {pdf_path}'],
                color='success',
                dismissable=True,
                duration=5000,
            )
            
            return dict(content=open(pdf_path, 'rb').read(), filename=os.path.basename(pdf_path), type='application/pdf'), alert
            
        except Exception as e:
            alert = dbc.Alert(
                [html.Span('❌', style={'marginRight': '10px'}), f'PDF 생성 실패: {str(e)}'],
                color='danger',
                dismissable=True,
            )
            return no_update, alert
    
    @app.callback(
        [
            # 게이지 차트
            Output('cpu-gauge', 'figure'),
            Output('gpu-gauge', 'figure'),
            Output('memory-gauge', 'figure'),
            # 게이지 정보
            Output('cpu-info', 'children'),
            Output('gpu-info', 'children'),
            Output('memory-info', 'children'),
            # 온도/상태 표시
            Output('cpu-temp-value', 'children'),
            Output('gpu-temp-value', 'children'),
            Output('memory-total-value', 'children'),
            Output('disk-total-value', 'children'),
            # 히스토리 차트
            Output('cpu-history-chart', 'figure'),
            Output('memory-history-chart', 'figure'),
            Output('network-chart', 'figure'),
            Output('disk-io-chart', 'figure'),
            Output('disk-partitions-chart', 'figure'),
            # 상태 텍스트
            Output('status-text', 'children'),
        ],
        Input('interval-component', 'n_intervals'),
    )
    def update_dashboard(n_intervals):
        """대시보드 전체 업데이트"""
        # 데이터 수집
        cpu_data = cpu_monitor.get_all_data()
        gpu_data = gpu_monitor.get_all_data()
        memory_data = memory_monitor.get_all_data()
        disk_data = disk_monitor.get_all_data()
        network_data = network_monitor.get_all_data()
        
        # 데이터 저장 (모니터링 활성 시)
        if data_store.is_monitoring_active():
            data_store.add_data_point({
                'cpu_usage': cpu_data['usage_percent'],
                'cpu_temperature': cpu_data['temperature'],
                'gpu_usage': gpu_data['usage_percent'],
                'gpu_temperature': gpu_data['temperature'],
                'gpu_memory_percent': gpu_data['memory_percent'],
                'memory_percent': memory_data['percent'],
                'memory_used_gb': memory_data['used_gb'],
                'disk_percent': disk_data['percent'],
                'disk_read_speed': disk_data['read_speed_mb'],
                'disk_write_speed': disk_data['write_speed_mb'],
                'network_upload_speed': network_data['upload_speed_kb'],
                'network_download_speed': network_data['download_speed_kb'],
            })
        
        # 게이지 차트 생성
        cpu_gauge = create_gauge_figure(cpu_data['usage_percent'])
        gpu_gauge = create_gauge_figure(gpu_data['usage_percent'])
        memory_gauge = create_gauge_figure(memory_data['percent'])
        
        # 게이지 정보 텍스트
        cpu_freq = f"{cpu_data['frequency_current']:.0f} MHz" if cpu_data['frequency_current'] else 'N/A'
        gpu_mem = f"{gpu_data['memory_used']:.0f}/{gpu_data['memory_total']:.0f} MB" if gpu_data['available'] else 'N/A'
        mem_usage = f"{memory_data['used_gb']:.1f}/{memory_data['total_gb']:.1f} GB"
        
        # 온도/상태 표시
        cpu_temp = f"{cpu_data['temperature']:.1f}°C" if cpu_data['temperature'] else 'N/A'
        gpu_temp = f"{gpu_data['temperature']:.1f}°C" if gpu_data['temperature'] else 'N/A'
        mem_total = f"{memory_data['percent']:.1f}%"
        disk_total = f"{disk_data['percent']:.1f}%"
        
        # 히스토리 데이터
        timestamps = data_store.get_timestamps_str()
        if not timestamps:
            timestamps = [datetime.now().strftime('%H:%M:%S')]
        
        cpu_history = data_store.get_data('cpu_usage') or [cpu_data['usage_percent']]
        memory_history = data_store.get_data('memory_percent') or [memory_data['percent']]
        upload_history = data_store.get_data('network_upload_speed') or [network_data['upload_speed_kb']]
        download_history = data_store.get_data('network_download_speed') or [network_data['download_speed_kb']]
        read_history = data_store.get_data('disk_read_speed') or [disk_data['read_speed_mb']]
        write_history = data_store.get_data('disk_write_speed') or [disk_data['write_speed_mb']]
        
        # 라인 차트 생성
        cpu_history_chart = create_line_chart(
            timestamps, cpu_history, 'CPU 사용률 (%)', COLORS['cpu']
        )
        memory_history_chart = create_line_chart(
            timestamps, memory_history, '메모리 사용률 (%)', COLORS['memory']
        )
        network_chart = create_line_chart(
            timestamps, upload_history, '업로드 (KB/s)', COLORS['network_up'],
            download_history, '다운로드 (KB/s)', COLORS['network_down']
        )
        disk_io_chart = create_line_chart(
            timestamps, read_history, '읽기 (MB/s)', COLORS['info'],
            write_history, '쓰기 (MB/s)', COLORS['warning']
        )
        
        # 디스크 파티션 바 차트
        partitions = disk_data['partitions']
        partition_labels = [p['mountpoint'] for p in partitions]
        partition_values = [p['percent'] for p in partitions]
        partition_colors = [
            COLORS['success'] if v < 70 else COLORS['warning'] if v < 90 else COLORS['danger']
            for v in partition_values
        ]
        disk_partitions_chart = create_bar_chart(partition_labels, partition_values, partition_colors)
        
        # 상태 텍스트
        status = f"마지막 업데이트: {datetime.now().strftime('%H:%M:%S')} | 데이터 포인트: {data_store.get_data_count()}"
        
        return (
            cpu_gauge, gpu_gauge, memory_gauge,
            cpu_freq, gpu_mem, mem_usage,
            cpu_temp, gpu_temp, mem_total, disk_total,
            cpu_history_chart, memory_history_chart, network_chart, disk_io_chart, disk_partitions_chart,
            status,
        )
