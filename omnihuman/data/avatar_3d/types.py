"""Types for the FBX parser."""

from typing import List, Tuple, TypeAlias, TypedDict

# Type aliases for repeated tuple shapes
Vector3: TypeAlias = Tuple[float, float, float]  # (x, y, z)
BoneAndChildren: TypeAlias = Tuple[str, List[str]]  # (bone_name, [child_bone_names])
Influence: TypeAlias = Tuple[str, float]  # (bone_name, weight)
FrameBones: TypeAlias = List[Vector3]  # one frame of bone positions
FrameVertices: TypeAlias = List[Vector3]  # one frame of vertex positions


# Intermediate structures
class ArmatureDict(TypedDict):
    name: str
    bones: List[BoneAndChildren]
    rest: FrameBones  # rest pose per bone
    animation: List[FrameBones]  # list of frames, each a list of Vec3 per bone


class MeshDict(TypedDict):
    name: str
    influences: List[List[Influence]]  # per vertex, list of bone‐weight pairs
    rest: FrameVertices  # rest pose per vertex
    animation: List[FrameVertices]  # per frame, list of Vec3 per vertex


class OtherObjectDict(TypedDict):
    name: str
    type: str


# Top‐level parsed structure
class FBXDict(TypedDict):
    armatures: List[ArmatureDict]
    meshes: List[MeshDict]
    others: List[OtherObjectDict]
