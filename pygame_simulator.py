# -*- coding: utf-8 -*-
import pygame
import math
import random
import os
import sys

# team_generator에서 팀 데이터 로드
try:
    from team_generator import ALL_TEAMS as TEAMS
except ImportError:
    # 예외 상황 시 더미 데이터셋 생성
    TEAMS = {
        "KOR": {
            "name": "대한민국",
            "primary_color": "#ef4444",
            "secondary_color": "#ffffff",
            "lineup": [
                {"name": "조현우", "pos": "GK"},
                {"name": "설영우", "pos": "DF"},
                {"name": "김민재", "pos": "DF"},
                {"name": "김영권", "pos": "DF"},
                {"name": "김진수", "pos": "DF"},
                {"name": "황인범", "pos": "MF"},
                {"name": "이재성", "pos": "MF"},
                {"name": "이강인", "pos": "MF"},
                {"name": "황희찬", "pos": "FW"},
                {"name": "조규성", "pos": "FW"},
                {"name": "손흥민", "pos": "FW"}
            ],
            "points": 1620
        },
        "BRA": {
            "name": "브라질",
            "primary_color": "#facc15",
            "secondary_color": "#000000",
            "lineup": [
                {"name": "알리송", "pos": "GK"},
                {"name": "다닐루", "pos": "DF"},
                {"name": "마르키뉴스", "pos": "DF"},
                {"name": "에데르 밀리탕", "pos": "DF"},
                {"name": "완데르송", "pos": "DF"},
                {"name": "기마랑이스", "pos": "MF"},
                {"name": "루카스 파케타", "pos": "MF"},
                {"name": "네이마르", "pos": "MF"},
                {"name": "호드리구", "pos": "FW"},
                {"name": "히샤를리송", "pos": "FW"},
                {"name": "비니시우스 Jr.", "pos": "FW"}
            ],
            "points": 1780
        }
    }

# 초기화
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1100, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("FC 온라인 2D 감독모드 Pygame 시뮬레이터")
clock = pygame.time.Clock()

# 폰트
font_name = pygame.font.match_font('malgungothic') or pygame.font.match_font('applesdgothicneo') or pygame.font.get_default_font()
FONT_S = pygame.font.Font(font_name, 14)
FONT_M = pygame.font.Font(font_name, 18)
FONT_L = pygame.font.Font(font_name, 24)
FONT_XL = pygame.font.Font(font_name, 36)

# 색상 정의
GREEN_DARK = (20, 66, 29)
GREEN_LIGHT = (16, 54, 23)
WHITE = (255, 255, 255)
CYAN = (0, 242, 254)
GOLD = (250, 204, 21)
RED = (239, 68, 68)
BLUE = (59, 130, 246)
DARK_NAVY = (11, 15, 25)
GRAY = (148, 163, 184)

# 포메이션 좌표 비율 (GK, DF x 4, MF x 3, FW x 3)
FORMATIONS = {
    "4-3-3": [
        (0.08, 0.50, "GK"),
        (0.32, 0.15, "DF"), (0.28, 0.38, "DF"), (0.28, 0.62, "DF"), (0.32, 0.85, "DF"),
        (0.55, 0.50, "MF"), (0.58, 0.25, "MF"), (0.58, 0.75, "MF"),
        (0.82, 0.20, "FW"), (0.85, 0.50, "FW"), (0.82, 0.80, "FW")
    ],
    "4-4-2": [
        (0.08, 0.50, "GK"),
        (0.32, 0.15, "DF"), (0.28, 0.38, "DF"), (0.28, 0.62, "DF"), (0.32, 0.85, "DF"),
        (0.55, 0.18, "MF"), (0.52, 0.38, "MF"), (0.52, 0.62, "MF"), (0.55, 0.82, "MF"),
        (0.82, 0.35, "FW"), (0.82, 0.65, "FW")
    ]
}

# 전술 설정 클래스
class Tactics:
    def __init__(self, speed=60, pass_risk=50, pressure=60, aggression=50):
        self.speed = speed
        self.pass_risk = pass_risk
        self.pressure = pressure
        self.aggression = aggression

# 선수 클래스
class Player:
    def __init__(self, name, team, role, stats, home_x, home_y, color, text_color):
        self.name = name
        self.team = team  # 'home' or 'away'
        self.role = role  # 'GK', 'DF', 'MF', 'FW'
        self.stats = stats # {'speed': 80, 'passing': 80, 'defense': 80}
        self.home_x = home_x
        self.home_y = home_y
        self.x = home_x
        self.y = home_y
        self.vx = 0
        self.vy = 0
        self.stamina = 100.0
        self.color = color
        self.text_color = text_color
        self.card = None  # 'yellow', 'red'
        self.perf = {"goals": 0, "passes": 0, "tackles": 0, "saves": 0, "shots": 0}

    def move_towards(self, target_x, target_y, speed_factor, dt):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 2:
            # 체력 비례 속도 페널티
            stamina_penalty = 0.7 if self.stamina < 40 else 1.0
            move_speed = speed_factor * dt * 60 * stamina_penalty
            self.x += (dx / dist) * min(dist, move_speed)
            self.y += (dy / dist) * min(dist, move_speed)

# 공 클래스
class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.owner = None

    def update(self):
        if self.owner:
            self.x = self.owner.x
            self.y = self.owner.y
        else:
            self.x += self.vx
            self.y += self.vy
            self.vx *= 0.94
            self.vy *= 0.94

# 비프음 사운드 생성기
def play_sound(freq, duration):
    try:
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = bytes([int(127 + 127 * math.sin(2 * math.pi * freq * i / sample_rate)) for i in range(n_samples)])
        sound = pygame.mixer.Sound(buffer=buf)
        sound.play()
    except Exception:
        pass

# 경기 시뮬레이터 메인 클래스
class ManagerSimulator:
    def __init__(self):
        self.home_code = "KOR"
        self.away_code = "BRA"
        
        self.tactics_home = Tactics(speed=70, pass_risk=65, pressure=60, aggression=55)
        self.tactics_away = Tactics(speed=60, pass_risk=50, pressure=65, aggression=60)
        
        self.score_home = 0
        self.score_away = 0
        self.match_time = 0.0
        self.is_playing = False
        self.sim_speed = 1
        
        self.ball = Ball(400, 300)
        self.players = []
        self.logs = []
        self.float_texts = []
        self.pass_lock_timer = 0
        self.pass_line = None
        self.kickoff_team = "home"
        
        self.init_squads()

    def init_squads(self):
        self.players = []
        self.ball.owner = None
        self.pass_line = None
        
        home_team_info = TEAMS.get(self.home_code)
        away_team_info = TEAMS.get(self.away_code)
        
        # 포메이션에 맞춰 좌표 할당
        home_coords = FORMATIONS["4-3-3"]
        away_coords = FORMATIONS["4-3-3"]
        
        # 홈팀 배치 (왼쪽 -> 오른쪽 공격)
        for idx, player_info in enumerate(home_team_info["lineup"]):
            rel = home_coords[idx]
            x = 30 + rel[0] * 350
            y = 50 + rel[1] * 400
            
            # 능력치 배정
            stats = {"speed": random.randint(70, 92), "passing": random.randint(70, 90), "defense": random.randint(68, 92)}
            self.players.append(Player(
                name=player_info["name"],
                team="home",
                role=rel[2],
                stats=stats,
                home_x=x,
                home_y=y,
                color=BLUE,
                text_color=WHITE
            ))
            
        # 어웨이팀 배치 (오른쪽 -> 왼쪽 공격)
        for idx, player_info in enumerate(away_team_info["lineup"]):
            rel = away_coords[idx]
            x = 770 - rel[0] * 350
            y = 50 + rel[1] * 400
            
            stats = {"speed": random.randint(72, 95), "passing": random.randint(70, 92), "defense": random.randint(70, 94)}
            self.players.append(Player(
                name=player_info["name"],
                team="away",
                role=rel[2],
                stats=stats,
                home_x=x,
                home_y=y,
                color=RED,
                text_color=WHITE
            ))
            
        self.setup_kickoff()

    def setup_kickoff(self):
        for p in self.players:
            p.x = p.home_x
            p.y = p.home_y
            
        if self.kickoff_team == "home":
            st = [p for p in self.players if p.team == "home" and p.role == "FW"][0]
            st.x, st.y = 390, 250
            self.ball.x, self.ball.y = 400, 250
            self.ball.owner = st
        else:
            st = [p for p in self.players if p.team == "away" and p.role == "FW"][0]
            st.x, st.y = 410, 250
            self.ball.x, self.ball.y = 400, 250
            self.ball.owner = st
            
        self.ball.vx, self.ball.vy = 0, 0

    def trigger_float_text(self, text, x, y, color):
        self.float_texts.append({"text": text, "x": x, "y": y, "color": color, "life": 1.0})

    def add_log(self, text):
        mins = int(self.match_time)
        secs = int((self.match_time % 1) * 60)
        time_str = f"[{mins:02d}:{secs:02d}]"
        self.logs.append(f"{time_str} {text}")
        if len(self.logs) > 15:
            self.logs.pop(0)

    def attempt_pass(self, passer):
        teammates = [p for p in self.players if p.team == passer.team and p != passer and p.role != "GK" and p.card != "red"]
        if not teammates:
            return
            
        # 패스 대상 선정 (상대 가로채기가 적고 전술 패스 거리에 적합한 동료)
        best_target = None
        best_score = -9999
        
        for tm in teammates:
            dx = tm.x - passer.x
            dy = tm.y - passer.y
            dist = math.hypot(dx, dy)
            if dist < 40 or dist > 250:
                continue
                
            # 가로채기 경로 점검 (패스 궤적 근처의 상대 수비수 밀집도 계산)
            opp_count = 0
            for opp in self.players:
                if opp.team != passer.team and opp.card != "red":
                    # 점과 직선 사이의 거리 공식 활용
                    # 패스 궤적 근처 30px 이내에 수비수가 있을 시 가로채기 확률 대입
                    cross = abs((tm.y - passer.y) * opp.x - (tm.x - passer.x) * opp.y + tm.x * passer.y - tm.y * passer.x)
                    line_len = math.hypot(tm.x - passer.x, tm.y - passer.y)
                    if line_len > 0 and (cross / line_len) < 25:
                        opp_count += 1
                        
            score = 100 - dist * 0.1 - opp_count * 40
            if score > best_score:
                best_score = score
                best_target = tm
                
        if best_target:
            dx = best_target.x - passer.x
            dy = best_target.y - passer.y
            dist = math.hypot(dx, dy)
            
            # 패스 정확도 연산 (체력 비례 적용)
            pass_success_rate = 0.65 + (passer.stats["passing"] / 300)
            if passer.stamina < 40:
                pass_success_rate -= 0.15
                
            self.ball.owner = None
            self.pass_lock_timer = 0.4
            
            if random.random() < pass_success_rate:
                self.ball.vx = (dx / dist) * 9
                self.ball.vy = (dy / dist) * 9
                self.pass_line = ((passer.x, passer.y), (best_target.x, best_target.y))
                passer.perf["passes"] += 1
                play_sound(800, 0.05)
            else:
                # 패스 미스 (궤적 살짝 어긋남)
                angle = math.atan2(dy, dx) + random.uniform(-0.4, 0.4)
                self.ball.vx = math.cos(angle) * 7
                self.ball.vy = math.sin(angle) * 7
                self.add_log(f"{passer.name}의 전술 패스가 아쉽게 차단당하며 루즈볼이 흐릅니다.")
                play_sound(400, 0.08)

    def attempt_shot(self, shooter):
        opp_gk = [p for p in self.players if p.team != shooter.team and p.role == "GK"][0]
        self.ball.owner = None
        self.ball.vx, self.ball.vy = 0, 0
        
        goal_x = 800 if shooter.team == "home" else 0
        goal_y = 250
        
        dx = goal_x - shooter.x
        dy = goal_y - shooter.y
        dist = math.hypot(dx, dy)
        
        # 슛 성공 확률
        gk_def = opp_gk.stats["defense"] if opp_gk else 75
        save_chance = 0.45 + (gk_def / 280) - (shooter.stats["speed"] / 400)
        
        if random.random() < save_chance:
            # 골키퍼 선방
            self.ball.x, self.ball.y = opp_gk.x, opp_gk.y
            self.ball.vx = random.choice([-5, 5])
            self.ball.vy = -6
            self.add_log(f"🧤 {opp_gk.name} 골키퍼의 환상적인 반사 신경 선방!!!")
            self.trigger_float_text("SAVE! 🧤", opp_gk.x, opp_gk.y - 20, CYAN)
            opp_gk.perf["saves"] += 1
            play_sound(900, 0.12)
        else:
            # 득점성공
            if shooter.team == "home":
                self.score_home += 1
                self.kickoff_team = "away"
            else:
                self.score_away += 1
                self.kickoff_team = "home"
                
            shooter.perf["goals"] += 1
            self.add_log(f"⚽ 득점 성공!!! {shooter.name}의 명품 슈팅이 골망을 가릅니다!")
            self.trigger_float_text("GOAL!!! ⚽", 400, 250, GOLD)
            play_sound(1200, 0.3)
            self.setup_kickoff()

    def update_physics(self, dt):
        if self.pass_lock_timer > 0:
            self.pass_lock_timer -= dt

        # 전술 계수 로드
        tactics_h = self.tactics_home
        tactics_a = self.tactics_away

        # 공 물리 갱신
        self.ball.update()

        # 루즈볼 확보 처리
        if not self.ball.owner and self.pass_lock_timer <= 0:
            for p in self.players:
                if p.card == "red":
                    continue
                dist = math.hypot(self.ball.x - p.x, self.ball.y - p.y)
                if dist < 12:
                    self.ball.owner = p
                    self.ball.vx = 0
                    self.ball.vy = 0
                    play_sound(700, 0.04)
                    break

        # 볼 소유자 공격 처리
        if self.ball.owner:
            owner = self.ball.owner
            tact = tactics_h if owner.team == "home" else tactics_a
            
            goal_x = 800 if owner.team == "home" else 0
            goal_y = 250
            
            # 드리블 진행 방향
            steer_x = goal_x - owner.x
            steer_y = goal_y - owner.y
            dist = math.hypot(steer_x, steer_y)
            if dist > 0:
                steer_x /= dist
                steer_y /= dist
                
            # 드리블 조향 속도
            dribble_speed = 2.2 + (owner.stats["speed"] / 45) + (tact.speed / 100)
            owner.x += steer_x * dribble_speed * dt * 60
            owner.y += steer_y * dribble_speed * dt * 60
            
            # 수비수 대인 압박 & 맨투맨 마킹 매칭
            closest_def = None
            min_def_dist = 9999
            for p in self.players:
                if p.team != owner.team and p.role != "GK" and p.card != "red":
                    d = math.hypot(owner.x - p.x, owner.y - p.y)
                    if d < min_def_dist:
                        min_def_dist = d
                        closest_def = p
                        
            if closest_def:
                # 맨투맨 타겟 마킹
                dx = owner.x - closest_def.x
                dy = owner.y - closest_def.y
                if min_def_dist > 0.1:
                    press_speed = 2.0 + (closest_def.stats["speed"] / 50) + (tact.pressure / 100)
                    closest_def.x += (dx / min_def_dist) * press_speed * dt * 60
                    closest_def.y += (dy / min_def_dist) * press_speed * dt * 60
                    
                # 대인 태클 판정
                if min_def_dist < 9 and self.pass_lock_timer <= 0:
                    tackle_chance = 0.12 + (closest_def.stats["defense"] / 200) + (tact.aggression / 400)
                    if random.random() < tackle_chance:
                        self.ball.owner = closest_def
                        closest_def.perf["tackles"] += 1
                        self.pass_lock_timer = 0.4
                        self.add_log(f"{closest_def.name}의 강력한 정면 차단 태클 성공!")
                        play_sound(500, 0.05)
                        
            # 슈팅 및 패스 판단
            in_shoot_area = (owner.team == "home" and owner.x > 670) or (owner.team == "away" and owner.x < 130)
            if in_shoot_area:
                if random.random() < 0.12:
                    self.attempt_shot(owner)
            else:
                pass_chance = 0.04 + (tact.pass_risk / 1100)
                if random.random() < pass_chance:
                    self.attempt_pass(owner)

        # 5. 공이 없는 선수들의 움직임 (맨투맨 마킹 및 루즈볼 추적)
        closest_home = None
        closest_away = None
        min_home = 9999
        min_away = 9999
        
        if not self.ball.owner:
            for p in self.players:
                if p.role == "GK" or p.card == "red":
                    continue
                d = math.hypot(self.ball.x - p.x, self.ball.y - p.y)
                if p.team == "home":
                    if d < min_home:
                        min_home = d
                        closest_home = p
                else:
                    if d < min_away:
                        min_away = d
                        closest_away = p

        for p in self.players:
            if p == self.ball.owner or p.card == "red":
                continue
                
            # 골키퍼
            if p.role == "GK":
                dy = self.ball.y - p.y
                gk_speed = 18 * dt * 60
                p.y += math.copysign(min(abs(dy), gk_speed), dy)
                p.y = max(190, min(310, p.y))
                continue
                
            target_x, target_y = p.home_x, p.home_y
            chase_mode = False
            
            # 루즈볼 추적
            if not self.ball.owner:
                if p == closest_home or p == closest_away:
                    target_x = self.ball.x
                    target_y = self.ball.y
                    chase_mode = True
                else:
                    target_x = p.home_x * 0.55 + self.ball.x * 0.45
                    target_y = p.home_y * 0.55 + self.ball.y * 0.45
            # 수비 마킹
            elif self.ball.owner.team != p.team:
                mark_target = None
                min_m = 9999
                for opp in self.players:
                    if opp.team != p.team and opp.role != "GK" and opp.card != "red":
                        d = math.hypot(opp.x - p.x, opp.y - p.y)
                        if d < min_m:
                            min_m = d
                            mark_target = opp
                if mark_target:
                    goal_x = 15 if p.team == "home" else 785
                    dir_x = goal_x - mark_target.x
                    dir_y = 250 - mark_target.y
                    dist_to_gk = math.hypot(dir_x, dir_y)
                    if dist_to_gk > 0:
                        target_x = mark_target.x + (dir_x / dist_to_gk) * 18
                        target_y = mark_target.y + (dir_y / dist_to_gk) * 18
            # 공격 시 오버랩
            else:
                ball_progress = self.ball.x / 800
                shift = ball_progress * 150 if p.team == "home" else (1 - ball_progress) * 150
                target_x = p.home_x + (shift if p.team == "home" else -shift)
                
            dx = target_x - p.x
            dy = target_y - p.y
            dist = math.hypot(dx, dy)
            if dist > 4:
                speed_factor = 3.5 if chase_mode else 2.3
                p.move_towards(target_x, target_y, speed_factor, dt)
                
        # 선수 겹침 충돌 방지
        for i in range(len(self.players)):
            for j in range(i+1, len(self.players)):
                p1 = self.players[i]
                p2 = self.players[j]
                if p1.role == "GK" or p2.role == "GK" or p1.card == "red" or p2.card == "red":
                    continue
                d = math.hypot(p2.x - p1.x, p2.y - p1.y)
                if d < 14:
                    overlap = 14 - d
                    dx = (p2.x - p1.x) / d if d > 0 else 1
                    dy = (p2.y - p1.y) / d if d > 0 else 0
                    p1.x -= dx * overlap * 0.5
                    p1.y -= dy * overlap * 0.5
                    p2.x += dx * overlap * 0.5
                    p2.y += dy * overlap * 0.5

        # 경기장 경계 탈출 방지
        for p in self.players:
            p.x = max(18, min(782, p.x))
            p.y = max(18, min(482, p.y))
            
        self.ball.x = max(15, min(785, self.ball.x))
        self.ball.y = max(15, min(485, self.ball.y))

    def draw(self):
        # 1. 2D 경기장 그리기 (왼쪽 800 x 500 영역)
        pitch_rect = pygame.Rect(0, 0, 800, 500)
        pygame.draw.rect(screen, GREEN_DARK, pitch_rect)
        
        # 잔디 스트라이프 효과
        for i in range(0, 800, 64):
            if (i // 64) % 2 == 0:
                pygame.draw.rect(screen, GREEN_LIGHT, (i, 0, 32, 500))
                
        # 터치라인
        pygame.draw.rect(screen, WHITE, (15, 15, 770, 470), 2)
        pygame.draw.line(screen, WHITE, (400, 15), (400, 485), 2)
        pygame.draw.circle(screen, WHITE, (400, 250), 50, 2)
        
        # 페널티 영역
        pygame.draw.rect(screen, WHITE, (15, 110, 80, 280), 2)
        pygame.draw.rect(screen, WHITE, (705, 110, 80, 280), 2)
        
        # 골대 그리기
        pygame.draw.rect(screen, WHITE, (5, 190, 10, 120), 2)
        pygame.draw.rect(screen, WHITE, (785, 190, 10, 120), 2)

        # 패스 라인 그리기
        if self.pass_line:
            pygame.draw.line(screen, CYAN, self.pass_line[0], self.pass_line[1], 2)
            self.pass_line = None  # 1프레임 노출 후 삭제

        # 선수 렌더링
        for p in self.players:
            if p.card == "red":
                continue
                
            # 볼 소유 오라
            if self.ball.owner == p:
                pygame.draw.circle(screen, (0, 242, 254, 80), (int(p.x), int(p.y)), 15)
                
            # 기본 원
            pygame.draw.circle(screen, p.color, (int(p.x), int(p.y)), 9)
            pygame.draw.circle(screen, WHITE, (int(p.x), int(p.y)), 9, 1)
            
            # 선수 성명 표기
            lbl = FONT_S.render(p.name, True, WHITE)
            screen.blit(lbl, (int(p.x) - lbl.get_width()//2, int(p.y) - 22))

        # 공 그리기
        pygame.draw.circle(screen, BLACK, (int(self.ball.x)+2, int(self.ball.y)+2), 5)
        pygame.draw.circle(screen, WHITE, (int(self.ball.x), int(self.ball.y)), 5)
        pygame.draw.circle(screen, BLACK, (int(self.ball.x), int(self.ball.y)), 5, 1)

        # 플로팅 경고/알림 텍스트
        for ft in self.float_texts[:]:
            txt = FONT_L.render(ft["text"], True, ft["color"])
            screen.blit(txt, (int(ft["x"]) - txt.get_width()//2, int(ft["y"])))
            ft["y"] -= 0.5
            ft["life"] -= 0.02
            if ft["life"] <= 0:
                self.float_texts.remove(ft)

        # 2. 우측 전술 컨트롤 패널 & 문자 중계 영역 (300px)
        ui_rect = pygame.Rect(800, 0, 300, 700)
        pygame.draw.rect(screen, DARK_NAVY, ui_rect)
        pygame.draw.line(screen, GRAY, (800, 0), (800, 700), 2)
        
        # 전술 타이틀
        title = FONT_L.render("📋 실시간 전술 지시", True, CYAN)
        screen.blit(title, (820, 20))
        
        # 슬라이더 정보 렌더링
        y_offset = 65
        sliders = [
            ("⚡ 속도 (Speed)", self.tactics_home.speed),
            ("📐 패스 모험도 (Pass Risk)", self.tactics_home.pass_risk),
            ("🛡️ 압박 (Pressure)", self.tactics_home.pressure),
            ("⚔️ 수비 격렬성 (Aggr)", self.tactics_home.aggression),
        ]
        
        for name, val in sliders:
            lbl = FONT_S.render(name, True, WHITE)
            screen.blit(lbl, (820, y_offset))
            val_lbl = FONT_S.render(str(val), True, GOLD)
            screen.blit(val_lbl, (1030, y_offset))
            
            # 슬라이더 선 및 노드 그리기
            pygame.draw.line(screen, GRAY, (820, y_offset + 22), (1050, y_offset + 22), 3)
            node_x = 820 + (val / 100) * 230
            pygame.draw.circle(screen, CYAN, (int(node_x), y_offset + 22), 6)
            y_offset += 45

        # 문자 중계 영역 타이틀
        log_title = FONT_L.render("✍️ 매치 주요 문자중계", True, GOLD)
        screen.blit(log_title, (820, 260))
        
        # 중계 로그 목록 표기
        log_y = 300
        for l in self.logs:
            log_lbl = FONT_S.render(l, True, WHITE)
            screen.blit(log_lbl, (820, log_y))
            log_y += 20

        # 3. 하단 실시간 스코어 HUD 보드
        bottom_rect = pygame.Rect(0, 500, 800, 200)
        pygame.draw.rect(screen, DARK_NAVY, bottom_rect)
        pygame.draw.line(screen, GRAY, (0, 500), (800, 500), 2)
        
        # 스코어 및 시간
        score_lbl = FONT_XL.render(f"{self.score_home} - {self.score_away}", True, GOLD)
        screen.blit(score_lbl, (360, 530))
        
        mins = int(self.match_time)
        secs = int((self.match_time % 1) * 60)
        time_lbl = FONT_M.render(f"진행 시간: {mins:02d}:{secs:02d} | 2배속", True, WHITE)
        screen.blit(time_lbl, (330, 580))
        
        # 팀명 명단
        h_name = FONT_L.render(TEAMS[self.home_code]["name"], True, BLUE)
        a_name = FONT_L.render(TEAMS[self.away_code]["name"], True, RED)
        screen.blit(h_name, (230, 530))
        screen.blit(a_name, (510, 530))
        
        # 조작 단축키 매뉴얼
        manual_lbl1 = FONT_S.render("단축키: [Q/W/E/R] 홈팀 전술 조절  |  [Space] 경기 시작/일시정지", True, GRAY)
        manual_lbl2 = FONT_S.render("Q:속도  W:패스  E:압박  R:수비격렬성 (상/하 방향키로 조절)", True, GRAY)
        screen.blit(manual_lbl1, (30, 625))
        screen.blit(manual_lbl2, (30, 645))

    def handle_keys(self):
        keys = pygame.key.get_pressed()
        
        # 방향키에 매칭하여 전술 파라미터 조절
        adj_speed = 1
        if keys[pygame.K_q]:
            if keys[pygame.K_UP]: self.tactics_home.speed = min(99, self.tactics_home.speed + adj_speed)
            if keys[pygame.K_DOWN]: self.tactics_home.speed = max(1, self.tactics_home.speed - adj_speed)
        if keys[pygame.K_w]:
            if keys[pygame.K_UP]: self.tactics_home.pass_risk = min(99, self.tactics_home.pass_risk + adj_speed)
            if keys[pygame.K_DOWN]: self.tactics_home.pass_risk = max(1, self.tactics_home.pass_risk - adj_speed)
        if keys[pygame.K_e]:
            if keys[pygame.K_UP]: self.tactics_home.pressure = min(99, self.tactics_home.pressure + adj_speed)
            if keys[pygame.K_DOWN]: self.tactics_home.pressure = max(1, self.tactics_home.pressure - adj_speed)
        if keys[pygame.K_r]:
            if keys[pygame.K_UP]: self.tactics_home.aggression = min(99, self.tactics_home.aggression + adj_speed)
            if keys[pygame.K_DOWN]: self.tactics_home.aggression = max(1, self.tactics_home.aggression - adj_speed)

    def run(self):
        global running
        dt = 0.016
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.is_playing = not self.is_playing
                        play_sound(600, 0.05)
                        
            self.handle_keys()
            
            if self.is_playing:
                # 경기 시간 전개 (약 2.5분 주기로 90분 연출)
                self.match_time += dt * 0.6 * self.sim_speed
                if self.match_time >= 90.0:
                    self.match_time = 90.0
                    self.is_playing = False
                    self.add_log("🏁 경기 종료! 전술 시뮬레이션이 마감되었습니다.")
                    play_sound(1000, 0.5)
                
                # 피치 물리 시뮬레이션 구동
                self.update_physics(dt * self.sim_speed)
                
            screen.fill(DARK_NAVY)
            self.draw()
            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    sim = ManagerSimulator()
    sim.run()
