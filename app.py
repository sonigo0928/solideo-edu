# -*- coding: utf-8 -*-
"""
시스템 리소스 모니터링 대시보드 - 메인 애플리케이션
================================================================================
실시간으로 CPU, GPU, 메모리, 디스크, 네트워크 등 시스템 리소스를 모니터링하고,
5분간 데이터를 수집한 후 상세한 PDF 보고서를 생성합니다.

사용법:
    python app.py
    
    브라우저에서 http://127.0.0.1:8050 접속
================================================================================
"""

import os
import sys
import logging

# 현재 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dash import Dash
import dash_bootstrap_components as dbc

from config import HOST, PORT, DEBUG
from ui.layout import create_layout
from ui.callbacks import register_callbacks

logger = logging.getLogger(__name__)


def check_dependencies():
    """필수 의존성 확인"""
    required_modules = [
        'psutil',
        'plotly',
        'dash',
        'jinja2',
        'apscheduler',
    ]

    missing = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)

    if missing:
        logger.error(f"다음 필수 모듈이 설치되어 있지 않습니다: {', '.join(missing)}")
        logger.error("다음 명령으로 설치하세요: pip install -r requirements.txt")
        sys.exit(1)

    logger.info("모든 필수 의존성이 설치되어 있습니다.")


def create_app() -> Dash:
    """Dash 애플리케이션 생성"""
    
    # Bootstrap 테마 적용
    app = Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.DARKLY,
            'https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap',
        ],
        title='System Resource Monitor',
        update_title='Updating...',
        suppress_callback_exceptions=True,
    )
    
    # 메타 태그 설정
    app.index_string = '''
    <!DOCTYPE html>
    <html>
        <head>
            {%metas%}
            <title>{%title%}</title>
            <meta name="description" content="실시간 시스템 리소스 모니터링 대시보드">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <link rel="icon" type="image/x-icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>">
            {%css%}
        </head>
        <body>
            {%app_entry%}
            <footer>
                {%config%}
                {%scripts%}
                {%renderer%}
            </footer>
        </body>
    </html>
    '''
    
    # 레이아웃 설정
    app.layout = create_layout()
    
    # 콜백 등록
    register_callbacks(app)
    
    return app


def main():
    """메인 함수"""
    # 의존성 확인
    check_dependencies()

    print("=" * 60)
    print("  [*] System Resource Monitor")
    print("  시스템 리소스 모니터링 대시보드")
    print("=" * 60)
    print()
    print(f"  [>] 서버 시작: http://{HOST}:{PORT}")
    print(f"  [>] 출력 디렉토리: output/")
    print()
    print("  사용법:")
    print("    1. 브라우저에서 위 주소로 접속")
    print("    2. '5분 모니터링 시작' 버튼 클릭")
    print("    3. 모니터링 완료 후 'PDF 보고서 생성' 클릭")
    print()
    print("  종료하려면 Ctrl+C를 누르세요.")
    print("=" * 60)
    print()

    # 애플리케이션 생성 및 실행
    try:
        app = create_app()
        app.run(host=HOST, port=PORT, debug=DEBUG)
    except KeyboardInterrupt:
        logger.info("애플리케이션이 종료되었습니다.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"애플리케이션 오류: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
