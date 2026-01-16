# System Resource Monitor

실시간 시스템 리소스 모니터링 대시보드

## 📊 소개

Windows 환경에서 CPU, GPU, 메모리, 디스크, 네트워크 등 시스템 리소스를 실시간으로 모니터링하고, 5분간 데이터를 수집한 후 상세한 PDF 보고서를 생성하는 웹 기반 대시보드 애플리케이션입니다.

## ✨ 주요 기능

- **실시간 모니터링**: 1초 간격으로 시스템 리소스 데이터 수집
- **CPU 모니터링**: 사용률, 주파수, 온도 추적
- **GPU 모니터링**: NVIDIA GPU 사용률, 메모리, 온도 (GPUtil 사용)
- **메모리 모니터링**: RAM 및 스왑 메모리 사용량
- **디스크 모니터링**: 파티션별 사용량 및 I/O 속도
- **네트워크 모니터링**: 업로드/다운로드 트래픽 추적
- **5분 모니터링 세션**: 정확히 5분간 데이터 수집
- **PDF 보고서 생성**: 그래프와 통계가 포함된 상세 보고서

## 🛠️ 기술 스택

| 구분            | 기술                |
| --------------- | ------------------- |
| 언어            | Python 3.10+        |
| 웹 프레임워크   | Plotly Dash         |
| 시스템 모니터링 | psutil, GPUtil, WMI |
| 시각화          | Plotly.js           |
| PDF 생성        | WeasyPrint, Jinja2  |

## 📦 설치 방법

```bash
# 저장소 클론
git clone https://github.com/sonigo0928/solideo-edu.git
cd solideo-edu

# 의존성 설치
pip install -r requirements.txt
```

## 🚀 실행 방법

```bash
python app.py
```

브라우저에서 `http://127.0.0.1:8050` 접속

## 📖 사용법

1. 브라우저에서 대시보드 접속
2. **"5분 모니터링 시작"** 버튼 클릭
3. 5분간 데이터 수집 (실시간 그래프 확인 가능)
4. 모니터링 완료 후 **"PDF 보고서 생성"** 클릭
5. PDF 파일 다운로드

## 📁 프로젝트 구조

```
├── app.py                    # 메인 애플리케이션
├── config.py                 # 설정 파일
├── requirements.txt          # 의존성 패키지
│
├── monitors/                 # 리소스 모니터링 모듈
│   ├── cpu_monitor.py        # CPU 모니터링
│   ├── gpu_monitor.py        # GPU 모니터링
│   ├── memory_monitor.py     # 메모리 모니터링
│   ├── disk_monitor.py       # 디스크 모니터링
│   └── network_monitor.py    # 네트워크 모니터링
│
├── data/                     # 데이터 저장
│   └── data_store.py         # 시계열 데이터 관리
│
├── ui/                       # UI 컴포넌트
│   ├── layout.py             # 대시보드 레이아웃
│   └── callbacks.py          # 실시간 업데이트 콜백
│
├── reports/                  # PDF 보고서 관련
│   ├── generator.py          # PDF 생성 로직
│   └── templates/            # HTML 템플릿
│
└── assets/                   # CSS 정적 파일
    └── style.css
```

## 📸 스크린샷

_(대시보드 스크린샷)_

## ⚠️ 주의사항

- **GPU 모니터링**: NVIDIA GPU에서만 작동합니다 (GPUtil 사용)
- **온도 모니터링**: Windows에서 관리자 권한이 필요할 수 있습니다
- **PDF 생성**: WeasyPrint 설치 필요 (GTK 런타임 필요할 수 있음)

## 📄 라이선스

MIT License

## 👤 개발자

sonigo0928
