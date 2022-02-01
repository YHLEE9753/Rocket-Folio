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

## Images
**구글로그인**<br>
![1_login](https://user-images.githubusercontent.com/71916223/151946022-fe7e7ff4-ca91-45de-9b4c-ab62eab70706.png)
<br><br>**포트폴리오**<br>
![2_pf](https://user-images.githubusercontent.com/71916223/151946028-1848dabc-20cc-42e0-aba6-88f74288656d.png)
<br><br>**분석**<br>
![3_an1](https://user-images.githubusercontent.com/71916223/151946029-0b23f521-a0e2-4be2-b7da-251a0c258305.png)
![4_an2](https://user-images.githubusercontent.com/71916223/151946032-2cec61d1-1d20-4ebd-bce5-03811c55a639.png)
![5_an3](https://user-images.githubusercontent.com/71916223/151946033-ce82281e-2a57-41fd-93ce-cda622c806a4.png)
![6_an4](https://user-images.githubusercontent.com/71916223/151946034-b0bee6a1-e2cd-4cad-a574-74ad5b4ee264.png)


### 자세한 설명 : PPT 
