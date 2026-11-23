# 병원 이용량 시계열 분석

## 프로젝트 소개 및 분석 목적

국민건강보험공단의 월별 진료 자료를 이용해 2004년 1월부터 2024년 12월까지 병원 이용량의 장기 변화와 월별 패턴을 살펴보는 프로젝트입니다. 실제 KOSIS 자료를 정리하고 시계열 분석과 시각화를 수행합니다.

### 연구 질문

1. 병원 이용량은 장기적으로 어떻게 변화했는가?
2. 월별 병원 이용량에 차이가 있는가?
3. 급격한 증가 또는 감소가 발생한 시기는 언제인가?

## 데이터

- **출처:** [KOSIS 국가통계포털](https://kosis.kr/)
- **통계표:** 국민건강보험공단 「월별 진료형태별 진료현황(총계)」 (`TX_35001_A040`)
- **분석 기간:** 2004년 1월~2024년 12월
- **분석 데이터:** 252개월
- **주요 변수:**
  - `inpatient_outpatient_days`: 입내원일수, 단위 일
  - `medical_expenses`: 진료비, 단위 천원

`data` 폴더의 타임스탬프가 붙은 CSV 파일 두 개는 KOSIS에서 내려받은 원본 보관용 자료입니다. 두 파일은 삭제하거나 변경하지 않았으며, 분석용 표준 원본과 구분해 보관합니다. 분석 스크립트는 정리된 `data/hospital_monthly.csv`를 읽습니다.

## 사용 기술 및 분석 방법

- **사용 기술:** Python, Pandas, NumPy, Matplotlib
- **분석 방법:** 연도별 추세(평균·합계), 월별 평균 비교, 12개월 이동평균, 전년 동월 대비 증감률

## 생성 그래프

| 파일 | 설명 |
|---|---|
| `images/01_patient_trend.png` | 2004~2024년 월별 입내원일수 추세 |
| `images/02_monthly_comparison.png` | 1~12월의 평균 입내원일수 비교 |
| `images/03_moving_average.png` | 월별 입내원일수와 12개월 이동평균 비교 |

## 설치 및 실행 방법

프로젝트 폴더에서 Windows PowerShell을 열고 다음 명령을 실행합니다.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python analysis.py
```

PowerShell 실행 정책이 가상환경 활성화를 막는 경우, 현재 PowerShell 창에서만 실행 정책을 임시로 바꾼 뒤 활성화를 다시 시도할 수 있습니다. 이 변경은 시스템 전체 정책에 적용되지 않습니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

활성화 후 `python analysis.py`를 실행하면 분석 결과가 콘솔에 표시되고 `images` 폴더의 그래프 파일이 생성됩니다.
