# -*- coding: utf-8 -*-
#
# Picard, the next-generation MusicBrainz tagger
#
# Copyright (C) 2019 Zenara Daley
# Copyright (C) 2019-2021, 2023-2024 Philipp Wolfer
# Copyright (C) 2019-2022 Laurent Monin
# Copyright (C) 2020 raingloom
# Copyright (C) 2021 Sophist-UK
# Copyright (C) 2024 Giorgio Fontanive
# Copyright (C) 2024 Suryansh Shakya
# Copyright (C) 2024 YohayAiTe
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


import os.path

import mutagen

from test.picardtestcase import PicardTestCase

from picard import config
from picard.file import File
from picard.formats import (
    id3,
    open_,
)
from picard.metadata import Metadata

from .common import (
    CommonTests,
    load_metadata,
    load_raw,
    save_and_load_metadata,
    save_metadata,
    save_raw,
    skipUnlessTestfile,
)
from .coverart import CommonCoverArtTests


# prevent unittest to run tests in those classes
class CommonId3Tests:

    class Id3TestCase(CommonTests.TagFormatsTestCase):

        def setup_tags(self):
            # Note: in ID3v23, the original date can only be stored as a year.
            super().setup_tags()
            self.set_tags({
                'originaldate': '1980'
            })
            self.unsupported_tags['r128_album_gain'] = '-2857'
            self.unsupported_tags['r128_track_gain'] = '-2857'

        @skipUnlessTestfile
        def test_id3_freeform_delete(self):
            metadata = Metadata(self.tags)
            metadata['Foo'] = 'Foo'
            original_metadata = save_and_load_metadata(self.filename, metadata)
            del metadata['Foo']
            new_metadata = save_and_load_metadata(self.filename, metadata)

            self.assertIn('Foo', original_metadata)
            self.assertNotIn('Foo', new_metadata)

        @skipUnlessTestfile
        def test_id3_ufid_delete(self):
            metadata = Metadata(self.tags)
            metadata['musicbrainz_recordingid'] = "Foo"
            original_metadata = save_and_load_metadata(self.filename, metadata)
            del metadata['musicbrainz_recordingid']
            new_metadata = save_and_load_metadata(self.filename, metadata)

            self.assertIn('musicbrainz_recordingid', original_metadata)
            self.assertNotIn('musicbrainz_recordingid', new_metadata)

        @skipUnlessTestfile
        def test_id3_multiple_freeform_delete(self):
            metadata = Metadata(self.tags)
            metadata['Foo'] = 'Foo'
            metadata['Bar'] = 'Foo'
            metadata['FooBar'] = 'Foo'
            original_metadata = save_and_load_metadata(self.filename, metadata)
            del metadata['Foo']
            del metadata['Bar']
            new_metadata = save_and_load_metadata(self.filename, metadata)

            self.assertIn('Foo', original_metadata)
            self.assertIn('Bar', original_metadata)
            self.assertIn('FooBar', original_metadata)
            self.assertNotIn('Foo', new_metadata)
            self.assertNotIn('Bar', new_metadata)
            self.assertIn('FooBar', new_metadata)

        @skipUnlessTestfile
        def test_id3_rename_freetext_delete(self):
            tags = mutagen.id3.ID3Tags()
            tags.add(mutagen.id3.TXXX(desc='Work', text='foo'))
            save_raw(self.filename, tags)
            raw_metadata = load_raw(self.filename)
            self.assertIn('TXXX:Work', raw_metadata)

            metadata = Metadata()
            metadata.delete('work')
            new_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertNotIn('work', new_metadata)
            raw_metadata = load_raw(self.filename)
            self.assertNotIn('TXXX:Work', raw_metadata)
            self.assertNotIn('TXXX:WORK', raw_metadata)

        @skipUnlessTestfile
        def test_id3_freetext_ci_delete(self):
            # No matter which of the names below gets deleted it always
            # should remove all of them
            tag_name_variants = [
                'replaygain_album_gain',
                'REPLAYGAIN_ALBUM_GAIN',
                'Replaygain_Album_Gain',
            ]

            for tag_in_test in tag_name_variants:
                tags = mutagen.id3.ID3Tags()
                for tag in tag_name_variants:
                    tags.add(mutagen.id3.TXXX(desc=tag, text='foo'))
                save_raw(self.filename, tags)
                raw_metadata = load_raw(self.filename)
                for tag in tag_name_variants:
                    self.assertIn('TXXX:' + tag, raw_metadata)

                metadata = Metadata()
                metadata.delete(tag_in_test)
                save_metadata(self.filename, metadata)
                raw_metadata = load_raw(self.filename)
                for tag in tag_name_variants:
                    self.assertNotIn('TXXX:' + tag, raw_metadata)

        @skipUnlessTestfile
        def test_id3_metadata_tofn(self):
            metadata = Metadata(self.tags)
            metadata = save_and_load_metadata(self.filename, metadata)

            self.assertIn('originalfilename', metadata)
            self.assertEqual(metadata['originalfilename'], "Foo")

        @skipUnlessTestfile
        def test_performer_duplication(self):

            config.setting['write_id3v23'] = True
            metadata = Metadata({
                'album': 'Foo',
                'artist': 'Foo',
                'performer:piano': 'Foo',
                'title': 'Foo',
            })
            original_metadata = save_and_load_metadata(self.filename, metadata)
            new_metadata = save_and_load_metadata(self.filename, original_metadata)

            self.assertEqual(len(new_metadata['performer:piano']), len(original_metadata['performer:piano']))

        @skipUnlessTestfile
        def test_performer_no_role_tmcl(self):
            metadata = Metadata({
                'performer': 'Performer',
                'performer:piano': 'Performer Piano',
            })
            save_metadata(self.filename, metadata)
            raw_metadata = load_raw(self.filename)
            self.assertIn(['piano', 'Performer Piano'], raw_metadata['TMCL'].people)
            self.assertIn(['performer', 'Performer'], raw_metadata['TMCL'].people)
            self.assertNotIn('TXXX:performer', raw_metadata)

        @skipUnlessTestfile
        def test_performer_no_role_tipl(self):
            config.setting['write_id3v23'] = True
            metadata = Metadata({
                'performer': 'Performer',
                'performer:piano': 'Performer Piano',
            })
            save_metadata(self.filename, metadata)
            raw_metadata = load_raw(self.filename)
            self.assertIn(['piano', 'Performer Piano'], raw_metadata['TIPL'].people)
            self.assertIn(['performer', 'Performer'], raw_metadata['TIPL'].people)
            self.assertNotIn('TXXX:performer', raw_metadata)

        @skipUnlessTestfile
        def test_comment_delete(self):
            metadata = Metadata(self.tags)
            metadata['comment:bar'] = 'Foo'
            metadata['comment:XXX:withlang'] = 'Foo'
            original_metadata = save_and_load_metadata(self.filename, metadata)
            del metadata['comment:bar']
            del metadata['comment:XXX:withlang']
            new_metadata = save_and_load_metadata(self.filename, metadata)

            self.assertIn('comment:foo', original_metadata)
            self.assertIn('comment:bar', original_metadata)
            self.assertIn('comment:XXX:withlang', original_metadata)
            self.assertIn('comment:foo', new_metadata)
            self.assertNotIn('comment:bar', new_metadata)
            self.assertNotIn('comment:XXX:withlang', new_metadata)

        @skipUnlessTestfile
        def test_id3v23_simple_tags(self):
            config.setting['write_id3v23'] = True
            metadata = Metadata(self.tags)
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            for (key, value) in self.tags.items():
                self.assertEqual(loaded_metadata[key], value, '%s: %r != %r' % (key, loaded_metadata[key], value))

        @property
        def itunes_grouping_metadata(self):
            metadata = Metadata()
            metadata['grouping'] = 'The Grouping'
            metadata['work'] = 'The Work'
            return metadata

        @skipUnlessTestfile
        def test_standard_grouping(self):
            metadata = self.itunes_grouping_metadata

            config.setting['itunes_compatible_grouping'] = False
            loaded_metadata = save_and_load_metadata(self.filename, metadata)

            self.assertEqual(loaded_metadata['grouping'], metadata['grouping'])
            self.assertEqual(loaded_metadata['work'], metadata['work'])

        @skipUnlessTestfile
        def test_itunes_compatible_grouping(self):
            metadata = self.itunes_grouping_metadata

            config.setting['itunes_compatible_grouping'] = True
            loaded_metadata = save_and_load_metadata(self.filename, metadata)

            self.assertEqual(loaded_metadata['grouping'], metadata['grouping'])
            self.assertEqual(loaded_metadata['work'], metadata['work'])

        @skipUnlessTestfile
        def test_always_read_grp1(self):
            metadata = self.itunes_grouping_metadata

            config.setting['itunes_compatible_grouping'] = True
            save_metadata(self.filename, metadata)
            config.setting['itunes_compatible_grouping'] = False
            loaded_metadata = load_metadata(self.filename)

            self.assertIn(metadata['grouping'], loaded_metadata['grouping'])
            self.assertIn(metadata['work'], loaded_metadata['grouping'])
            self.assertEqual(loaded_metadata['work'], '')

        @skipUnlessTestfile
        def test_always_read_txxx_work(self):
            metadata = self.itunes_grouping_metadata

            config.setting['itunes_compatible_grouping'] = False
            save_metadata(self.filename, metadata)
            config.setting['itunes_compatible_grouping'] = True
            loaded_metadata = load_metadata(self.filename)

            self.assertIn(metadata['grouping'], loaded_metadata['work'])
            self.assertIn(metadata['work'], loaded_metadata['work'])
            self.assertEqual(loaded_metadata['grouping'], '')

        @skipUnlessTestfile
        def test_save_itunnorm_tag(self):
            config.setting['clear_existing_tags'] = True
            iTunNORM = '00001E86 00001E86 0000A2A3 0000A2A3 000006A6 000006A6 000078FA 000078FA 00000211 00000211'
            metadata = Metadata()
            metadata['comment:iTunNORM'] = iTunNORM
            new_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertEqual(new_metadata['comment:iTunNORM'], iTunNORM)

        @skipUnlessTestfile
        def test_delete_itun_tags(self):
            metadata = Metadata()
            metadata['comment:iTunNORM'] = '00001E86 00001E86 0000A2A3 0000A2A3 000006A6 000006A6 000078FA 000078FA 00000211 00000211'
            metadata['comment:iTunPGAP'] = '1'
            new_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertIn('comment:iTunNORM', new_metadata)
            self.assertIn('comment:iTunPGAP', new_metadata)
            del metadata['comment:iTunNORM']
            del metadata['comment:iTunPGAP']
            new_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertNotIn('comment:iTunNORM', new_metadata)
            self.assertNotIn('comment:iTunPGAP', new_metadata)

        def test_rename_txxx_tags(self):
            file_path = os.path.join('test', 'data', 'test-id3-rename-tags.mp3')
            filename = self.copy_file_tmp(file_path, '.mp3')
            raw_metadata = load_raw(filename)
            self.assertIn('TXXX:Artists', raw_metadata)
            self.assertNotIn('TXXX:ARTISTS', raw_metadata)
            self.assertIn('TXXX:Work', raw_metadata)
            self.assertNotIn('TXXX:WORK', raw_metadata)
            metadata = load_metadata(filename)
            self.assertEqual(metadata['artists'], 'Artist1; Artist2')
            self.assertNotIn('Artists', metadata)
            self.assertEqual(metadata['work'], 'The Work')
            self.assertNotIn('Work', metadata)
            save_metadata(filename, metadata)
            raw_metadata = load_raw(filename)
            self.assertNotIn('TXXX:Artists', raw_metadata)
            self.assertIn('TXXX:ARTISTS', raw_metadata)
            self.assertNotIn('TXXX:Work', raw_metadata)
            self.assertIn('TXXX:WORK', raw_metadata)

        def test_preserve_unchanged_tags_v23(self):
            config.setting['write_id3v23'] = True
            self.test_preserve_unchanged_tags()

        @skipUnlessTestfile
        def test_replaygain_tags_case_insensitive(self):
            tags = mutagen.id3.ID3Tags()
            tags.add(mutagen.id3.TXXX(desc='replaygain_album_gain', text='-6.48 dB'))
            tags.add(mutagen.id3.TXXX(desc='Replaygain_Album_Peak', text='0.978475'))
            tags.add(mutagen.id3.TXXX(desc='replaygain_album_range', text='7.84 dB'))
            tags.add(mutagen.id3.TXXX(desc='replaygain_track_gain', text='-6.16 dB'))
            tags.add(mutagen.id3.TXXX(desc='REPLAYGAIN_track_peak', text='0.976991'))
            tags.add(mutagen.id3.TXXX(desc='REPLAYGAIN_TRACK_RANGE', text='8.22 dB'))
            tags.add(mutagen.id3.TXXX(desc='replaygain_reference_loudness', text='-18.00 LUFS'))
            save_raw(self.filename, tags)
            loaded_metadata = load_metadata(self.filename)
            for (key, value) in self.replaygain_tags.items():
                self.assertEqual(loaded_metadata[key], value, '%s: %r != %r' % (key, loaded_metadata[key], value))

        @skipUnlessTestfile
        def test_ci_tags_save(self):
            tag_name_variants = [
                'replaygain_album_gain',
                'REPLAYGAIN_ALBUM_GAIN',
                'Replaygain_Album_Gain',
            ]

            for tag in tag_name_variants:
                metadata = Metadata({tag: 'foo'})
                loaded_metadata = save_and_load_metadata(self.filename, metadata)
                self.assertEqual('foo', loaded_metadata['replaygain_album_gain'])

        @skipUnlessTestfile
        def test_ci_tags_preserve_case(self):
            # Ensure values are not duplicated on repeated save and are saved
            # case preserving.
            tags = mutagen.id3.ID3Tags()
            tags.add(mutagen.id3.TXXX(desc='Replaygain_Album_Peak', text='0.978475'))
            save_raw(self.filename, tags)
            loaded_metadata = load_metadata(self.filename)
            loaded_metadata['replaygain_album_peak'] = '1.0'
            save_metadata(self.filename, loaded_metadata)
            raw_metadata = load_raw(self.filename)
            self.assertIn('TXXX:Replaygain_Album_Peak', raw_metadata)
            self.assertEqual(
                raw_metadata['TXXX:Replaygain_Album_Peak'].text[0],
                loaded_metadata['replaygain_album_peak'])
            self.assertEqual(1, len(raw_metadata['TXXX:Replaygain_Album_Peak'].text))
            self.assertNotIn('TXXX:REPLAYGAIN_ALBUM_PEAK', raw_metadata)

        @skipUnlessTestfile
        def test_lyrics_with_description(self):
            metadata = Metadata({'lyrics:foo': 'bar'})
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertEqual(metadata['lyrics:foo'], loaded_metadata['lyrics:foo'])

        @skipUnlessTestfile
        def test_syncedlyrics_preserve_language_and_description(self):
            metadata = Metadata({'syncedlyrics': '[00:00.000]<00:00.000>foo1'})
            metadata.add('syncedlyrics:deu:desc', '[00:00.000]<00:00.000>foo2')
            metadata.add('syncedlyrics:ita', '[00:00.000]<00:00.000>foo3')
            metadata.add('syncedlyrics::desc', '[00:00.000]<00:00.000>foo4')
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertEqual(metadata['syncedlyrics'], loaded_metadata['syncedlyrics:eng'])
            self.assertEqual(metadata['syncedlyrics:deu:desc'], loaded_metadata['syncedlyrics:deu:desc'])
            self.assertEqual(metadata['syncedlyrics:ita'], loaded_metadata['syncedlyrics:ita'])
            self.assertEqual(metadata['syncedlyrics::desc'], loaded_metadata['syncedlyrics:eng:desc'])

        @skipUnlessTestfile
        def test_syncedlyrics_delete(self):
            metadata = Metadata({'syncedlyrics': '[00:00.000]<00:00.000>foo1'})
            metadata.delete('syncedlyrics:eng')
            save_metadata(self.filename, metadata)
            raw_metadata = load_raw(self.filename)
            self.assertNotIn('syncedlyrics:eng', raw_metadata)

        @skipUnlessTestfile
        def test_invalid_track_and_discnumber(self):
            metadata = Metadata({
                'discnumber': 'notanumber',
                'tracknumber': 'notanumber',
            })
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertNotIn('discnumber', loaded_metadata)
            self.assertNotIn('tracknumber', loaded_metadata)

        @skipUnlessTestfile
        def test_save_explicit_id3_frames(self):
            metadata = Metadata({
                '~id3:TXXX:foo': 'bar',
                '~id3:TOWN': 'owner'
            })
            save_metadata(self.filename, metadata)
            raw_metadata = load_raw(self.filename)
            self.assertIn('TXXX:foo', raw_metadata)
            self.assertEqual('bar', raw_metadata['TXXX:foo'])
            self.assertEqual('owner', raw_metadata['TOWN'])

        @skipUnlessTestfile
        def test_delete_explicit_id3_frames(self):
            tags = mutagen.id3.ID3Tags()
            tags.add(mutagen.id3.TOWN(text='bar'))
            tags.add(mutagen.id3.TXXX(desc='foo', text='bar1'))
            tags.add(mutagen.id3.TXXX(desc='foo', text='bar2'))
            save_raw(self.filename, tags)
            raw_metadata = load_raw(self.filename)
            self.assertIn('TOWN', raw_metadata)
            self.assertIn('TXXX:foo', raw_metadata)
            metadata = Metadata()
            metadata.delete('~id3:TOWN')
            metadata.delete('~id3:TXXX:foo')
            metadata.delete('~id3:NOTAFRAME')
            save_metadata(self.filename, metadata)
            raw_metadata = load_raw(self.filename)
            self.assertNotIn('TOWN', raw_metadata)
            self.assertNotIn('TXXX:foo', raw_metadata)

        @skipUnlessTestfile
        def test_delete_tipl(self):
            tags = mutagen.id3.ID3Tags()
            tags.add(mutagen.id3.TIPL(people=[
                ['mix', 'mixer1'],
                ['mix', 'mixer2'],
                ['producer', 'producer1'],
            ]))
            save_raw(self.filename, tags)
            metadata = Metadata()
            metadata.delete('mixer')
            save_metadata(self.filename, metadata)
            raw_metadata = load_raw(self.filename)
            people = raw_metadata['TIPL'].people
            self.assertIn(['producer', 'producer1'], people)
            self.assertNotIn(['mix', 'mixer1'], people)
            self.assertNotIn(['mix', 'mixer2'], people)
            self.assertEqual(1, len(people))

        @skipUnlessTestfile
        def test_load_conflicting_txxx_tags(self):
            tags = mutagen.id3.ID3Tags()
            tags.add(mutagen.id3.TXXX(desc='title', text='foo'))
            save_raw(self.filename, tags)
            loaded_metadata = load_metadata(self.filename)
            self.assertEqual('foo', loaded_metadata['~id3:TXXX:title'])

        @skipUnlessTestfile
        def test_license_single_url(self):
            metadata = Metadata({
                'license': 'http://example.com'
            })
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertEqual(metadata['license'], loaded_metadata['license'])
            raw_metadata = load_raw(self.filename)
            self.assertEqual(metadata['license'], raw_metadata['WCOP'])

        @skipUnlessTestfile
        def test_license_single_non_url(self):
            metadata = Metadata({
                'license': 'foo'
            })
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertEqual(metadata['license'], loaded_metadata['license'])
            raw_metadata = load_raw(self.filename)
            self.assertEqual(metadata['license'], raw_metadata['TXXX:LICENSE'])

        @skipUnlessTestfile
        def test_license_multi_url(self):
            metadata = Metadata({
                'license': [
                    'http://example.com/1',
                    'http://example.com/2',
                ]
            })
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertEqual(metadata['license'], loaded_metadata['license'])
            raw_metadata = load_raw(self.filename)
            self.assertEqual(
                set(metadata.getall('license')),
                set(raw_metadata.get('TXXX:LICENSE').text))

        @skipUnlessTestfile
        def test_license_wcop_and_txxx(self):
            tags = mutagen.id3.ID3Tags()
            tags.add(mutagen.id3.WCOP(url='http://example.com/1'))
            tags.add(mutagen.id3.TXXX(desc='license', text='http://example.com/2'))
            save_raw(self.filename, tags)
            loaded_metadata = load_metadata(self.filename)
            loaded_licenses = loaded_metadata.getall('license')
            self.assertEqual(2, len(loaded_licenses))
            self.assertIn('http://example.com/1', loaded_licenses)
            self.assertIn('http://example.com/2', loaded_licenses)

        @skipUnlessTestfile
        def test_license_upgrade_wcop(self):
            tags = mutagen.id3.ID3Tags()
            tags.add(mutagen.id3.WCOP(url='http://example.com/1'))
            save_raw(self.filename, tags)
            metadata = load_metadata(self.filename)
            self.assertEqual('http://example.com/1', metadata['license'])
            metadata.add('license', 'http://example.com/2')
            save_metadata(self.filename, metadata)
            raw_metadata = load_raw(self.filename)
            self.assertNotIn('WCOP', raw_metadata)
            loaded_licenses = [url for url in raw_metadata['TXXX:LICENSE']]
            self.assertEqual(['http://example.com/1', 'http://example.com/2'], loaded_licenses)

        @skipUnlessTestfile
        def test_license_downgrade_wcop(self):
            tags = mutagen.id3.ID3Tags()
            licenses = ['http://example.com/1', 'http://example.com/2']
            tags.add(mutagen.id3.TXXX(desc='LICENSE', text=licenses))
            save_raw(self.filename, tags)
            raw_metadata = load_raw(self.filename)
            metadata = load_metadata(self.filename)
            self.assertEqual(licenses, metadata.getall('license'))
            metadata['license'] = 'http://example.com/1'
            save_metadata(self.filename, metadata)
            raw_metadata = load_raw(self.filename)
            self.assertEqual('http://example.com/1', raw_metadata['WCOP'])
            self.assertNotIn('TXXX:LICENSE', raw_metadata)

        @skipUnlessTestfile
        def test_license_delete(self):
            tags = mutagen.id3.ID3Tags()
            tags.add(mutagen.id3.WCOP(url='http://example.com/1'))
            tags.add(mutagen.id3.TXXX(desc='LICENSE', text='http://example.com/2'))
            save_raw(self.filename, tags)
            metadata = load_metadata(self.filename)
            del metadata['license']
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertNotIn('license', loaded_metadata)

        @skipUnlessTestfile
        def test_woar_not_duplicated(self):
            metadata = Metadata({
                'website': 'http://example.com/1'
            })
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertEqual(metadata['website'], loaded_metadata['website'])
            metadata['website'] = 'http://example.com/2'
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertEqual(metadata['website'], loaded_metadata['website'])

        @skipUnlessTestfile
        def test_woar_delete(self):
            metadata = Metadata({
                'website': 'http://example.com/1'
            })
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertEqual(metadata['website'], loaded_metadata['website'])
            del metadata['website']
            loaded_metadata = save_and_load_metadata(self.filename, metadata)
            self.assertNotIn('website', loaded_metadata)

        @skipUnlessTestfile
        def test_rating_email_non_latin1(self):
            for rating in range(6):
                config.setting['rating_user_email'] = 'foo€'
                rating = '3'
                metadata = Metadata({'~rating': rating})
                loaded_metadata = save_and_load_metadata(self.filename, metadata)
                self.assertEqual(loaded_metadata['~rating'], rating, '~rating: %r != %r' % (loaded_metadata['~rating'], rating))

        @skipUnlessTestfile
        def test_unchanged_metadata(self):
            self.set_config_values({
                'compare_ignore_tags': [],
                'write_id3v23': True,
            })
            file = open_(self.filename)
            file.orig_metadata = Metadata({
                'album': 'somealbum',
                'title': 'sometitle',
                'date': '2021',
                'originaldate': '2021',
                'artists': 'foo/bar',
            })
            file.metadata = Metadata({
                'album': 'somealbum',
                'title': 'sometitle',
                'date': '2021-12',
                'originaldate': '2021-12-04',
                'artists': ['foo', 'bar'],
            })
            file.state = File.NORMAL
            file.update(signal=False)
            self.assertEqual(file.similarity, 1.0)
            self.assertEqual(file.state, File.NORMAL)

        @skipUnlessTestfile
        def test_releasedate_v23(self):
            config.setting['write_id3v23'] = True
            metadata = Metadata({
                'releasedate': '2023-04-28',
            })
            save_metadata(self.filename, metadata)
            raw_metadata = load_raw(self.filename)
            self.assertEqual(metadata['releasedate'], raw_metadata['TXXX:RELEASEDATE'])

        @skipUnlessTestfile
        def test_releasedate_v24(self):
            config.setting['write_id3v23'] = False
            metadata = Metadata({
                'releasedate': '2023-04-28',
            })
            save_metadata(self.filename, metadata)
            raw_metadata = load_raw(self.filename)
            self.assertEqual(metadata['releasedate'], raw_metadata['TDRL'])


class MP3Test(CommonId3Tests.Id3TestCase):
    testfile = 'test.mp3'
    supports_ratings = True
    expected_info = {
        'length': 156,
        '~channels': '2',
        '~sample_rate': '44100',
        '~filesize': '2760',
    }
    unexpected_info = ['~video']

    @skipUnlessTestfile
    def test_remove_apev2(self):
        # Add APEv2 tags
        apev2_tags = mutagen.apev2.APEv2()
        apev2_tags['Title'] = 'foo'
        apev2_tags.save(self.filename)
        self.assertEqual('foo', mutagen.apev2.APEv2(self.filename)['Title'])
        config.setting['remove_ape_from_mp3'] = False
        save_metadata(self.filename, Metadata())
        self.assertEqual('foo', mutagen.apev2.APEv2(self.filename)['Title'])
        config.setting['remove_ape_from_mp3'] = True
        save_metadata(self.filename, Metadata())
        self.assertRaises(mutagen.apev2.APENoHeaderError, mutagen.apev2.APEv2, self.filename)

    @skipUnlessTestfile
    def test_remove_apev2_no_existing_tags(self):
        self.assertRaises(mutagen.apev2.APENoHeaderError, mutagen.apev2.APEv2, self.filename)
        config.setting['remove_ape_from_mp3'] = True
        save_metadata(self.filename, Metadata())
        self.assertRaises(mutagen.apev2.APENoHeaderError, mutagen.apev2.APEv2, self.filename)


class TTATest(CommonId3Tests.Id3TestCase):
    testfile = 'test.tta'
    supports_ratings = True
    expected_info = {
        'length': 82,
        '~sample_rate': '44100',
        '~filesize': '2300',
    }
    unexpected_info = ['~video']


class DSFTest(CommonId3Tests.Id3TestCase):
    testfile = 'test.dsf'
    supports_ratings = True
    expected_info = {
        'length': 10,
        '~channels': '2',
        '~sample_rate': '5644800',
        '~bitrate': '11289.6',
        '~bits_per_sample': '1',
        '~filesize': '112988',
    }
    unexpected_info = ['~video']


if id3.DSDIFFFile:
    class DSDIFFTest(CommonId3Tests.Id3TestCase):
        testfile = 'test-dsd.dff'
        supports_ratings = True
        expected_info = {
            'length': 10,
            '~channels': '2',
            '~sample_rate': '5644800',
            '~bitrate': '11289.6',
            '~bits_per_sample': '1',
            '~filesize': '14242',
        }
        unexpected_info = ['~video']

    class DSDIFFDSTTest(CommonId3Tests.Id3TestCase):
        testfile = 'test-dst.dff'
        supports_ratings = True
        expected_info = {
            'length': 0,
            '~channels': '2',
            '~sample_rate': '5644800',
            '~bits_per_sample': '1',
            '~filesize': '2214',
        }
        unexpected_info = ['~video']


class AIFFTest(CommonId3Tests.Id3TestCase):
    testfile = 'test.aiff'
    supports_ratings = False
    expected_info = {
        'length': 82,
        '~channels': '2',
        '~sample_rate': '44100',
        '~bitrate': '1411.2',
        '~filesize': '14662',
    }
    unexpected_info = ['~video']


class Id3UtilTest(PicardTestCase):
    def test_id3encoding_from_config(self):
        self.assertEqual(id3.Id3Encoding.LATIN1, id3.Id3Encoding.from_config('iso-8859-1'))
        self.assertEqual(id3.Id3Encoding.UTF16, id3.Id3Encoding.from_config('utf-16'))
        self.assertEqual(id3.Id3Encoding.UTF8, id3.Id3Encoding.from_config('utf-8'))

    def test_id3text(self):
        teststring = '日本語testÖäß'
        self.assertEqual(id3.id3text(teststring, id3.Id3Encoding.LATIN1), '???testÖäß')
        self.assertEqual(id3.id3text(teststring, id3.Id3Encoding.UTF16), teststring)
        self.assertEqual(id3.id3text(teststring, id3.Id3Encoding.UTF16BE), teststring)
        self.assertEqual(id3.id3text(teststring, id3.Id3Encoding.UTF8), teststring)


class Mp3CoverArtTest(CommonCoverArtTests.CoverArtTestCase):
    testfile = 'test.mp3'


class ID3FileTest(PicardTestCase):

    def setUp(self):
        super().setUp()
        self.file = id3.ID3File('somepath/somefile.mp3')
        config.setting['write_id3v23'] = False
        config.setting['id3v23_join_with'] = ' / '
        self.file.metadata['artist'] = ['foo', 'bar']
        self.file.metadata['originaldate'] = '2020-04-01'
        self.file.metadata['date'] = '2021-04-01'

    def test_format_specific_metadata_v24(self):
        metadata = self.file.metadata
        for name, values in metadata.rawitems():
            self.assertEqual(values, self.file.format_specific_metadata(metadata, name))

    def test_format_specific_metadata_v23(self):
        config.setting['write_id3v23'] = True
        metadata = self.file.metadata
        self.assertEqual(['foo / bar'], self.file.format_specific_metadata(metadata, 'artist'))
        self.assertEqual(['2020'], self.file.format_specific_metadata(metadata, 'originaldate'))
        self.assertEqual(['2021-04-01'], self.file.format_specific_metadata(metadata, 'date'))

    def test_format_specific_metadata_v23_incomplete_date(self):
        config.setting['write_id3v23'] = True
        metadata = self.file.metadata
        metadata['date'] = '2021-04'
        self.assertEqual(['2021'], self.file.format_specific_metadata(metadata, 'date'))

    def test_format_specific_metadata_override_settings(self):
        settings = {
            'write_id3v23': True,
            'id3v23_join_with': '; ',
        }
        metadata = self.file.metadata
        self.assertEqual(['foo; bar'], self.file.format_specific_metadata(metadata, 'artist', settings))

    def test_syncedlyrics_converting_to_lrc(self):
        sylts = (
            [("Test", 0), ("normal\n", 500), ("behaviour", 1000)],
            [("Test", 0), ("syl", 10), ("la", 20), ("bles", 30)],
            [("Test newline\nin the middle", 0), ("of the text", 1000)],
            [("Test empty lyrics at the end\n", 0), ("", 1000)],
            [("Test timestamp estimation", 0), ("in the\nlast phrase", 1000)])
        correct_lrcs = (
            "[00:00.000]<00:00.000>Test<00:00.500>normal\n[00:01.000]<00:01.000>behaviour",
            "[00:00.000]<00:00.000>Test<00:00.010>syl<00:00.020>la<00:00.030>bles",
            "[00:00.000]<00:00.000>Test newline\n[00:00.480]in the middle<00:01.000>of the text",
            "[00:00.000]<00:00.000>Test empty lyrics at the end\n[00:01.000]<00:01.000>",
            "[00:00.000]<00:00.000>Test timestamp estimation<00:01.000>in the\n[00:01.352]last phrase")
        for sylt, correct_lrc in zip(sylts, correct_lrcs):
            lrc = self.file._parse_sylt_text(sylt, 2)
            self.assertEqual(lrc, correct_lrc)

    def test_syncedlyrics_converting_to_sylt(self):
        lrcs = (
            "[00:00.000]<00:00.000>Test<00:00.500>normal\n[00:00.750]<00:01.000>behaviour",
            "[00:00.000]Test lyrics with\n[01:00.000]only line time stamps",
            "<00:00.000>Test lyrics with<01:00.000>only syllable time stamps",
            "[00:00.000]<00:00.000>Test extra\n<00:00.750>[00:00.750]<00:00.750>timestamp<00:01.500>",
            "[00:01.00]<00:01.00>Test lyrics with two\n[00:01.75]<00:01.75>digit ms",
            "[01:01.0]<01:01.000>Test lyrics with different\n[01:01.8]<01:01.7506>digit ms",
            "[2:1.0]<2:1.0>Test lyrics with single digits\n[2:2]<2:2>or no ms",
            "[300:1.000]<300:1.000>Test lyrics with long minutes",
            "Test invalid[00:00.000]input\nTest invalid[00:01.000]input",
            "Test lyrics with no timestamps")
        correct_sylts = (
            [("Test", 0), ("normal\n", 500), ("behaviour", 1000)],
            [("Test lyrics with\n", 0), ("only line time stamps", 60 * 1000)],
            [("Test lyrics with", 0), ("only syllable time stamps", 60 * 1000)],
            [("Test extra\n", 0), ("timestamp", 750), ("", 1500)],
            [("Test lyrics with two\n", 1000), ("digit ms", 1750)],
            [("Test lyrics with different\n", 61000), ("digit ms", 61750)],
            [("Test lyrics with single digits\n", 121000), ("or no ms", 122000)],
            [("Test lyrics with long minutes", (300*60+1)*1000)],
            [("input\nTest invalid", 0), ("input", 1000)],
            [])
        for lrc, correct_sylt in zip(lrcs, correct_sylts):
            sylt = self.file._parse_lrc_text(lrc)
            self.assertEqual(sylt, correct_sylt)
