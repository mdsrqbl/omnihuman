"""Wrapper for 3D point-cloud animations"""

from typing import Tuple

try:
    import bpy
except ImportError:
    bpy = None

from omnihuman.data.avatar_3d.types import ArmatureDict, FBXDict, MeshDict


def assert_bpy_is_imported():
    """Check if the Blender Python API (bpy) is available."""
    if bpy is None:
        raise ModuleNotFoundError("Blender Python API (bpy) is not available. Please run `pip install bpy`.")


class Avatar3D:
    @classmethod
    def parse_fbx(cls, path: str, precision=5) -> FBXDict:
        assert_bpy_is_imported()

        # clear existing scene # todo: beware multithreading
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False)

        # import FBX
        bpy.ops.import_scene.fbx(filepath=path)
        scene = bpy.context.scene
        depsgraph = bpy.context.evaluated_depsgraph_get()

        start, end = cls.extract_frame_range(scene)

        parsed = {
            "armatures": [],
            "meshes": [],
            "others": [],
        }

        for obj in scene.objects:
            if obj.type == "ARMATURE":
                parsed["armatures"].append(cls._parse_armature(obj, scene, start, end, precision=precision))
            elif obj.type == "MESH":
                parsed["meshes"].append(cls._parse_mesh(obj, scene, depsgraph, start, end, precision=precision))
            else:
                parsed["others"].append({"name": obj.name, "type": obj.type})

        # todo: clean up

        return parsed

    @staticmethod
    def extract_frame_range(scene) -> Tuple[int, int]:
        """frame numbers where the animation starts and ends (1-indexed in Blender)"""
        first = scene.frame_start
        final = scene.frame_end

        # try to determine frame range from action keyframes
        if (
            (armature := next((o for o in scene.objects if o.type == "ARMATURE"), None))
            and armature.animation_data
            and armature.animation_data.action
            and (keyframes := [kp.co.x for fc in armature.animation_data.action.fcurves for kp in fc.keyframe_points])
        ):
            first = int(min(keyframes))
            final = int(max(keyframes))

        return first, final

    @staticmethod
    def _parse_armature(armature, scene, start=0, end=1000, precision=5) -> ArmatureDict:
        assert_bpy_is_imported()

        parsed = {
            "name": armature.name,
            "bones": [(b.name, [c.name for c in b.children]) for b in armature.data.bones],
            "rest": [
                [round(c, precision) for c in tuple(armature.matrix_world @ bone.head_local)]
                for bone in armature.data.bones
            ],
            "animation": [],
        }
        for idx in range(start, end + 1):
            scene.frame_set(idx)
            bpy.context.view_layer.update()
            parsed["animation"].append(
                [
                    [round(c, precision) for c in tuple(armature.matrix_world @ armature.pose.bones[name].head)]
                    for name, _ in parsed["bones"]
                ]
            )

        return parsed

    @staticmethod
    def _parse_mesh(mesh, scene, depsgraph, start=0, end=1000, precision=5) -> MeshDict:
        assert_bpy_is_imported()

        parsed = {
            "name": mesh.name,
            "influences": [
                sorted(
                    ((mesh.vertex_groups[g.group].name, round(g.weight, precision)) for g in v.groups),
                    key=lambda item: -item[-1],
                )
                for v in mesh.data.vertices
            ],
            "rest": [[round(c, precision) for c in tuple(mesh.matrix_world @ v.co)] for v in mesh.data.vertices],
            "animation": [],
        }
        for idx in range(start, end + 1):
            scene.frame_set(idx)
            bpy.context.view_layer.update()
            eval_obj = mesh.evaluated_get(depsgraph)
            eval_mesh = eval_obj.to_mesh()
            parsed["animation"].append(
                [[round(c, precision) for c in tuple(mesh.matrix_world @ v.co)] for v in eval_mesh.vertices]
            )
            eval_obj.to_mesh_clear()

        return parsed
