import bpy
from bpy.props import (BoolProperty, CollectionProperty, FloatProperty,
                       StringProperty)

from ..goldsrc.bsp.import_bsp import BSP
from ...library.global_config import GoldSrcConfig
from ...library.shared.content_manager.manager import ContentManager
from ...library.utils.math_utilities import SOURCE1_HAMMER_UNIT_TO_METERS
from ...library.utils.tiny_path import TinyPath
from ...logger import SourceLogMan

logger = SourceLogMan().get_logger("GoldSrc::Operators")


class SOURCEIO_OT_GBSPImport(bpy.types.Operator):
    """Load GoldSrc BSP"""
    bl_idname = "sourceio.gbsp"
    bl_label = "Import GoldSrc BSP file"
    bl_options = {'UNDO'}

    filepath: StringProperty(subtype="FILE_PATH")
    files: CollectionProperty(name='File paths', type=bpy.types.OperatorFileListElement)
    filter_glob: StringProperty(default="*.bsp", options={'HIDDEN'})

    scale: FloatProperty(name="World scale", default=SOURCE1_HAMMER_UNIT_TO_METERS, precision=6)
    use_hd: BoolProperty(name="Load HD models", default=False, subtype='UNSIGNED')
    single_collection: BoolProperty(name="Load everything into 1 collection", default=False, subtype='UNSIGNED')
    fix_rotation: BoolProperty(name="Fix rotations. Some games require it", default=True, subtype='UNSIGNED')

    def execute(self, context):

        if TinyPath(self.filepath).is_file():
            directory = TinyPath(self.filepath).parent.absolute()
        else:
            directory = TinyPath(self.filepath).absolute()
        content_provider = ContentManager()
        content_provider.scan_for_content(directory)
        for n, file in enumerate(self.files):
            logger.info(f"Loading {n}/{len(self.files)}")
            config = GoldSrcConfig()
            config.use_hd = self.use_hd
            bsp = BSP(content_provider, directory / file.name, scale=self.scale,
                      single_collection=self.single_collection,
                      fix_rotation=self.fix_rotation)
            bsp.load_map()
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        wm.fileselect_add(self)
        return {'RUNNING_MODAL'}
