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

from unittest.mock import (
    MagicMock,
    patch,
)

from test.picardtestcase import PicardTestCase

from picard.ui.options.dialog import OptionsDialog


class TestOptionsDialogPluginNotes(PicardTestCase):
    """Plugin notes must not appear before the options dialog is visible."""

    def _make_dialog_stub(self, visible=False):
        dialog = MagicMock()
        dialog.isVisible.return_value = visible
        item = MagicMock()
        page = MagicMock()
        page.NAME = 'plugins'
        page.loaded = True
        dialog.ui.pages_tree.selectedItems.return_value = [item]
        dialog.item_to_page = {item: MagicMock(NAME='plugins')}
        dialog._load_page.return_value = page
        dialog._current_page.return_value = page
        dialog._pending_plugin_notes = False
        dialog._show_plugin_notes = lambda: OptionsDialog._show_plugin_notes(dialog)
        dialog._defer_plugin_notes = lambda: OptionsDialog._defer_plugin_notes(dialog)
        return dialog

    @patch('picard.ui.options.dialog.PluginNotesDialog')
    def test_notes_not_created_before_options_dialog_is_visible(self, notes_dialog_cls):
        notes_dialog_cls.is_hidden.return_value = False
        dialog = self._make_dialog_stub(visible=False)

        OptionsDialog.switch_page(dialog)

        notes_dialog_cls.assert_not_called()
        self.assertTrue(dialog._pending_plugin_notes)

    @patch('picard.ui.options.dialog.PluginNotesDialog')
    def test_notes_shown_after_options_dialog_is_visible(self, notes_dialog_cls):
        notes_dialog_cls.is_hidden.return_value = False
        dialog = self._make_dialog_stub(visible=True)
        dialog._pending_plugin_notes = True

        OptionsDialog._show_plugin_notes(dialog)

        notes_dialog_cls.assert_called_once_with(dialog)
        notes_dialog_cls.return_value.show.assert_called_once_with()
        self.assertFalse(dialog._pending_plugin_notes)

    @patch('picard.ui.options.dialog.PluginNotesDialog')
    def test_pending_notes_skipped_if_page_changed(self, notes_dialog_cls):
        notes_dialog_cls.is_hidden.return_value = False
        dialog = self._make_dialog_stub(visible=True)
        dialog._current_page.return_value = MagicMock(NAME='metadata')

        OptionsDialog._show_plugin_notes(dialog)

        notes_dialog_cls.assert_not_called()

    @patch('picard.ui.options.dialog.PluginNotesDialog')
    def test_hidden_notes_not_created(self, notes_dialog_cls):
        notes_dialog_cls.is_hidden.return_value = True
        dialog = self._make_dialog_stub(visible=True)

        OptionsDialog._show_plugin_notes(dialog)

        notes_dialog_cls.assert_not_called()

    @patch('picard.ui.options.dialog.QtCore.QTimer.singleShot')
    def test_deferred_notes_run_on_event_loop(self, single_shot):
        dialog = self._make_dialog_stub(visible=True)

        OptionsDialog._defer_plugin_notes(dialog)

        single_shot.assert_called_once_with(200, dialog._show_plugin_notes)
        self.assertFalse(dialog._pending_plugin_notes)
