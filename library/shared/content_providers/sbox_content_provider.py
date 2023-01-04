from pathlib import Path
from typing import Union, Iterator, Tuple, Optional

from ...shared.app_id import SteamAppId
from .content_provider_base import ContentProviderBase
from ...utils import Buffer


class SBoxAddonProvider(ContentProviderBase):

    @property
    def steam_id(self):
        return SteamAppId.SBOX_STEAM_ID

    def find_file(self, filepath: Union[str, Path], additional_dir=None, extension=None) -> Optional[Buffer]:
        return self._find_file_generic(filepath, additional_dir, extension)

    def find_path(self, filepath: Union[str, Path], additional_dir=None, extension=None) -> Optional[Path]:
        return self._find_path_generic(filepath, additional_dir, extension)

    def glob(self, pattern: str) -> Iterator[Tuple[Path, Buffer]]:
        yield from self._glob_generic(pattern)


class SBoxDownloadsProvider(ContentProviderBase):

    @property
    def steam_id(self):
        return SteamAppId.SBOX_STEAM_ID

    def find_file(self, filepath: Union[str, Path], additional_dir=None, extension=None) -> Optional[Buffer]:
        return self._find_file_generic(filepath, additional_dir, extension)

    def find_path(self, filepath: Union[str, Path], additional_dir=None, extension=None) -> Optional[Path]:
        return self._find_path_generic(filepath, additional_dir, extension)

    def glob(self, pattern: str) -> Iterator[Tuple[Path, Buffer]]:
        yield from self._glob_generic(pattern)
