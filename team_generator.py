# -*- coding: utf-8 -*-
import random
from data import TEAMS as BASE_TEAMS
from cl_data import CL_TEAMS as BASE_CL_TEAMS

# 추가 국가 목록과 기본 오버롤/FIFA 랭킹 설정
ADDITIONAL_NATIONS = {
    "VIE": {"name": "베트남", "rank": 115, "points": 1160, "continent": "아시아", "primary_color": "#DA251D", "secondary_color": "#FFFF00", "manager": "김상식", "names": ["응우옌 티엔 린", "응우옌 꽝 하이", "응우옌 꽁 푸엉", "팜 뚜안 하이", "도 훙 중", "응우옌 투안 안", "부 반 탄", "꿰 응옥 하이", "도안 반 하우", "부이 호앙 비엣 안", "당 반 람"]},
    "THA": {"name": "태국", "rank": 101, "points": 1210, "continent": "아시아", "primary_color": "#002060", "secondary_color": "#FFFFFF", "manager": "이시이 마사타다", "names": ["티라신 당다", "차나팁 송크라신", "티라톤 분마탄", "수파촉 사라차트", "수파낫 무에안타", "사라치 요옌", "판사 헴비분", "위라텝 뽐판", "카윈 탐삿차난", "크릿사다 카만", "파티왓 캄마이"]},
    "IDN": {"name": "인도네시아", "rank": 133, "points": 1100, "continent": "아시아", "primary_color": "#FF0000", "secondary_color": "#FFFFFF", "manager": "신태용", "names": ["라파엘 스트라윅", "라그나 오랏망운", "마르셀리노 페르디난", "톰 헤이", "이바르 제너", "위탄 술라에만", "프라타마 아르한", "제이 이드제스", "저스틴 허브너", "아스나위 망쿠알람", "에르난도 아리"]},
    "CHN": {"name": "중국", "rank": 92, "points": 1250, "continent": "아시아", "primary_color": "#EE1C25", "secondary_color": "#FFFF00", "manager": "브란코 이반코비치", "names": ["우레이", "장위닝", "웨이스하오", "왕상위안", "장즈펑", "리커", "장광타이", "주천제", "왕다레이", "류양", "가오준이"]},
    "IND": {"name": "인도", "rank": 124, "points": 1130, "continent": "아시아", "primary_color": "#0054B4", "secondary_color": "#FF9933", "manager": "마놀로 마르케스", "names": ["수닐 체트리", "랄리안주알라 창테", "아니루드 타파", "사할 압둘 사마드", "브랜든 페르난데스", "만비르 싱", "산데시 징간", "수바시시 보스", "안와르 알리", "라훌 베케", "구르프리트 싱 산두"]},
    "PRK": {"name": "북한", "rank": 110, "points": 1180, "continent": "아시아", "primary_color": "#ED1C24", "secondary_color": "#FFFFFF", "manager": "신영남", "names": ["한광성", "정일관", "최주성", "리은철", "김국범", "김유성", "장국철", "강국철", "백명성", "최옥철", "강주혁"]},
    "UZB": {"name": "우즈베키스탄", "rank": 62, "points": 1425, "continent": "아시아", "primary_color": "#0099B8", "secondary_color": "#FFFFFF", "manager": "스레치코 카타네츠", "names": ["엘도르 쇼무로도프", "아보스벡 파이줄라에프", "오타벡 슈쿠로프", "잘롤리딘 마샤리포프", "오스톤 우루노프", "야수르벡 야흐시보에프", "후스니딘 알리쿨로프", "루스탐 아슈르마토프", "파루흐 사이피에프", "우마르 에쉬무로도프", "우트키르 유수포프"]},
    "JOR": {"name": "요르단", "rank": 68, "points": 1380, "continent": "아시아", "primary_color": "#FF0000", "secondary_color": "#007A3D", "manager": "자말 셀라미", "names": ["무사 알 타마리", "야잔 알 나이마트", "알리 올완", "니자르 알 라쉬단", "누르 알 라와브데", "마하무드 알 마르디", "에산 하다드", "야잔 알 아랍", "압달라 나시브", "살렘 알 아잘린", "야제드 아부라일라"]},
    "NOR": {"name": "노르웨이", "rank": 47, "points": 1470, "continent": "유럽", "primary_color": "#EF2B2D", "secondary_color": "#00205B", "manager": "스톨레 솔바켄", "lineup_override": [
        {"name": "외리얀 륄란", "pos": "GK"},
        {"name": "율리안 뤼에르손", "pos": "DF"},
        {"name": "크리스토페르 아예르", "pos": "DF"},
        {"name": "레오 외스티고르", "pos": "DF"},
        {"name": "안드레아스 한체올센", "pos": "DF"},
        {"name": "마틴 외데고르", "pos": "MF"},
        {"name": "산데르 베르게", "pos": "MF"},
        {"name": "안토니오 누사", "pos": "MF"},
        {"name": "엘링 홀란", "pos": "FW"},
        {"name": "알렉산더 쇠를로트", "pos": "FW"},
        {"name": "요르겐 라센", "pos": "FW"}
    ], "subs": ["셀비크", "올센", "페데르센", "토르스트베트", "도눔", "에울네스", "벨데"]},
    "SCO": {"name": "스코틀랜드", "rank": 52, "points": 1440, "continent": "유럽", "primary_color": "#002B5C", "secondary_color": "#FFFFFF", "manager": "스티브 클라크", "names": ["스콧 맥토미니", "앤드류 로버트슨", "존 맥긴", "빌리 길모어", "체 애덤스", "라이언 크리스티", "키어런 트리피어", "칼럼 맥그리거", "존 수타", "그랜트 한리", "앵거스 건"]},
    "GRE": {"name": "그리스", "rank": 54, "points": 1430, "continent": "유럽", "primary_color": "#0D5EAF", "secondary_color": "#FFFFFF", "manager": "이반 요바노비치", "names": ["포티스 이오아니디스", "방겔리스 파블리디스", "아나스타시오스 바카세타스", "디미트리오스 펠카스", "요르고스 마수라스", "페트로스 만탈로스", "콘스타티노스 치미카스", "콘스타티노스 마브로파노스", "판텔리스 하치디아코스", "라자로스 로타", "오디세아스 블라호디모스"]},
    "BOL": {"name": "볼리비아", "rank": 89, "points": 1260, "continent": "남미", "primary_color": "#007A33", "secondary_color": "#FFFF00", "manager": "오스카 비예가스", "names": ["카르멜로 알가라냐스", "라미로 바카", "미겔 테르세로스", "보리스 세스페데스", "롭손 마테우스", "디에고 메디나", "루이스 하킨", "호세 사그레도", "마르셀로 수아레스", "로베르토 페르난데스", "카를로스 람페"]},
    "VEN": {"name": "베네수엘라", "rank": 40, "points": 1500, "continent": "남미", "primary_color": "#7B162C", "secondary_color": "#FFFFFF", "manager": "페르난도 바티스타", "names": ["살로몬 론돈", "예페르손 소텔도", "제퍼슨 사바리노", "크리스티안 카세레스", "호세 마르티네스", "앙헬 에레라", "존 아람부루", "나우엘 페라레시", "요르단 오소리오", "미겔 나바르토", "라파엘 로모"]},
    "PRY": {"name": "파라과이", "rank": 64, "points": 1410, "continent": "남미", "primary_color": "#D2143A", "secondary_color": "#FFFFFF", "manager": "구스타보 알파로", "names": ["안토니오 사나브리아", "미겔 알미론", "훌리오 엔시소", "마티아스 비야산티", "디에고 고메스", "다미안 보바디야", "구스타보 고메스", "오마르 알데레테", "주니어 알론소", "구스타보 벨라스케스", "로베르토 페르난데스"]},
    "RSA": {"name": "남아프리카 공화국", "rank": 59, "points": 1435, "continent": "아프리카", "primary_color": "#007A4B", "secondary_color": "#FFB612", "manager": "위구 브로스", "names": ["퍼시 타우", "템바 즈와네", "테보호 모코에나", "오브리 모디바", "탈렌테 음바타", "스펠렐레 음키제", "모토비 음발라", "그랜트 케카나", "쿨리소 무다우", "툴라니 흘라츠와요", "론웬 윌리엄스"]},
    "SMR": {"name": "산마리노", "rank": 210, "points": 740, "continent": "유럽", "primary_color": "#5B92E5", "secondary_color": "#FFFFFF", "manager": "로베르토 체볼리", "names": ["필리포 나타니", "니코 센솔리", "마테오 비타이올리", "로렌초 라자리", "알레산드로 골리누치", "로렌초 카피키오니", "안드레아 그란도니", "필리포 파브리", "단테 로시", "미켈레 체볼리", "에도아르도 콜롬보"]}
}

ADDITIONAL_CLUBS = {
    "MIA": {"name": "인터 마이애미", "points": 1520, "primary_color": "#F7B5CD", "secondary_color": "#000000", "manager": "헤라르도 마르티노", "lineup_override": [
        {"name": "드레이크 캘린더", "pos": "GK"},
        {"name": "조르디 알바", "pos": "DF"},
        {"name": "토마스 아빌레스", "pos": "DF"},
        {"name": "세르게이 크리브초프", "pos": "DF"},
        {"name": "마르셀로 위간트", "pos": "DF"},
        {"name": "세르히오 부스케츠", "pos": "MF"},
        {"name": "페데리코 레돈도", "pos": "MF"},
        {"name": "율리안 그레셀", "pos": "MF"},
        {"name": "리오넬 메시", "pos": "FW"},
        {"name": "루이스 수아레스", "pos": "FW"},
        {"name": "로버트 테일러", "pos": "FW"}
    ], "subs": ["도스 산토스", "프레이레", "네그리", "루이즈", "크레마스키", "캄파나", "고메즈"]},
    
    "NAS": {"name": "알 나스르", "points": 1490, "primary_color": "#FFF200", "secondary_color": "#005CA9", "manager": "스테파노 피올리", "lineup_override": [
        {"name": "벤토", "pos": "GK"},
        {"name": "알렉스 텔레스", "pos": "DF"},
        {"name": "아이메릭 라포르트", "pos": "DF"},
        {"name": "알리 라자미", "pos": "DF"},
        {"name": "술탄 알 가남", "pos": "DF"},
        {"name": "마르셀로 브로조비치", "pos": "MF"},
        {"name": "압둘라 알 카이바리", "pos": "MF"},
        {"name": "오타비우", "pos": "MF"},
        {"name": "사디오 마네", "pos": "FW"},
        {"name": "크리스티아누 호날두", "pos": "FW"},
        {"name": "앤더슨 탈리스카", "pos": "FW"}
    ], "subs": ["알 아키디", "알 파틸", "부샬", "알 나지", "알 하산", "가립", "마란"]},
    
    "HIL": {"name": "알 힐랄", "points": 1530, "primary_color": "#004B87", "secondary_color": "#FFFFFF", "manager": "조르제 제수스", "lineup_override": [
        {"name": "야신 부누", "pos": "GK"},
        {"name": "야세르 알 샤흐라니", "pos": "DF"},
        {"name": "칼리두 쿨리발리", "pos": "DF"},
        {"name": "알리 알 불라이히", "pos": "DF"},
        {"name": "사우드 압둘하미드", "pos": "DF"},
        {"name": "후벵 네베스", "pos": "MF"},
        {"name": "세르게이 밀린코비치-사비치", "pos": "MF"},
        {"name": "말콤", "pos": "MF"},
        {"name": "네이마르", "pos": "FW"},
        {"name": "알렉산다르 미트로비치", "pos": "FW"},
        {"name": "살레 알 셰흐리", "pos": "FW"}
    ], "subs": ["알 오와이스", "탐바크티", "알 도사리", "칸노", "알 파라지", "미샤엘", "알 햄단"]},

    "ULS": {"name": "울산 HD", "points": 1410, "primary_color": "#002F6C", "secondary_color": "#FFC72C", "manager": "김판곤", "lineup_override": [
        {"name": "조현우", "pos": "GK"},
        {"name": "이명재", "pos": "DF"},
        {"name": "김영권", "pos": "DF"},
        {"name": "임종은", "pos": "DF"},
        {"name": "설영우", "pos": "DF"},
        {"name": "원두재", "pos": "MF"},
        {"name": "고승범", "pos": "MF"},
        {"name": "이규성", "pos": "MF"},
        {"name": "루빅손", "pos": "FW"},
        {"name": "주민규", "pos": "FW"},
        {"name": "아타루", "pos": "FW"}
    ], "subs": ["조수혁", "황석호", "장시영", "보야니치", "이청용", "김민우", "엄원상"]},
    
    "SEO": {"name": "FC 서울", "points": 1390, "primary_color": "#E50012", "secondary_color": "#000000", "manager": "김기동", "lineup_override": [
        {"name": "백종범", "pos": "GK"},
        {"name": "강상우", "pos": "DF"},
        {"name": "권완규", "pos": "DF"},
        {"name": "김주성", "pos": "DF"},
        {"name": "최준", "pos": "DF"},
        {"name": "기성용", "pos": "MF"},
        {"name": "류재문", "pos": "MF"},
        {"name": "제시 린가드", "pos": "MF"},
        {"name": "조영욱", "pos": "FW"},
        {"name": "일류첸코", "pos": "FW"},
        {"name": "임상협", "pos": "FW"}
    ], "subs": ["최철원", "윤종규", "박성훈", "팔로세비치", "조지훈", "한승규", "강성진"]},
    
    "JEO": {"name": "전북 현대", "points": 1380, "primary_color": "#007A3E", "secondary_color": "#C4D600", "manager": "김두현", "lineup_override": [
        {"name": "김정훈", "pos": "GK"},
        {"name": "김진수", "pos": "DF"},
        {"name": "박진섭", "pos": "DF"},
        {"name": "홍정호", "pos": "DF"},
        {"name": "안현범", "pos": "DF"},
        {"name": "이수빈", "pos": "MF"},
        {"name": "보아텡", "pos": "MF"},
        {"name": "이영재", "pos": "MF"},
        {"name": "송민규", "pos": "FW"},
        {"name": "티아고", "pos": "FW"},
        {"name": "에르난데스", "pos": "FW"}
    ], "subs": ["정민기", "구자룡", "정우재", "이학민", "맹성웅", "한교원", "박재용"]},

    "AJA": {"name": "AFC 아약스", "points": 1450, "primary_color": "#FFFFFF", "secondary_color": "#D1001C", "manager": "프란체스코 파리올리", "names": ["브라이언 브로비", "스티븐 베르흐베인", "조던 헨더슨", "케네스 테일러", "요시프 슈탈로", "데바인 렌쉬", "디안 라마이", "추바 악폼", "미카 고츠", "카플란", "루이"]},
    "BOC": {"name": "보카 주니어스", "points": 1430, "primary_color": "#003A70", "secondary_color": "#FEE600", "manager": "디에고 마르티네스", "names": ["에딘손 카바니", "미겔 메렌티엘", "케빈 제논", "루이스 아드빈쿨라", "마르코스 로호", "크리스티안 메디나", "폴 페르난데스", "레마", "블론델", "사라치", "세르히오 로메로"]},
    "RIV": {"name": "리버 플레이트", "points": 1440, "primary_color": "#FFFFFF", "secondary_color": "#FF0000", "manager": "마르셀로 가야르도", "names": ["미겔 보르하", "파쿤도 콜리디오", "마누엘 란시니", "마르코스 아쿠냐", "헤르만 페셀라", "클라우디오 에체베리", "로치고 아리엔드로", "크라네비테르", "산타나", "파울로 디아스", "프랑코 아르마니"]}
}

def generate_standard_lineup(team_name, is_national=True, names=None, overrides=None):
    if overrides:
        lineup = []
        for i, ply in enumerate(overrides):
            pos = ply["pos"]
            if pos == "GK":
                x, y = 50, 10
            elif pos == "DF":
                x = 15 + (i - 1) * 23 if i < 5 else 50
                y = 30
            elif pos == "MF":
                x = 30 + (i - 5) * 20 if i < 8 else 50
                y = 50
            else:
                x = 20 + (i - 8) * 30 if i < 11 else 50
                y = 80
            lineup.append({"name": ply["name"], "pos": pos, "x": x, "y": y})
        return lineup

    if not names:
        names = [f"선수 {i+1}" for i in range(18)]
    
    lineup = []
    positions = ["GK", "DF", "DF", "DF", "DF", "MF", "MF", "MF", "FW", "FW", "FW"]
    x_coords = [
        50,
        85, 62, 38, 15,
        70, 50, 30,
        80, 50, 20
    ]
    y_coords = [
        10,
        30, 25, 25, 30,
        50, 45, 50,
        80, 85, 80
    ]
    
    for idx, pos in enumerate(positions):
        name_val = names[idx] if idx < len(names) else f"{pos} {idx}"
        lineup.append({
            "name": name_val,
            "pos": pos,
            "x": x_coords[idx],
            "y": y_coords[idx]
        })
    return lineup

def build_all_nations():
    res = BASE_TEAMS.copy()
    for code, info in ADDITIONAL_NATIONS.items():
        if code not in res:
            res[code] = {
                "name": info["name"],
                "rank": info["rank"],
                "points": info["points"],
                "continent": info["continent"],
                "primary_color": info["primary_color"],
                "secondary_color": info["secondary_color"],
                "manager": info["manager"],
                "lineup": generate_standard_lineup(info["name"], True, info.get("names"), info.get("lineup_override")),
                "subs": info.get("subs", [f"교체 {i+1}" for i in range(7)])
            }
    return res

def build_all_clubs():
    res = BASE_CL_TEAMS.copy()
    for code, info in ADDITIONAL_CLUBS.items():
        if code not in res:
            res[code] = {
                "name": info["name"],
                "rank": info.get("rank", 999),
                "points": info["points"],
                "primary_color": info["primary_color"],
                "secondary_color": info["secondary_color"],
                "manager": info["manager"],
                "lineup": generate_standard_lineup(info["name"], False, info.get("names"), info.get("lineup_override")),
                "subs": info.get("subs", [f"교체 {i+1}" for i in range(7)])
            }
    return res

ALL_TEAMS = build_all_nations()
ALL_CL_TEAMS = build_all_clubs()
