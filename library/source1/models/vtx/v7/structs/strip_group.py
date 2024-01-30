from dataclasses import dataclass, field

import numpy as np
import numpy.typing as npt

from SourceIO.library.utils import Buffer
from ...v6.structs.strip import Strip
from ...v6.structs.strip_group import StripGroup as StripGroup6, StripGroupFlags

VERTEX_DTYPE = np.dtype(
    [
        ('bone_weight_index', np.uint8, (3,)),
        ('bone_count', np.uint8, (1,)),
        ('original_mesh_vertex_index', np.uint16, (1,)),
        ('bone_id', np.uint8, (3,)),

    ]
)


@dataclass(slots=True)
class StripGroup(StripGroup6):
    flags: StripGroupFlags
    vertexes: npt.NDArray[VERTEX_DTYPE] = field(repr=False)
    indices: npt.NDArray[np.uint16] = field(repr=False)
    strips: list[Strip] = field(repr=False)

    # topology: list[int]

    @classmethod
    def from_buffer(cls, buffer: Buffer, extra8: bool = False):
        entry = buffer.tell()
        vertex_count = buffer.read_uint32()
        vertex_offset = buffer.read_uint32()
        index_count = buffer.read_uint32()
        assert index_count % 3 == 0
        index_offset = buffer.read_uint32()
        strip_count = buffer.read_uint32()
        strip_offset = buffer.read_uint32()
        assert vertex_offset < buffer.size()
        assert strip_offset < buffer.size()
        assert index_offset < buffer.size()
        flags = StripGroupFlags(buffer.read_uint8())
        if extra8:
            buffer.skip(8)
        strips = []
        with buffer.save_current_offset():
            buffer.seek(entry + index_offset)
            indices = np.frombuffer(buffer.read(2 * index_count), dtype=np.uint16)
            buffer.seek(entry + vertex_offset)
            vertexes = np.frombuffer(buffer.read(vertex_count * VERTEX_DTYPE.itemsize), VERTEX_DTYPE)
            buffer.seek(entry + strip_offset)
            for _ in range(strip_count):
                strip = Strip.from_buffer(buffer, extra8)
                strips.append(strip)

        return cls(flags, vertexes, indices, strips)
