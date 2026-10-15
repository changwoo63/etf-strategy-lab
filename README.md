# 미국 ETF 투자전략 실험실 v0.2

## 실행 (Mac)

기존 v0.1 Streamlit 서버는 터미널에서 Ctrl+C로 중지합니다.

```bash
cd ~/Downloads/ETF_Lab_MVP_v02
python3 -m pip install -r requirements.txt
python3 -m streamlit run app.py
```

세 탭: (1) 매수 규칙 초안 생성·JSON/TXT 저장, (2) 기존 전략 백테스트, (3) 1분 피드백 파일 저장.

## 주의
- ETF 적합성 판단 및 투자권유 아님. 주문은 자동 실행되지 않습니다.
- 분석은 교육용 과거 시뮬레이션이며 거래비용·세금·환율을 반영하지 않습니다.
- 피드백은 자동 전송되지 않으므로 파일을 고객에게서 받아야 합니다.
