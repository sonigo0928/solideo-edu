# -*- coding: utf-8 -*-
"""
대시보드 레이아웃 모듈
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from config import COLORS, MONITORING_DURATION_SECONDS


def create_gauge_card(id_prefix: str, title: str, icon: str, color: str) -> dbc.Card:
    """게이지 차트 카드 생성"""
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={'fontSize': '1.5rem', 'marginRight': '10px'}),
                html.Span(title, style={'fontSize': '1.1rem', 'fontWeight': '600'}),
            ], style={'marginBottom': '10px', 'color': color}),
            dcc.Graph(
                id=f'{id_prefix}-gauge',
                config={'displayModeBar': False},
                style={'height': '180px'},
            ),
            html.Div(
                id=f'{id_prefix}-info',
                style={'textAlign': 'center', 'fontSize': '0.9rem', 'color': COLORS['text']},
            ),
        ]),
        style={
            'backgroundColor': COLORS['card_bg'],
            'border': f'1px solid {color}33',
            'borderRadius': '16px',
            'boxShadow': f'0 4px 20px {color}22',
        },
    )


def create_chart_card(id_prefix: str, title: str, icon: str, height: str = '300px') -> dbc.Card:
    """차트 카드 생성"""
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={'fontSize': '1.3rem', 'marginRight': '10px'}),
                html.Span(title, style={'fontSize': '1.1rem', 'fontWeight': '600'}),
            ], style={'marginBottom': '15px', 'color': COLORS['text']}),
            dcc.Graph(
                id=f'{id_prefix}-chart',
                config={'displayModeBar': False},
                style={'height': height},
            ),
        ]),
        style={
            'backgroundColor': COLORS['card_bg'],
            'border': f'1px solid {COLORS["primary"]}33',
            'borderRadius': '16px',
            'boxShadow': f'0 4px 20px rgba(0,0,0,0.3)',
        },
    )


def create_stat_card(id_prefix: str, title: str, icon: str, color: str) -> dbc.Card:
    """통계 카드 생성"""
    return dbc.Card(
        dbc.CardBody([
            html.Div([
                html.Span(icon, style={'fontSize': '2rem'}),
            ], style={'textAlign': 'center', 'marginBottom': '10px', 'color': color}),
            html.H4(
                id=f'{id_prefix}-value',
                children='--',
                style={'textAlign': 'center', 'color': COLORS['text'], 'fontWeight': '700', 'margin': '0'},
            ),
            html.P(
                title,
                style={'textAlign': 'center', 'color': f'{COLORS["text"]}99', 'fontSize': '0.85rem', 'margin': '5px 0 0 0'},
            ),
        ]),
        style={
            'backgroundColor': COLORS['card_bg'],
            'border': f'1px solid {color}44',
            'borderRadius': '12px',
            'padding': '5px',
        },
    )


def create_layout() -> html.Div:
    """메인 대시보드 레이아웃 생성"""
    return html.Div([
        # 인터벌 컴포넌트
        dcc.Interval(
            id='interval-component',
            interval=1000,  # 1초마다 업데이트
            n_intervals=0,
        ),
        
        # 상태 저장소
        dcc.Store(id='monitoring-state', data={'active': False, 'elapsed': 0}),
        
        # 헤더
        html.Div([
            html.Div([
                html.H1([
                    html.Span('📊', style={'marginRight': '15px'}),
                    'System Resource Monitor',
                ], style={
                    'margin': '0',
                    'fontSize': '2rem',
                    'fontWeight': '700',
                    'background': f'linear-gradient(135deg, {COLORS["primary"]}, {COLORS["secondary"]})',
                    'WebkitBackgroundClip': 'text',
                    'WebkitTextFillColor': 'transparent',
                }),
                html.P(
                    '실시간 시스템 리소스 모니터링 대시보드',
                    style={'margin': '5px 0 0 0', 'color': f'{COLORS["text"]}88', 'fontSize': '0.95rem'},
                ),
            ]),
            html.Div([
                # 타이머 표시
                html.Div([
                    html.Span('⏱️', style={'marginRight': '8px', 'fontSize': '1.2rem'}),
                    html.Span(id='timer-display', children='00:00', style={'fontSize': '1.5rem', 'fontWeight': '600'}),
                    html.Span(f' / {MONITORING_DURATION_SECONDS // 60}:00', style={'color': f'{COLORS["text"]}66'}),
                ], style={
                    'padding': '10px 20px',
                    'backgroundColor': COLORS['card_bg'],
                    'borderRadius': '10px',
                    'marginRight': '15px',
                    'color': COLORS['text'],
                }),
                # 모니터링 버튼
                dbc.Button(
                    [html.Span('▶️', style={'marginRight': '8px'}), '5분 모니터링 시작'],
                    id='start-monitoring-btn',
                    color='primary',
                    style={
                        'background': f'linear-gradient(135deg, {COLORS["primary"]}, {COLORS["secondary"]})',
                        'border': 'none',
                        'borderRadius': '10px',
                        'padding': '12px 24px',
                        'fontWeight': '600',
                        'marginRight': '10px',
                    },
                ),
                # PDF 생성 버튼
                dbc.Button(
                    [html.Span('📄', style={'marginRight': '8px'}), 'PDF 보고서 생성'],
                    id='generate-pdf-btn',
                    color='success',
                    disabled=True,
                    style={
                        'borderRadius': '10px',
                        'padding': '12px 24px',
                        'fontWeight': '600',
                    },
                ),
                # PDF 다운로드 링크
                dcc.Download(id='download-pdf'),
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ], style={
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'padding': '20px 30px',
            'backgroundColor': COLORS['card_bg'],
            'borderRadius': '16px',
            'marginBottom': '20px',
            'boxShadow': '0 4px 20px rgba(0,0,0,0.3)',
        }),
        
        # 알림 영역
        html.Div(id='alert-container'),
        
        # 온도 상태 표시줄
        dbc.Row([
            dbc.Col([
                create_stat_card('cpu-temp', 'CPU 온도', '🌡️', COLORS['cpu']),
            ], width=3),
            dbc.Col([
                create_stat_card('gpu-temp', 'GPU 온도', '🔥', COLORS['gpu']),
            ], width=3),
            dbc.Col([
                create_stat_card('memory-total', '메모리', '💾', COLORS['memory']),
            ], width=3),
            dbc.Col([
                create_stat_card('disk-total', '디스크', '💿', COLORS['disk']),
            ], width=3),
        ], style={'marginBottom': '20px'}),
        
        # 게이지 차트 행
        dbc.Row([
            dbc.Col([
                create_gauge_card('cpu', 'CPU 사용률', '⚡', COLORS['cpu']),
            ], width=4),
            dbc.Col([
                create_gauge_card('gpu', 'GPU 사용률', '🎮', COLORS['gpu']),
            ], width=4),
            dbc.Col([
                create_gauge_card('memory', '메모리 사용률', '📊', COLORS['memory']),
            ], width=4),
        ], style={'marginBottom': '20px'}),
        
        # CPU/메모리 실시간 차트
        dbc.Row([
            dbc.Col([
                create_chart_card('cpu-history', 'CPU 사용률 추이', '📈'),
            ], width=6),
            dbc.Col([
                create_chart_card('memory-history', '메모리 사용률 추이', '📉'),
            ], width=6),
        ], style={'marginBottom': '20px'}),
        
        # 네트워크 트래픽 차트
        dbc.Row([
            dbc.Col([
                create_chart_card('network', '네트워크 트래픽', '🌐', '280px'),
            ], width=8),
            dbc.Col([
                create_chart_card('disk-io', '디스크 I/O', '💽', '280px'),
            ], width=4),
        ], style={'marginBottom': '20px'}),
        
        # 디스크 파티션 사용량
        dbc.Row([
            dbc.Col([
                create_chart_card('disk-partitions', '디스크 파티션별 사용량', '📁', '250px'),
            ], width=12),
        ], style={'marginBottom': '20px'}),
        
        # 푸터
        html.Div([
            html.P([
                '© 2024 System Resource Monitor | ',
                html.Span('실시간 데이터 갱신 중...', id='status-text'),
            ], style={'margin': '0', 'color': f'{COLORS["text"]}66', 'fontSize': '0.85rem'}),
        ], style={
            'textAlign': 'center',
            'padding': '15px',
            'marginTop': '10px',
        }),
        
    ], style={
        'padding': '20px',
        'minHeight': '100vh',
        'background': f'linear-gradient(180deg, {COLORS["background"]} 0%, #1a1a3e 100%)',
    })
