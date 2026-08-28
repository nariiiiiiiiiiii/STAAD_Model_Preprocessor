"""Raw DXF geometry reader for the T05 preview pipeline."""

from __future__ import annotations

from pathlib import Path

import ezdxf

from staadprep.importers.contracts import ImportBatch, RawPoint, RawSegment
from staadprep.model.geometry import Vec3

_INSUNITS = {
    0: None,
    1: "in",
    2: "ft",
    3: "mi",
    4: "mm",
    5: "cm",
    6: "m",
    7: "km",
    8: "microin",
    9: "mil",
    10: "yd",
    11: "angstrom",
    12: "nm",
    13: "um",
    14: "dm",
    15: "dam",
    16: "hm",
    17: "gm",
    18: "au",
    19: "ly",
    20: "pc",
}


def _vec3(value) -> Vec3:
    return Vec3(float(value[0]), float(value[1]), float(value[2]))


class DxfReader:
    """Extract only raw LINE, 3D POLYLINE, and POINT geometry."""

    def read(self, path: Path) -> ImportBatch:
        source = Path(path)
        document = ezdxf.readfile(source)
        modelspace = document.modelspace()

        points: list[RawPoint] = []
        segments: list[RawSegment] = []
        warnings: list[str] = []

        for entity in modelspace:
            entity_type = entity.dxftype()
            handle = entity.dxf.handle
            layer = entity.dxf.layer or None

            if entity_type == "LINE":
                segments.append(
                    RawSegment(
                        start=_vec3(entity.dxf.start),
                        end=_vec3(entity.dxf.end),
                        source_ref=f"LINE:{handle}",
                        layer=layer,
                    )
                )
                continue

            if entity_type == "POLYLINE":
                if not entity.is_3d_polyline:
                    warnings.append(f"Skipped non-3D POLYLINE:{handle}")
                    continue
                vertices = [_vec3(vertex.dxf.location) for vertex in entity.vertices]
                for index, (start, end) in enumerate(zip(vertices[:-1], vertices[1:], strict=True)):
                    segments.append(
                        RawSegment(
                            start=start,
                            end=end,
                            source_ref=f"POLYLINE:{handle}:{index}",
                            layer=layer,
                        )
                    )
                continue

            if entity_type == "POINT":
                points.append(
                    RawPoint(
                        position=_vec3(entity.dxf.location),
                        source_ref=f"POINT:{handle}",
                        layer=layer,
                    )
                )

        insunits_code = int(document.header.get("$INSUNITS", 0) or 0)
        return ImportBatch(
            points=tuple(points),
            segments=tuple(segments),
            source_format="dxf",
            declared_unit=_INSUNITS.get(insunits_code),
            metadata={
                "insunits_code": insunits_code,
                "dxfversion": document.dxfversion,
                "source_file": str(source),
            },
            warnings=tuple(warnings),
        )
