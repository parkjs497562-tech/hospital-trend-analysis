"""KOSIS 월별 병원 이용 데이터 시계열 분석 스크립트."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "hospital_monthly.csv"
IMAGE_DIR = BASE_DIR / "images"
PATIENT_COL = "inpatient_outpatient_days"
EXPENSE_COL = "medical_expenses"


def main():
    # 분석에 필요한 열만 읽고 날짜를 날짜형으로 바꿉니다.
    data = pd.read_csv(DATA_PATH, parse_dates=["date"])
    data = data.sort_values("date").reset_index(drop=True)
    data[PATIENT_COL] = pd.to_numeric(data[PATIENT_COL], errors="coerce")
    data[EXPENSE_COL] = pd.to_numeric(data[EXPENSE_COL], errors="coerce")

    # 분석 기간과 핵심 변수의 데이터가 완전한지 확인합니다.
    expected_dates = pd.date_range("2004-01-01", "2024-12-01", freq="MS")
    if len(data) != 252 or not data["date"].equals(pd.Series(expected_dates, name="date")):
        raise ValueError("분석 데이터가 2004년 1월부터 2024년 12월까지 252개월과 일치하지 않습니다.")
    if data[[PATIENT_COL, EXPENSE_COL]].isna().any().any():
        raise ValueError("분석 변수에 결측값이 있습니다.")

    # 연도별 평균과 합계로 장기 변화의 규모를 요약합니다.
    data["year"] = data["date"].dt.year
    data["month"] = data["date"].dt.month
    yearly = data.groupby("year").agg(
        patient_mean=(PATIENT_COL, "mean"),
        patient_sum=(PATIENT_COL, "sum"),
        expense_sum=(EXPENSE_COL, "sum"),
    )

    # 같은 달끼리 여러 해를 비교해 월별 계절 패턴을 살핍니다.
    monthly = data.groupby("month")[PATIENT_COL].mean().reindex(range(1, 13))
    if monthly.isna().any() or len(monthly) != 12:
        raise ValueError("월별 평균 12개가 모두 계산되지 않았습니다.")

    # 12개월 이동평균은 직전 12개월, 전년 동월 변화율은 12개월 전과 비교합니다.
    data["moving_average_12m"] = data[PATIENT_COL].rolling(window=12, min_periods=12).mean()
    data["yoy_change_pct"] = data[PATIENT_COL].pct_change(periods=12, fill_method=None) * 100
    if data["moving_average_12m"].notna().sum() != 241:
        raise ValueError("12개월 이동평균 유효값 수가 예상과 다릅니다.")

    # Windows의 맑은 고딕을 사용하고, 없으면 Matplotlib 기본 글꼴을 사용합니다.
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)

    # 그래프 1: 전체 기간의 월별 입내원일수입니다.
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(data["date"], data[PATIENT_COL], color="#2563a6", linewidth=1.25, label="월별 입내원일수")
    ax.set_title("월별 입내원일수 추세 (2004–2024)")
    ax.set_xlabel("연월")
    ax.set_ylabel("입내원일수 (일)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(IMAGE_DIR / "01_patient_trend.png", dpi=160)
    plt.close(fig)

    # 그래프 2: 모든 해의 같은 달을 평균해 월별 차이를 비교합니다.
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(monthly.index, monthly.values, color="#4d9b73", label="월평균 입내원일수")
    ax.set_title("월별 평균 입내원일수 비교 (2004–2024)")
    ax.set_xlabel("월")
    ax.set_ylabel("평균 입내원일수 (일)")
    ax.set_xticks(range(1, 13), [f"{month}월" for month in range(1, 13)])
    ax.grid(axis="y", alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(IMAGE_DIR / "02_monthly_comparison.png", dpi=160)
    plt.close(fig)

    # 그래프 3: 월별 원자료와 12개월 이동평균을 함께 표시합니다.
    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.plot(data["date"], data[PATIENT_COL], color="#9bb7d4", linewidth=0.8, label="월별 입내원일수")
    ax.plot(data["date"], data["moving_average_12m"], color="#c34a36", linewidth=2.0, label="12개월 이동평균")
    ax.set_title("월별 입내원일수와 12개월 이동평균")
    ax.set_xlabel("연월")
    ax.set_ylabel("입내원일수 (일)")
    ax.grid(True, alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(IMAGE_DIR / "03_moving_average.png", dpi=160)
    plt.close(fig)

    # 명목 진료비와 입내원일수의 연도별 변화를 나란히 확인합니다.
    patient_first = yearly.loc[2004, "patient_sum"]
    patient_last = yearly.loc[2024, "patient_sum"]
    expense_first = yearly.loc[2004, "expense_sum"]
    expense_last = yearly.loc[2024, "expense_sum"]
    patient_growth = (patient_last / patient_first - 1) * 100
    expense_growth = (expense_last / expense_first - 1) * 100
    season_high = int(monthly.idxmax())
    season_low = int(monthly.idxmin())
    yoy = data.dropna(subset=["yoy_change_pct"])

    print("=== 데이터 확인 ===")
    print(f"관측값: {len(data)}개월 ({data['date'].min():%Y-%m} ~ {data['date'].max():%Y-%m})")
    print("=== 연도별 입내원일수 평균(일), 합계(일), 진료비 합계(천원) ===")
    print(yearly.round(2).to_string())
    print("=== 월별 평균 입내원일수(일) ===")
    print(monthly.round(2).to_string())
    print(f"월평균 최고: {season_high}월 ({monthly.loc[season_high]:,.2f}일), 최저: {season_low}월 ({monthly.loc[season_low]:,.2f}일)")
    print(f"입내원일수 합계 변화(2004→2024): {patient_growth:+.2f}%")
    print(f"명목 진료비 합계 변화(2004→2024): {expense_growth:+.2f}%")
    print("주의: 진료비는 명목 금액이며 물가상승률을 반영하지 않았습니다.")
    print(f"12개월 이동평균 유효값: {data['moving_average_12m'].notna().sum()}개; 전년 동월 변화율 유효값: {len(yoy)}개")
    print("전년 동월 증감률 증가 상위 5개 시점:")
    print(yoy.nlargest(5, "yoy_change_pct")[["date", "yoy_change_pct"]].to_string(index=False, formatters={"date": lambda value: value.strftime("%Y-%m"), "yoy_change_pct": "{:+.2f}%".format}))
    print("전년 동월 증감률 감소 상위 5개 시점:")
    print(yoy.nsmallest(5, "yoy_change_pct")[["date", "yoy_change_pct"]].to_string(index=False, formatters={"date": lambda value: value.strftime("%Y-%m"), "yoy_change_pct": "{:+.2f}%".format}))
    print("그래프 파일:")
    for filename in ("01_patient_trend.png", "02_monthly_comparison.png", "03_moving_average.png"):
        image_path = IMAGE_DIR / filename
        if not image_path.is_file() or image_path.stat().st_size == 0:
            raise RuntimeError(f"그래프 생성에 실패했습니다: {image_path}")
        print(f"- {image_path} ({image_path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()


