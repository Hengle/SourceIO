from typing import Optional

from SourceIO.blender_bindings.models.model_tags import MODEL_HANDLERS, choose_model_importer
from SourceIO.library.utils import Buffer
from . import mdl4, mdl6, mdl10, mdl36, mdl44, mdl49, md3_15
from ..operators.import_settings_base import ModelOptions
from ..shared.exceptions import SourceIOUnsupportedFormatException
from ..shared.model_container import ModelContainer
from ...library.shared.app_id import SteamAppId
from ...library.shared.content_manager.manager import ContentManager
from ...library.utils.tiny_path import TinyPath
from ...logger import SourceLogMan

log_manager = SourceLogMan()
logger = log_manager.get_logger('MDL loader')


def import_model(model_path: TinyPath, buffer: Buffer,
                 content_provider: ContentManager,
                 options: ModelOptions,
                 override_steam_id: Optional[SteamAppId] = None,
                 ) -> Optional[ModelContainer]:
    ident, version = buffer.read_fmt("4sI")
    logger.info(f"Trying to load model: {model_path}")
    logger.info(f"Detected magic: {ident!r}, version:{version}")
    steam_id = content_provider.get_steamid_from_asset(model_path)
    handler = choose_model_importer(ident, version, (override_steam_id or steam_id or None))
    if handler is None:
        raise SourceIOUnsupportedFormatException(f"No handler found for ident {ident} version: {version}")
    buffer.seek(0)
    container = handler(model_path, buffer, content_provider, options)
    return container
