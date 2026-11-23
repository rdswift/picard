# Picard, the next-generation MusicBrainz tagger
#
# Copyright (C) 2026 Bob Swift
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.


from PyQt6 import QtWidgets

from picard.i18n import (
    N_,
    gettext as _,
)

from picard.ui.dialogs.donotshowagainmessagebox import DoNotShowAgainMessageBox


class PluginNotesDialog(DoNotShowAgainMessageBox):
    """Dialog for displaying notes specific to the plugins options page."""

    KEY = 'plugin_page_notes'
    TITLE = N_("Plugin Page Notes")

    def __init__(self, parent):
        text = _(
            "<p>"
            "Picard's functionality can be extended through the use of plugins. "
            "Plugins can be installed/uninstalled and enabled/disabled from the "
            "Options menu. Installed plugins are loaded during the startup of "
            "Picard, and are made available to the program."
            "</p><p>"
            "The Plugins page under the Options menu differs from all other option "
            "settings pages in that any changes made or actions taken on this page "
            "are processed immediately and are not reverted if the user clicks "
            "\"Cancel\"."
            "</p><p>"
            "<strong>Be aware that installing plugins from unknown sources may pose "
            "security risks. Only install plugins from sources you trust!</strong>"
            "</p>"
        )

        super().__init__(parent, text=text)

        pixmap = self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning).pixmap(24, 24)
        self.setIconPixmap(pixmap)
