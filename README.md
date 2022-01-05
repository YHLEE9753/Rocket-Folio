# Rocket-Folio

Backend = Django<br>
Frontend = HTML, CSS, CS<br>
Deployment = AWS(EC2), uwsgi, nginx<br>

## Description
웹 어플리케이션으로 비트코인 주식 자산 포트폴리오 어플리케이션입니다.
주식 종목간 상관관계와 백테스팅을 통한 자산 분석을 제공합니다.

## utils
실시간 주식 데이터 : BeautifulSoup 를 통한 네이버 증권 크롤링<br>
가상화폐 데이터 : Pyupbit API 연동<br>
주식 데이터 : 대신증권 API 를 통해 코스피 코스닥 전체 주식데이터 이용<br>
그래프 : (Opensource) FusionCharts 사용<br>
로그인 : Google OAuth<br>

## Functions
1. 포트폴리오에 주식추가
2. 소유 주식에 대한 현재가 및 관련데이터 제공(크롤링을 통해 현재 가격 제공)
3. 최대 5개의 주식간 상관관계 정보 제공(5개선택)
4. 최대 2016년 부터의 백테스팅 그래프 제공
5. 백테스팅 구성 주식데이터 정보 제공

자세한 설명 : PPT 
