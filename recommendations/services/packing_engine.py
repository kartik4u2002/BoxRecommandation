from decimal import Decimal
from typing import List, Tuple, Optional


class ItemToPack:
    """
    Represents an individual physical item to be placed in a shipping box.
    """
    def __init__(
        self,
        name: str,
        length: Decimal,
        width: Decimal,
        height: Decimal,
        weight: Decimal = Decimal('0.00'),
        product_id: Optional[int] = None
    ):
        self.name = name
        self.length = Decimal(str(length))
        self.width = Decimal(str(width))
        self.height = Decimal(str(height))
        self.weight = Decimal(str(weight))
        self.product_id = product_id

    @property
    def volume(self) -> Decimal:
        """Volume in cubic centimeters."""
        return self.length * self.width * self.height

    def get_unique_orientations(self) -> List[Tuple[Decimal, Decimal, Decimal]]:
        """
        Generate all unique 3D rectangular orientations for this item.
        The six canonical orientations are:
        - L x W x H
        - L x H x W
        - W x L x H
        - W x H x L
        - H x L x W
        - H x W x L

        Duplicate orientations resulting from equal dimensions (e.g., cubes)
        are eliminated while preserving deterministic order.
        """
        raw_orientations = [
            (self.length, self.width, self.height),
            (self.length, self.height, self.width),
            (self.width, self.length, self.height),
            (self.width, self.height, self.length),
            (self.height, self.length, self.width),
            (self.height, self.width, self.length),
        ]
        unique_orientations = []
        for orientation in raw_orientations:
            if orientation not in unique_orientations:
                unique_orientations.append(orientation)
        return unique_orientations

    def __repr__(self):
        return f"ItemToPack({self.name}, {self.length}x{self.width}x{self.height}, vol={self.volume})"


class PlacedItem:
    """
    Represents an item that has been positioned inside the box coordinate space.
    The bounding box extends from (x, y, z) to (x + dx, y + dy, z + dz).
    """
    def __init__(
        self,
        item: ItemToPack,
        x: Decimal,
        y: Decimal,
        z: Decimal,
        dx: Decimal,
        dy: Decimal,
        dz: Decimal
    ):
        self.item = item
        self.x = x
        self.y = y
        self.z = z
        self.dx = dx
        self.dy = dy
        self.dz = dz

    def overlaps_with(
        self,
        x: Decimal,
        y: Decimal,
        z: Decimal,
        dx: Decimal,
        dy: Decimal,
        dz: Decimal
    ) -> bool:
        """
        Determine if this placed item overlaps with a candidate bounding box.
        Two 3D boxes overlap if and only if their intervals strictly overlap
        along all three Cartesian axes (X, Y, and Z).
        Items touching at their faces/boundaries do NOT overlap.
        """
        overlap_x = max(self.x, x) < min(self.x + self.dx, x + dx)
        overlap_y = max(self.y, y) < min(self.y + self.dy, y + dy)
        overlap_z = max(self.z, z) < min(self.z + self.dz, z + dz)
        return overlap_x and overlap_y and overlap_z

    def __repr__(self):
        return (
            f"PlacedItem({self.item.name} at [{self.x}, {self.y}, {self.z}] "
            f"size [{self.dx}, {self.dy}, {self.dz}])"
        )


class PackingEngine:
    """
    Deterministic 3D heuristic packing engine using Extreme Point Placement.

    Algorithm Summary:
    1. Items are sorted by descending volume (with maximum dimension as tie-breaker).
    2. A candidate placement coordinate pool is maintained, initialized with (0, 0, 0).
    3. Candidate points are sorted bottom-to-top (Z), back-to-front (Y), left-to-right (X).
    4. For each item:
       - Iterate over candidate placement points.
       - Test all deduplicated 3D rotations.
       - Verify the item stays within internal box dimensions.
       - Verify the item does not overlap with any previously placed item.
       - Place the item at the first valid point and rotation.
       - Add new extreme points along the placed item's boundaries and adjacent items.
    5. Returns True and placed items if all items fit; otherwise returns False.

    Limitations:
    - 3D Bin Packing is an NP-hard problem. This engine implements a deterministic greedy
      heuristic designed for clarity, predictability, and efficiency.
    - It does not guarantee finding a packing arrangement in pathological cases where
      complex interlocking arrangements are required, even if mathematically feasible.
    """

    @staticmethod
    def generate_orientations(
        length: Decimal,
        width: Decimal,
        height: Decimal
    ) -> List[Tuple[Decimal, Decimal, Decimal]]:
        """
        Utility method to generate deduplicated orientations for given dimensions.
        """
        item = ItemToPack("temp", length, width, height)
        return item.get_unique_orientations()

    @classmethod
    def can_pack(
        cls,
        box_length: Decimal,
        box_width: Decimal,
        box_height: Decimal,
        items: List[ItemToPack]
    ) -> bool:
        """
        Check if the list of items can be packed inside the box.
        """
        success, _ = cls.pack(box_length, box_width, box_height, items)
        return success

    @classmethod
    def pack(
        cls,
        box_length: Decimal,
        box_width: Decimal,
        box_height: Decimal,
        items: List[ItemToPack]
    ) -> Tuple[bool, List[PlacedItem]]:
        """
        Attempt to pack all items inside the box dimensions.

        Returns:
            Tuple of (success: bool, placed_items: List[PlacedItem])
        """
        if not items:
            return True, []

        box_l = Decimal(str(box_length))
        box_w = Decimal(str(box_width))
        box_h = Decimal(str(box_height))

        # Check total volume preliminary feasibility
        total_items_volume = sum(item.volume for item in items)
        box_volume = box_l * box_w * box_h
        if total_items_volume > box_volume:
            return False, []

        # Sort items: largest volume first; tie breaker: largest single dimension
        sorted_items = sorted(
            items,
            key=lambda it: (it.volume, max(it.length, it.width, it.height)),
            reverse=True
        )

        placed_items: List[PlacedItem] = []
        candidate_points = {(Decimal('0'), Decimal('0'), Decimal('0'))}

        for item in sorted_items:
            placed = False
            unique_orientations = item.get_unique_orientations()

            # Sort candidate points: lowest Z first (gravity/bottom-up), then lowest Y, lowest X
            sorted_points = sorted(
                candidate_points,
                key=lambda pt: (pt[2], pt[1], pt[0])
            )

            for pt in sorted_points:
                px, py, pz = pt

                for dx, dy, dz in unique_orientations:
                    # 1. Boundary check: ensure the item fits within the box
                    if (px + dx > box_l) or (py + dy > box_w) or (pz + dz > box_h):
                        continue

                    # 2. Overlap check: ensure no collision with already placed items
                    collision = False
                    for existing in placed_items:
                        if existing.overlaps_with(px, py, pz, dx, dy, dz):
                            collision = True
                            break

                    if collision:
                        continue

                    # Valid placement found! Place the item.
                    new_placement = PlacedItem(item, px, py, pz, dx, dy, dz)
                    placed_items.append(new_placement)

                    # Update candidate points
                    candidate_points.discard(pt)

                    # Generate new extreme points along the faces of the placed item
                    new_points = [
                        (px + dx, py, pz),
                        (px, py + dy, pz),
                        (px, py, pz + dz),
                    ]

                    # Also project with respect to existing placed items to fill crevices
                    for existing in placed_items:
                        if existing is new_placement:
                            continue
                        # Align X with new item, Y with existing
                        new_points.append((px + dx, existing.y + existing.dy, pz))
                        # Align Y with new item, X with existing
                        new_points.append((existing.x + existing.dx, py + dy, pz))
                        # Align Z with new item, X/Y with existing
                        new_points.append((existing.x + existing.dx, py, pz + dz))
                        new_points.append((px, existing.y + existing.dy, pz + dz))

                    for npt in new_points:
                        nx, ny, nz = npt
                        # Filter out points that exceed box boundaries
                        if nx >= box_l or ny >= box_w or nz >= box_h:
                            continue

                        # Filter out points located strictly inside an already placed item
                        inside_any = False
                        for p in placed_items:
                            if (p.x <= nx < p.x + p.dx and
                                p.y <= ny < p.y + p.dy and
                                p.z <= nz < p.z + p.dz):
                                inside_any = True
                                break

                        if not inside_any:
                            candidate_points.add((nx, ny, nz))

                    placed = True
                    break

                if placed:
                    break

            if not placed:
                # Unable to place this item anywhere in the box
                return False, []

        return True, placed_items
