from __future__ import annotations

from typing import TYPE_CHECKING

from grassland.entities.base import Entity
from grassland.geometry import Vec2

if TYPE_CHECKING:
    from grassland.world import World


class Plant(Entity):
    """
    모든 식물의 부모 클래스.

    속성:
        health       : 현재 체력. 0 이하가 되면 die() 호출.
        max_health   : 체력 상한값.
        photosynthesis: 광합성으로 초당 회복하는 체력량.
        spread       : 번식 누적값. 서브클래스/World가 읽어 새 개체를 생성.
    """

    def __init__(
        self,
        name: str,
        position: Vec2,
        health: float,
        max_health: float,
        color: tuple[int, int, int],
        photosynthesis: float = 1.0,
    ):
        super().__init__(
            name=name,
            position=position,
            radius=20,
            color=color,
            kind="plant",
        )
        self.health = health
        self.max_health = max_health
        self.photosynthesis = photosynthesis  # 초당 체력 회복량 (햇빛)
        self.spread = 0.0                     # 번식 누적값

    # ── 매 틱 갱신 ───────────────────────────────────────────────────────────

    def update(self, _world: "World", dt: float) -> None:
        """기본 동작: 광합성으로 체력 회복. 서브클래스에서 super().update() 호출 권장."""
        if self.alive:
            self.photosynthesize(dt)

    def photosynthesize(self, dt: float) -> None:
        """햇빛으로 체력을 max_health까지 서서히 회복."""
        self.health = min(self.max_health, self.health + self.photosynthesis * dt)

    # ── 핵심 메서드 ──────────────────────────────────────────────────────────

    def reproduce(self) -> None:
        """번식 누적값 증가. World가 이 값을 읽어 주변에 새 식물을 생성."""
        self.spread += 1.0

    def consume(self, amount: float) -> float:
        """
        동물이 이 식물을 섭취할 때 호출.
        실제로 먹힌 양을 반환하며, 체력이 0 이하면 die() 호출.
        Bush처럼 추가 효과가 있는 서브클래스는 이 메서드를 오버라이딩.
        """
        eaten = min(self.health, amount)
        self.health -= eaten
        if self.health <= 0:
            self.die()
        return eaten

    def die(self) -> None:
        """식물을 죽은 상태로 전환 (통과 가능, 렌더링에서 제거 대상)."""
        self.alive = False
        self.solid = False
        self.action_text = "dead"
