from grassland.geometry import Vec2


class PhysicsEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.friction = 0.88

    def update(self, entities, dt):
        movable = []
        for entity in entities:
            if getattr(entity, "alive", True):
                movable.append(entity)

        self._separate(movable)

        for entity in movable:
            self._integrate(entity, dt)

    def _integrate(self, entity, dt):
        entity.position = entity.position + entity.velocity * dt
        entity.velocity = entity.velocity * self.friction

        min_x = entity.radius
        min_y = entity.radius
        max_x = self.width - entity.radius
        max_y = self.height - entity.radius
        clamped = entity.position.clamp(min_x, min_y, max_x, max_y)

        if clamped.x != entity.position.x:
            entity.velocity = Vec2(-entity.velocity.x * 0.2, entity.velocity.y)
        if clamped.y != entity.position.y:
            entity.velocity = Vec2(entity.velocity.x, -entity.velocity.y * 0.2)

        entity.position = clamped

    def _separate(self, entities):
        for index in range(len(entities)):
            first = entities[index]
            if not getattr(first, "solid", True):
                continue

            for second in entities[index + 1 :]:
                if not getattr(second, "solid", True):
                    continue

                delta = second.position - first.position
                distance = delta.length()
                min_distance = first.radius + second.radius + 2

                if distance <= 0 or distance >= min_distance:
                    continue

                push = delta.normalized() * ((min_distance - distance) * 0.5)
                first.position = first.position - push
                second.position = second.position + push

