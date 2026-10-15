"""ETF 투자전략 실험실 v0.2 — 규칙 생성 + 과거 전략 비교. 투자자문/자동주문 아님."""
from pathlib import Path
import json
from datetime import date
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='미국 ETF 투자전략 실험실',page_icon='📈',layout='wide')
st.title('미국 ETF 투자전략 실험실')
st.caption('v0.2 · 나만의 규칙 만들기 → 기록 → 과거 전략 비교')
tab_plan,tab_backtest,tab_feedback=st.tabs(['① 매수 규칙 만들기','② 과거 전략 실험','③ 1분 피드백'])

with tab_plan:
    st.subheader('매수 결정을 매번 다시 하지 않도록')
    st.write('원하는 ETF와 예산을 선택하면 실행하기 쉬운 **매수 규칙 초안**을 만듭니다. 주문은 직접 확인하고 실행합니다.')
    left,right=st.columns([1,1])
    with left:
        asset=st.selectbox('관심 ETF',['QQQ','QLD','TQQQ'],key='plan_etf')
        budget=st.number_input('월 투자 예산 (원)',min_value=10000,max_value=100000000,value=300000,step=10000)
        freq=st.radio('매수 주기',['매월','매주','매 거래일'],horizontal=True)
        cash_weight=st.slider('현금성 자산으로 적립할 비중 (%)',0,80,25,5)
        horizon=st.selectbox('예상 투자 기간',['3년 미만','3~5년','5~10년','10년 이상'],index=3)
        loss=st.selectbox('손실이 발생해도 감당할 수 있다고 생각하는 범위',['잘 모르겠음','-10%','-30%','-50%','-70% 이상'])
        risky_debt=st.checkbox('고금리 대출이 있다')
    events={'매월':1,'매주':4,'매 거래일':21}[freq]
    etf_month=round(budget*(100-cash_weight)/100)
    reserve_month=budget-etf_month
    plan={
        'product':'미국 ETF 투자전략 실험실','version':'0.2','created_on':str(date.today()),
        'etf':asset,'monthly_budget_krw':budget,'frequency':freq,
        'monthly_etf_krw':etf_month,'monthly_reserve_krw':reserve_month,
        'cash_pct':cash_weight,'estimated_purchases_per_month':events,
        'estimated_etf_per_purchase_krw':round(etf_month/events),
        'estimated_reserve_per_purchase_krw':round(reserve_month/events),
        'horizon':horizon,'self_reported_loss_tolerance':loss,'has_high_interest_debt':risky_debt,
        'execution':'manual_confirmation_only'
    }
    with right:
        st.markdown('### 내 매수 규칙 초안')
        st.metric('월 ETF 투자 예산',f'{etf_month:,}원')
        st.metric('월 현금성 예산',f'{reserve_month:,}원')
        st.info(f'**{asset}** · **{freq}** · ETF 1회 약 **{round(etf_month/events):,}원** / 현금성 1회 약 **{round(reserve_month/events):,}원**')
        st.write('**기본 실행 규칙**')
        st.write('1. 정해진 날짜에 매수 가능 여부와 사용 가능한 잔고 확인')
        st.write('2. 계획된 예산 내에서 주문금액을 직접 확인하고 매수')
        st.write('3. 실행 여부를 기록하고 다음 예정일에 반복')
        if risky_debt: st.warning('고금리 대출이 있습니다. 조기상환 대안과 필수 지출을 먼저 확인해 주세요.')
        if asset in ['QLD','TQQQ']: st.warning(f'{asset}는 일일 레버리지 ETF로, 장기 손실이 매우 클 수 있습니다. 이 결과는 적합성 판단이 아닙니다.')
        if loss=='잘 모르겠음': st.warning('실제 손실 감내 능력이 불확실합니다. 큰 하락 시 투자 중단·매도 상황을 별도로 점검하세요.')
        st.download_button('내 투자 규칙 저장 (JSON)',json.dumps(plan,ensure_ascii=False,indent=2).encode('utf-8'),file_name='my_etf_plan.json',mime='application/json',use_container_width=True)
        textplan=(f'ETF: {asset}\n월 예산: {budget:,}원\nETF: {etf_month:,}원 / 현금성: {reserve_month:,}원\n주기: {freq}\nETF 1회 예산(근사): {round(etf_month/events):,}원\n사용자가 확인 후 주문')
        st.download_button('매수 규칙 메모 받기 (TXT)',textplan.encode('utf-8-sig'),file_name='my_etf_plan.txt',mime='text/plain',use_container_width=True)
    st.caption('월 거래일은 21일, 주간 매수는 월 4회로 단순 환산합니다. 실제 매수일·환율·거래수수료·소수점 거래 조건에 따라 달라집니다. 주문 및 계좌 연동은 제공하지 않습니다.')

with tab_feedback:
    st.subheader('1분만 써보고 알려주세요')
    st.write('첫 고객 피드백 10개를 모아 다음 개발 우선순위를 정합니다. 이 버전은 **응답을 서버로 전송하지 않고 파일로 저장**합니다.')
    useful=st.radio('이 규칙 생성 기능이 필요한가요?',['매우 필요','어느 정도 필요','필요 없음'],horizontal=True)
    nextfeature=st.radio('어떤 기능이 가장 필요할까요?',['실제 매수 일정표','적립식 vs 분할매수 백테스트','매수 완료 기록','증권사 자동 주문(장기 아이디어)'])
    pay=st.radio('기능이 충분히 작동한다면 유료로 이용할 의향이 있나요?',['있음','기능을 더 봐야 함','없음'],horizontal=True)
    feedback=st.text_area('가장 불편하거나 고쳤으면 하는 점 (선택)')
    response={'date':str(date.today()),'utility':useful,'top_requested_feature':nextfeature,'willingness_to_pay':pay,'comment':feedback}
    st.download_button('피드백 저장하기',json.dumps(response,ensure_ascii=False,indent=2).encode('utf-8'),file_name='feedback.json',mime='application/json')
    st.caption('테스트 사용자에게 이 파일을 받아 취합할 수 있습니다. 자동 전송·중앙 수집 기능은 아직 없습니다.')

with tab_backtest:
    st.caption('기존 v0.1 과거 전략 비교 기능. 가격 데이터는 동봉된 과거 데이터이며 새로 자동 갱신되지 않습니다.')
    @st.cache_data
    def load_prices():
        p=pd.read_csv(Path(__file__).parent/'data'/'prices.csv',parse_dates=['Date'],encoding='utf-8-sig').set_index('Date').sort_index()
        return p[['QLD','TQQQ','CASH_PROXY']].dropna()

    p=load_prices()
    with st.sidebar:
        st.header('실험 조건')
        etf=st.selectbox('투자 ETF',['QLD','TQQQ'])
        monthly=st.number_input('월 납입금 (USD)',min_value=10.,max_value=100000.,value=1000.,step=100.)
        start=st.date_input('시작일',value=p.index[0].date(),min_value=p.index[0].date(),max_value=p.index[-2].date())
        end=st.date_input('종료일',value=p.index[-1].date(),min_value=p.index[1].date(),max_value=p.index[-1].date())
        reserve_pct=st.slider('C: SGOV 신규 납입 비중 (%)',0,90,25,5)
        t1=st.slider('C: 첫 하락 진입 (%)',10,70,40,5)
        delta=st.select_slider('C: 다음 단계 간격 (%p)',options=[5,10,15,20],value=10)
        portions=st.text_input('C: 3단계 투입비중 (최초 예비금 기준, %)',value='10,30,50')
        st.caption('A: 월 적립금 100% ETF 매수 / B: 매월 현금 적립 후 매년 1월 첫 거래일 일괄 ETF 매수 / C: ETF와 현금성 ETF를 나눠 적립하고 하락 시 추가매수')
    try:
        weights=[float(x.strip())/100 for x in portions.split(',')]
        if len(weights)!=3 or any(w<0 for w in weights) or sum(weights)>1.0000001: raise ValueError
    except ValueError:
        st.error('투입 비중을 예: 10,30,50 형태로 입력하세요. 합계는 100% 이하이어야 합니다.')
        st.stop()
    if start>=end:
        st.error('종료일은 시작일보다 나중이어야 합니다.');st.stop()
    pxdata=p.loc[str(start):str(end)]
    if len(pxdata)<25:
        st.error('기간이 너무 짧습니다.');st.stop()

    # 투자금은 매월 첫 거래일에 동일하게 납입한다. 가격은 해당일 조정종가에 체결됐다고 가정.
    months=pxdata.index.to_period('M')
    payday=(months!=months.shift(1)) if hasattr(months,'shift') else None
    # pandas PeriodIndex.shift(1)은 달 이동이므로 이전 원소 비교는 직접 생성.
    payday=np.r_[True, months[1:].to_numpy()!=months[:-1].to_numpy()]

    def run_strategy(kind):
        q=0.;cash=0.; pending=0.; deposit=0.; peak=0.; triggered=set();starting_reserve=0.
        last_val=None; nav=100.; maxnav=100.; mdd=0.; rows=[]; trades=[]
        first_year=None
        for n,(date,row) in enumerate(pxdata.iterrows()):
            ep=float(row[etf]);cp=float(row['CASH_PROXY'])
            if payday[n]:
                deposit+=monthly
                if kind=='A': q+=monthly/ep
                elif kind=='B': cash+=monthly/cp;pending+=monthly
                else:
                    q+=monthly*(1-reserve_pct/100)/ep
                    cash+=monthly*(reserve_pct/100)/cp
            if kind=='B':
                # 첫 거래일에는 아직 축적 기간이 없음. 이후 연도 변경 첫 거래일에 일괄투자.
                if first_year is None:first_year=date.year
                elif date.year!=first_year:
                    amt=cash*cp
                    q+=amt/ep;cash=0.;pending=0.;first_year=date.year
                    trades.append({'날짜':date,'단계':'연초 거치','하락률_%':np.nan,'투입액_USD':amt})
            elif kind=='C':
                if ep>peak:
                    peak=ep
                    if triggered:
                        triggered=set();starting_reserve=0.
                dd=100*(1-ep/peak)
                for i,(level,w) in enumerate(zip([t1,t1+delta,t1+2*delta],weights)):
                    if dd>=level and i not in triggered:
                        if not triggered:starting_reserve=cash*cp
                        invest=min(starting_reserve*w,cash*cp)
                        if invest>0:
                            cash-=invest/cp;q+=invest/ep
                            trades.append({'날짜':date,'단계':f'{i+1}차 (-{level}%)','하락률_%':round(dd,2),'투입액_USD':round(invest,2)})
                        triggered.add(i)
            value=q*ep+cash*cp
            if last_val is not None and last_val>0:
                newcash=monthly if payday[n] else 0.
                nav*= (value-newcash)/last_val
            last_val=value
            maxnav=max(maxnav,nav);mdd=min(mdd,(nav/maxnav-1)*100)
            rows.append((date,value,deposit,nav,100*q*ep/value if value else 0))
        curve=pd.DataFrame(rows,columns=['Date','평가액','총납입','시간가중지수','ETF비중']).set_index('Date')
        summary={'전략':kind,'최종평가액_USD':value,'누적납입_USD':deposit,'원금대비수익률_%':(value/deposit-1)*100,'MDD_%':mdd,'추가매수횟수':len(trades),'ETF최종비중_%':100*q*ep/value}
        return summary,curve,pd.DataFrame(trades)

    results={k:run_strategy(k) for k in ['A','B','C']}
    summary=pd.DataFrame([v[0] for v in results.values()])
    st.subheader('전략별 결과')
    st.dataframe(summary.style.format({'최종평가액_USD':'{:,.0f}','누적납입_USD':'{:,.0f}','원금대비수익률_%':'{:+,.1f}','MDD_%':'{:.1f}','ETF최종비중_%':'{:.1f}'}),use_container_width=True,hide_index=True)
    combined=pd.concat({k:v[1]['평가액'] for k,v in results.items()},axis=1)
    fig=px.line(combined,x=combined.index,y=combined.columns,labels={'value':'평가액(USD)','index':'날짜','variable':'전략'},title='자산 평가액 추이')
    st.plotly_chart(fig,use_container_width=True)
    st.markdown('**기본 가정**: 매월 첫 거래일 종가로 납입금을 투자합니다. 미투자 자금은 CASH_PROXY(BIL/SGOV 연결 계열)에 보관합니다. B는 매년 첫 거래일에 대기자금을 QLD 또는 TQQQ로 전환합니다. C는 고점 대비 하락 시 보유 현금 일부를 ETF로 전환합니다. QLD/TQQQ 직접투자는 일일 레버리지 상품의 큰 손실 위험이 있습니다.')
    st.caption('가격 파일의 2010~SGOV 출시 전 구간은 BIL 기반 대용값입니다. 종가 체결, 배당 조정가격, 환율·거래세금·슬리피지 제외. 과거 결과는 미래 성과를 보장하지 않습니다. 결과는 투자자문이 아닙니다.')
    st.subheader('매수 기록')
    choice=st.selectbox('매수 기록 전략',['C','B','A'])
    trades=results[choice][2]
    if len(trades):st.dataframe(trades,use_container_width=True,hide_index=True)
    else:st.info('선택 전략에서 추가매수 기록이 없습니다.')
    left,right=st.columns(2)
    with left:st.download_button('결과표 CSV',summary.to_csv(index=False).encode('utf-8-sig'),file_name='summary.csv',mime='text/csv')
    with right:st.download_button('자산곡선 CSV',combined.to_csv().encode('utf-8-sig'),file_name='equity.csv',mime='text/csv')
    with st.expander('개발 로드맵'):
        st.write('1. 백테스트 계산 엔진 별도 단위테스트 / 2. Macro Lab: FRED DGS10 병합 / 3. 동일 위험 예산 및 대출 상환 대안 비교 / 4. 배포와 고객 테스트')
