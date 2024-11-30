import bpy
from mathutils import Quaternion, Vector, Matrix

from SourceIO.library.utils.tiny_path import TinyPath
from SourceIO.library.shared.content_manager.manager import ContentManager
from SourceIO.library.source1.dmx.sfm import open_session
from SourceIO.library.source1.dmx.sfm.animation_set import AnimationSet
from SourceIO.library.source1.dmx.sfm.camera import Camera
from SourceIO.library.source1.dmx.sfm.film_clip import FilmClip
from SourceIO.library.source1.dmx.sfm_utils import convert_source_rotation, convert_source_position
from SourceIO.library.utils.math_utilities import SOURCE1_HAMMER_UNIT_TO_METERS
from SourceIO.library.utils.path_utilities import find_vtx_cm
from SourceIO.blender_bindings.shared.model_container import ModelContainer
from SourceIO.blender_bindings.models.mdl49.import_mdl import import_model
from SourceIO.blender_bindings.models.common import put_into_collections


def _convert_quat(quat):
    return Quaternion([quat[3], quat[0], quat[1], quat[2]])
    # return quat


def import_gamemodel(mdl_path, scale=SOURCE1_HAMMER_UNIT_TO_METERS):
    mdl_path = TinyPath(mdl_path)
    mld_file = ContentManager().find_file(mdl_path)
    if mld_file:
        vvd_file = ContentManager().find_file(mdl_path.with_suffix('.vvd'))
        vtx_file = find_vtx_cm(mdl_path, ContentManager())
        file_list = FileImport(mld_file, vvd_file, vtx_file, None, None)
        model_container = import_model(file_list, scale, False, True, True)
        # import_materials(model_container.mdl)
        put_into_collections(model_container, mdl_path.stem, bodygroup_grouping=True)
        return model_container
    return None


def create_camera(dme_camera: Camera, scale=SOURCE1_HAMMER_UNIT_TO_METERS):
    camera = bpy.data.cameras.new(name=dme_camera.name)
    camera_obj = bpy.data.objects.new(dme_camera.name, camera)

    bpy.context.scene.collection.objects.link(camera_obj)

    camera_obj.location = Vector(dme_camera.transform.position) * scale
    camera_obj.rotation_mode = 'QUATERNION'
    camera_obj.rotation_quaternion = _convert_quat(dme_camera.transform.orientation)
    camera.lens = dme_camera.milliliters


def _apply_transforms(container: ModelContainer, animset: AnimationSet, scale=SOURCE1_HAMMER_UNIT_TO_METERS):
    for control in animset.controls:
        if control.type == 'DmElement':
            for obj in container.objects:
                if obj.type != 'MESH':
                    continue
                if obj.data.shape_keys and control.name in obj.data.shape_keys.key_blocks:
                    obj.data.shape_keys.key_blocks[control.name].value = control['value']
            pass  # flex
        elif control.type == 'DmeTransformControl':
            bone_name = control.name
            tmp = control['valuePosition']
            pos = Vector(tmp) * scale
            rot = _convert_quat(control['valueOrientation'])
            if container.armature:
                arm = container.armature
                bone = arm.pose.bones.get(bone_name, None)
                if bone:
                    mat = Matrix.Translation(pos) @ rot.to_matrix().to_4x4()
                    mat = bone.parent.matrix @ mat if bone.parent else mat
                    bone.matrix = mat
                    # bone.matrix_basis.identity()


def load_animset(animset: AnimationSet, shot: FilmClip, scale=SOURCE1_HAMMER_UNIT_TO_METERS):
    if animset.game_model:
        container = import_gamemodel(animset.game_model.model_name, scale)
        if container is None:
            print(f'Failed to load {animset.name} model')
            return None
        if container.armature:

            qrot = convert_source_rotation(animset.game_model.transform.orientation)
            pos = convert_source_position(animset.game_model.transform.position)
            container.armature.rotation_mode = 'QUATERNION'
            container.armature.location = pos * scale
            container.armature.rotation_quaternion = qrot
            # _apply_bone_transforms(animset, container, scale)

        else:
            for obj in container.objects:
                qrot = convert_source_rotation(animset.game_model.transform.orientation)
                pos = convert_source_position(animset.game_model.transform.position)
                obj.location = pos * scale
                obj.rotation_quaternion = qrot
        _apply_transforms(container, animset, scale)


def load_session(session_path: TinyPath, scale=SOURCE1_HAMMER_UNIT_TO_METERS):
    session = open_session(session_path)
    active_clip = session.active_clip
    # map_file = active_clip.map_file
    # if map_file:
    #     print(f'Loading {active_clip.map_name}')
    #
    #     bsp_map = BSP(map_file, scale=scale)
    #
    #     bsp_map.load_disp()
    #     bsp_map.load_entities()
    #     bsp_map.load_static_props()
    #     # bsp_map.load_materials()

    for shot in active_clip.sub_clip_track_group.tracks[0].children[:1]:
        camera = shot.camera
        create_camera(camera)
        for anim_set in shot.animation_sets:
            load_animset(anim_set, shot, scale)
