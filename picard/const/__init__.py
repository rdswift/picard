# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
#
# Copyright (C) 2007, 2014, 2016 Lukáš Lalinský
# Copyright (C) 2014, 2019-2022, 2024 Philipp Wolfer
# Copyright (C) 2014-2016, 2018-2021, 2023-2024 Laurent Monin
# Copyright (C) 2015 Ohm Patel
# Copyright (C) 2016 Rahul Raturi
# Copyright (C) 2016 Wieland Hoffmann
# Copyright (C) 2016-2017 Frederik “Freso” S. Olesen
# Copyright (C) 2017 Antonio Larrosa
# Copyright (C) 2017 Sambhav Kothari
# Copyright (C) 2018 Vishal Choudhary
# Copyright (C) 2018, 2021, 2023, 2025 Bob Swift
# Copyright (C) 2020 RomFouq
# Copyright (C) 2021 Gabriel Ferreira
# Copyright (C) 2021 Vladislav Karbovskii
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.


from collections import OrderedDict

from picard import PICARD_VERSION
from picard.const import appdirs
from picard.const.attributes import MB_ATTRIBUTES
from picard.i18n import N_


# Config directory
USER_DIR = appdirs.config_folder()
USER_PLUGIN_DIR = appdirs.plugin_folder()

# Network Cache default settings
CACHE_SIZE_DISPLAY_UNIT = 1000*1000

# AcoustID client API key
ACOUSTID_KEY = 'v8pQ6oyB'
ACOUSTID_URL = 'https://api.acoustid.org/v2'
FPCALC_NAMES = ['fpcalc', 'pyfpcalc']

# MB OAuth client credentials
MUSICBRAINZ_OAUTH_CLIENT_ID = 'jIqTXsN2WQvhpZXmsjo1ygxj62R9ww4X'
MUSICBRAINZ_OAUTH_CLIENT_SECRET = 'IVg2qnvErgX046Ptz3FsTxW4dbyQM9Jr'

# Cover art archive URL
CAA_URL = 'https://coverartarchive.org'

# Prepare documentation URLs
if PICARD_VERSION.identifier == 'final':
    DOCS_VERSION = "v{}.{}/".format(PICARD_VERSION.major, PICARD_VERSION.minor)
else:
    DOCS_VERSION = ""  # points to latest version
DOCS_LANGUAGE = 'en'
DOCS_SERVER_URL = "https://picard-docs.musicbrainz.org/"
DOCS_BASE_URL = DOCS_SERVER_URL + DOCS_VERSION + DOCS_LANGUAGE

MB_DOCS_BASE_URL = "https://musicbrainz.org/doc"

# URLs
PICARD_URLS = {
    'home':                    "https://picard.musicbrainz.org/",
    'license':                 "https://www.gnu.org/licenses/gpl-2.0.html",
    'documentation_server':    DOCS_SERVER_URL,     # Shows latest version and tries to match the user's language if available.
    'documentation':           DOCS_BASE_URL + "/",
    'troubleshooting':         DOCS_BASE_URL + "/troubleshooting/troubleshooting.html",
    'doc_options':             DOCS_BASE_URL + "/config/configuration.html",
    'doc_scripting':           DOCS_BASE_URL + "/extending/scripting.html",
    'doc_tags_from_filenames': DOCS_BASE_URL + "/usage/tags_from_file_names.html",
    'doc_naming_script_edit':  DOCS_BASE_URL + "/config/options_filerenaming_editor.html",
    'doc_cover_art_types':     MB_DOCS_BASE_URL + "/Cover_Art/Types",
    'plugins':                 "https://picard.musicbrainz.org/plugins/",
    'forum':                   "https://community.metabrainz.org/c/picard",
    'donate':                  "https://metabrainz.org/donate",
    'chromaprint':             "https://acoustid.org/chromaprint#download",
    'acoustid_apikey':         "https://acoustid.org/api-key",
    'acoustid_track':          "https://acoustid.org/track/",
    'mb_doc':                  MB_DOCS_BASE_URL + "/",
    'mb_doc_search_syntax':    MB_DOCS_BASE_URL + "/Indexed_Search_Syntax",
}

# Various Artists MBID
VARIOUS_ARTISTS_ID = '89ad4ac3-39f7-470e-963a-56509c546377'

# Artist alias types
ALIAS_TYPE_ARTIST_NAME_ID = '894afba6-2816-3c24-8072-eadb66bd04bc'
ALIAS_TYPE_LEGAL_NAME_ID = 'd4dcd0c0-b341-3612-a332-c0ce797b25cf'
ALIAS_TYPE_SEARCH_HINT_ID = '1937e404-b981-3cb7-8151-4c86ebfc8d8e'

# Special purpose track titles
SILENCE_TRACK_TITLE = '[silence]'
DATA_TRACK_TITLE = '[data track]'

# Release formats
RELEASE_FORMATS = {}
RELEASE_PRIMARY_GROUPS = {}
RELEASE_SECONDARY_GROUPS = {}
RELEASE_STATUS = {}
for k, v in MB_ATTRIBUTES.items():
    if k.startswith('DB:medium_format/name:'):
        RELEASE_FORMATS[v] = v
    elif k.startswith('DB:release_group_primary_type/name:'):
        RELEASE_PRIMARY_GROUPS[v] = v
    elif k.startswith('DB:release_group_secondary_type/name:'):
        RELEASE_SECONDARY_GROUPS[v] = v
    elif k.startswith('DB:release_status/name:'):
        RELEASE_STATUS[v] = v

# List of official musicbrainz servers - must support SSL for mblogin requests (such as collections).
MUSICBRAINZ_SERVERS = [
    'musicbrainz.org',
    'beta.musicbrainz.org',
]

# Plugins and Release Versions API
PLUGINS_API_BASE_URL = 'https://picard.musicbrainz.org/api/v2/'
PLUGINS_API = {
    'urls': {
        'plugins': PLUGINS_API_BASE_URL + 'plugins/',
        'download': PLUGINS_API_BASE_URL + 'download/',
        'releases': PLUGINS_API_BASE_URL + 'releases',
    },
}

# Maximum number of covers to draw in a stack in CoverArtThumbnail
MAX_COVERS_TO_STACK = 4

# Update levels available for automatic checking
PROGRAM_UPDATE_LEVELS = OrderedDict(
    [
        (
            0, {
                'name': 'stable',
                'title': N_("Stable releases only"),
            }
        ),
        (
            1, {
                'name': 'beta',
                'title': N_("Stable and Beta releases"),
            }
        ),
        (
            2, {
                'name': 'dev',
                'title': N_("Stable, Beta and Dev releases"),
            }
        ),
    ]
)

SCRIPT_LANGUAGE_VERSION = '1.1'

BROWSER_INTEGRATION_LOCALIP = '127.0.0.1'
BROWSER_INTEGRATION_LOCALHOST = BROWSER_INTEGRATION_LOCALIP
