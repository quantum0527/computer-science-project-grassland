# computer-science-project-grassland

## 와글와글 초원 생태계

객체지향 프로그래밍 프로젝트 계획서에 맞춘 아프리카 초원 생태계 시뮬레이션입니다.  
현재 이미지는 없으므로 동물, 식물, 자원, 지형은 텍스트가 붙은 단순 도형으로 표시합니다.

## 실행 방법

이 폴더에서는 `.venv`에 `pygame`이 설치되어 있으므로 바로 실행할 수 있습니다.

```powershell
.\.venv\Scripts\python.exe main.py
```

다른 조원이 처음 내려받은 경우에는 아래처럼 환경을 만들면 됩니다.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

마우스로 화면을 드래그하면 1280x720 창보다 큰 초원 맵을 이동해서 볼 수 있습니다.

## 파일 구조

- `main.py`: 프로그램 시작 파일
- `grassland/gui.py`: pygame GUI, 화면 그리기, 카메라 드래그
- `grassland/physics.py`: 간단한 위치, 속도, 경계, 충돌/밀림 처리
- `grassland/world.py`: 생태계 객체 생성과 전체 시뮬레이션 진행
- `grassland/entities/animals/`: `Animal` 공통 부모 클래스와 동물 계열 폴더
  - `carnivores/`: `Carnivore`, `Lion`, `Hyena`, `BaldEagle`
  - `herbivores/`: `Herbivore`, `Zebra`, `Gazelle`, `Elephant`
  - `omnivores/`: `Omnivore`, `Meerkat`, `Warthog`
- `grassland/entities/plants/`: `Plant`와 자식 식물 클래스
- `grassland/entities/resources/`: `Resource`, `WaterPuddle`, `Carcass`
- `grassland/entities/terrain/`: `Terrain`, `Plain`, `LakeSide`, `Cave`
- `grassland/entities/environment/`: `Environment`, `DroughtEvent`

## GitHub 공유 흐름

이 폴더는 Git 저장소로 초기화되어 있고 `origin`이 아래 주소로 연결되어 있습니다. VSCode의 소스 제어 탭에서 커밋/동기화를 사용할 수 있습니다.

```powershell
git remote -v
git add .
git commit -m "Initial grassland simulation"
git push -u origin main
```
