# 환경 코드 설명서

이 문서는 `entities`를 제외한 환경 코드만 설명한다.

환경 코드 범위:

- `main.py`
- `grassland/app.py`
- `grassland/config.py`
- `grassland/geometry.py`
- `grassland/gui.py`
- `grassland/physics.py`
- `grassland/world.py`

## .venv의 역할

`.venv`는 프로젝트 전용 Python 실행 환경이다.

이 폴더 안에는 다음과 같은 것들이 들어간다.

- `Scripts/python.exe`: 이 프로젝트에서 사용하는 Python 실행 파일
- `Scripts/pip.exe`: 이 프로젝트 전용 패키지 설치 도구
- `Lib/site-packages/`: `pygame` 같은 외부 라이브러리가 설치되는 폴더
- `pyvenv.cfg`: 이 가상환경이 어떤 Python을 기반으로 만들어졌는지 기록하는 설정 파일

`.venv`는 코드를 자동으로 바꾸지 않는다.

실행 과정은 다음과 같다.

1. `python -m venv .venv`로 가상환경 폴더를 만든다.
2. `.\.venv\Scripts\activate`를 실행하면 터미널의 기본 `python`, `pip`가 `.venv` 안의 것으로 바뀐다.
3. `pip install -r requirements.txt`를 실행하면 필요한 라이브러리가 `.venv/Lib/site-packages`에 설치된다.
4. `python main.py` 또는 `.\.venv\Scripts\python.exe main.py`로 실행한다.

중요한 점:

- `.venv`를 활성화해야 자동으로 적용된다.
- 활성화하지 않아도 `.\.venv\Scripts\python.exe main.py`처럼 직접 경로를 쓰면 적용된다.
- `.venv` 안에 설치된 `pygame`은 프로젝트 코드가 import할 때 사용된다.
- 내가 직접 설정한 것은 `.venv` 생성과 `pygame` 설치다.
- `.venv` 안의 세부 파일들은 Python과 pip가 자동으로 만든다.

## 사용된 외부/기본 모듈

### argparse

Python 기본 모듈이다. 터미널 옵션을 읽는다.

현재 사용 위치:

- `app.py`

역할:

- `--headless-steps 600` 같은 실행 옵션을 처리한다.
- GUI 없이 시뮬레이션만 테스트할 수 있게 한다.

### random

Python 기본 모듈이다. 랜덤 값을 만든다.

현재 사용 위치:

- `world.py`
- `geometry.py`

역할:

- 날씨를 랜덤으로 고른다.
- 온도를 랜덤으로 정한다.
- 가뭄 강도를 랜덤으로 정한다.
- 랜덤 방향 벡터를 만든다.

### math

Python 기본 모듈이다. 수학 계산을 한다.

현재 사용 위치:

- `geometry.py`

역할:

- `sqrt`: 거리 계산에 사용한다.
- `sin`, `cos`: 랜덤 방향 벡터에 사용한다.
- `tau`: 360도 전체 각도 값을 의미한다.

### pathlib.Path

Python 기본 모듈이다. 파일 경로를 다룬다.

현재 사용 위치:

- `gui.py`

역할:

- 스프라이트시트 이미지 파일이 존재하는지 확인한다.

### pygame

외부 라이브러리다. `.venv`에 설치되어 있다.

현재 사용 위치:

- `gui.py`

역할:

- 창 만들기
- 창 크기 변경 처리
- 마우스 입력 처리
- 도형 그리기
- 글자 그리기
- 이미지 로딩
- 화면 업데이트

## config.py

설정값을 모아둔 파일이다. 함수나 클래스 없이 상수만 있다.

- `SCREEN_WIDTH`: 기본 창 가로 크기
- `SCREEN_HEIGHT`: 기본 창 세로 크기
- `MIN_SCREEN_WIDTH`: 사용자가 창을 줄일 수 있는 최소 가로 크기
- `MIN_SCREEN_HEIGHT`: 사용자가 창을 줄일 수 있는 최소 세로 크기
- `WORLD_WIDTH`: 실제 맵의 가로 크기
- `WORLD_HEIGHT`: 실제 맵의 세로 크기
- `FPS`: 1초에 화면을 몇 번 갱신할지 정하는 값
- `GAME_HOURS_PER_SECOND`: 실제 1초가 게임 시간 몇 시간인지 정하는 값
- `DAY_LENGTH_HOURS`: 하루 길이. 24시간
- `SKY_OVERLAY_ALPHA`: 하늘 오버레이의 투명도
- `BACKGROUND_COLOR`: 초원 배경색
- `GRID_COLOR`: 맵 격자선 색
- `TEXT_COLOR`: 기본 글자색
- `PANEL_COLOR`: HUD 패널 배경색
- `PANEL_BORDER`: HUD 패널 테두리색
- `ASSET_SPRITE_SHEET`: 스프라이트시트 이미지 경로

## geometry.py

2D 좌표 계산 도구를 정의한다.

### `class Vec2`

2D 벡터 클래스다. 위치와 방향을 모두 표현한다.

- `x`: 가로 좌표 또는 가로 방향 성분
- `y`: 세로 좌표 또는 세로 방향 성분

### `__init__(self, x=0.0, y=0.0)`

객체가 만들어질 때 실행된다.

- `self.x = x`: x값 저장
- `self.y = y`: y값 저장

### `__add__(self, other)`

`a + b`를 가능하게 한다.

두 벡터의 x끼리, y끼리 더한다.

### `__sub__(self, other)`

`a - b`를 가능하게 한다.

두 위치의 차이를 구할 때 사용한다.

### `__mul__(self, value)`

`vector * 숫자`를 가능하게 한다.

속도에 시간을 곱해 이동량을 계산할 때 사용한다.

### `__rmul__ = __mul__`

`숫자 * vector`도 가능하게 한다.

### `__truediv__(self, value)`

`vector / 숫자`를 가능하게 한다.

방향을 정규화할 때 사용한다.

### `copy(self)`

같은 좌표를 가진 새 `Vec2`를 만든다.

### `length_squared(self)`

벡터 길이의 제곱을 구한다.

### `length(self)`

벡터 길이를 구한다.

### `normalized(self)`

길이가 1인 방향 벡터를 만든다.

### `distance_to(self, other)`

다른 좌표까지의 거리를 구한다.

### `limit(self, max_length)`

벡터 길이가 너무 길면 제한한다.

### `clamp(self, min_x, min_y, max_x, max_y)`

좌표가 특정 범위를 벗어나지 않게 제한한다.

### `as_int_tuple(self)`

pygame에서 쓰기 좋게 `(int(x), int(y))` 형태로 바꾼다.

### `random_unit_vector()`

랜덤 방향의 길이 1짜리 벡터를 만든다.

## physics.py

간단한 이동 물리 처리를 담당한다.

### `class PhysicsEngine`

맵 경계와 객체 겹침을 처리한다.

- `width`: 월드 가로 크기
- `height`: 월드 세로 크기
- `friction`: 매 프레임 속도를 줄이는 비율

### `update(self, entities, dt)`

살아 있는 객체만 골라 물리를 적용한다.

- `entities`: 위치와 속도를 가진 객체 목록
- `dt`: 이전 프레임 이후 흐른 실제 시간

### `_integrate(self, entity, dt)`

한 객체의 위치를 업데이트한다.

처리 순서:

1. 위치에 속도 곱하기 시간을 더한다.
2. 속도에 마찰을 곱해 조금 줄인다.
3. 맵 밖으로 나가지 못하게 위치를 제한한다.
4. 벽에 닿으면 속도를 반대 방향으로 약하게 튕긴다.

### `_separate(self, entities)`

두 객체가 겹치면 서로 밀어낸다.

## world.py

시뮬레이션 전체 상태를 관리한다.

### `class Environment`

날짜, 시간, 날씨, 온도를 관리한다.

- `day`: 현재 날짜
- `time`: 현재 시간. 0부터 24까지
- `weather`: 현재 날씨
- `temperature`: 현재 온도
- `ended`: 시뮬레이션 종료 여부
- `end_reason`: 종료 이유

### `Environment.update(self, dt)`

실제 시간을 게임 시간으로 바꿔 흐르게 한다.

### `change_time(self, hours)`

게임 시간을 증가시킨다. 24시가 넘으면 다음 날로 넘긴다.

### `change_day(self)`

날짜를 하루 증가시키고 날씨와 온도를 다시 정한다.

### `change_weather(self)`

날씨를 `sunny`, `cloudy`, `rain`, `drought` 중 하나로 정한다.

### `change_temperature(self)`

날씨에 맞춰 온도 범위를 다르게 잡는다.

### `clock_text(self)`

시간을 `06:00` 같은 문자열로 바꾼다.

### `class DroughtEvent`

가뭄 이벤트를 관리한다.

- `drought_intensity`: 가뭄 세기

### `dry_up_map(self, world, dt)`

가뭄일 때 물웅덩이의 물 양을 줄인다.

### `class MapObject`

맵 위에 놓이는 기본 객체다.

- `name`: 객체 이름
- `kind`: 객체 종류. `plant`, `resource`, `terrain`
- `position`: 월드 좌표
- `radius`: 표시 크기와 충돌 범위
- `color`: GUI에서 그릴 색
- `velocity`: 이동 속도
- `alive`: 살아 있거나 남아 있는지 여부
- `solid`: 물리 충돌 여부
- `action_text`: 화면에 표시할 행동 설명

### `class BasicPlant`

임시 식물 객체다.

- `health`: 식물의 남은 체력 또는 먹을 수 있는 양

### `class BasicResource`

임시 자원 객체다.

- `amount`: 현재 자원 양
- `max_amount`: 최대 자원 양
- `carried_by`: 누가 들고 있는지
- `being_eaten_by`: 누가 먹고 있는지

### `class BasicTerrain`

임시 지형 객체다.

동굴 숨기기, 호숫가 마시기 같은 기능을 제공한다.

### `class World`

전체 생태계를 담는 중심 클래스다.

- `width`: 월드 가로 크기
- `height`: 월드 세로 크기
- `environment`: 시간/날씨/온도 상태
- `physics`: 물리 처리 객체
- `elapsed`: 시뮬레이션이 실행된 총 시간
- `animals`: 동물 객체 목록. 지금은 비어 있음
- `plants`: 식물 객체 목록
- `resources`: 자원 객체 목록
- `terrains`: 지형 객체 목록
- `drought_event`: 현재 가뭄 이벤트

### `seed_default(cls)`

기본 월드를 만든다.

### `seed_terrain(self)`

평원, 호숫가, 동굴을 배치한다.

### `seed_plants(self)`

풀, 덤불, 아카시아, 바오밥을 배치한다.

### `seed_resources(self)`

물웅덩이와 사체를 배치한다.

### `update(self, dt)`

매 프레임 전체 시뮬레이션을 진행한다.

처리 순서:

1. 시간이 흐른다.
2. 새 날이 되면 하루 이벤트를 처리한다.
3. 가뭄이면 물을 줄인다.
4. 식물 업데이트를 실행한다.
5. 동물이 있으면 동물 업데이트를 실행한다.
6. 물리 처리를 실행한다.
7. 자원 업데이트를 실행한다.
8. 종료 조건을 확인한다.

### 탐색 메서드

동물 클래스가 나중에 사용할 수 있도록 가까운 객체를 찾아준다.

- `nearest_plant`
- `nearest_bush`
- `nearest_carcass`
- `nearest_water`
- `nearest_predator`
- `nearest_prey_for`
- `nearest_named`

## gui.py

pygame 화면과 입력을 담당한다.

### `class GrasslandApp`

GUI 앱 전체를 관리한다.

- `screen_width`: 현재 창 가로 크기
- `screen_height`: 현재 창 세로 크기
- `screen`: pygame 화면 객체
- `clock`: FPS 조절용 시계
- `world`: 화면에 보여줄 월드 객체
- `camera`: 현재 보고 있는 맵 위치
- `dragging`: 마우스로 드래그 중인지 여부
- `font`, `small_font`, `title_font`: 글자 표시용 폰트
- `sky_sprites`: 하늘 이미지 조각

### 주요 기능

- `run`: pygame 이벤트 루프 실행
- `resize`: 창 크기 변경
- `clamp_camera`: 카메라가 맵 밖으로 나가지 않게 제한
- `world_to_screen`: 월드 좌표를 화면 좌표로 변환
- `visible`: 객체가 현재 화면에 보이는지 확인
- `draw`: 전체 화면 그리기
- `draw_field`: 맵 격자 그리기
- `draw_sky_overlay`: 화면 상단 고정 하늘 그리기
- `draw_terrains`: 지형 그리기
- `draw_plants`: 식물 그리기
- `draw_resources`: 자원 그리기
- `draw_animals`: 나중에 추가될 동물 그리기
- `draw_ui`: 날짜, 시간, 날씨, 온도, 좌표 표시
- `draw_label`: 글자 그리기

