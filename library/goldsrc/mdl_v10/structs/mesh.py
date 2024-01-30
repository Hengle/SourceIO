from dataclasses import dataclass

from ....utils import Buffer

# // meshes
# struct mstudiomesh_t
# {
# 	int		numtris;
# 	int		triindex;
# 	int		skinref;
# 	int		numnorms;		// per mesh normals
# 	int		normindex;		// normal glm::vec3
# };

@dataclass(slots=True)
class StudioTrivert:
    vertex_index: int
    normal_index: int
    uv: tuple[int, int]

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        return cls(buffer.read_uint16(), buffer.read_uint16(), buffer.read_fmt("2H"))


@dataclass(slots=True)
class StudioMesh:
    skin_ref: int
    triangle_count: int
    triangles: list[tuple[list[StudioTrivert], bool]]

    @classmethod
    def from_buffer(cls, buffer: Buffer):
        (triangle_count, triangle_offset,
         skin_ref,
         normal_count, normal_offset) = buffer.read_fmt('5i')
        with buffer.save_current_offset():
            buffer.seek(triangle_offset)
            triangles = []
            while True:
                trivert_count = buffer.read_int16()
                trivert_fan = trivert_count < 0
                trivert_count = abs(trivert_count)
                if trivert_count == 0:
                    break
                triverts = []
                for _ in range(trivert_count):
                    trivert = StudioTrivert.from_buffer(buffer)
                    triverts.append(trivert)
                triangles.append((triverts, trivert_fan))
        return cls(skin_ref, triangle_count, triangles)
