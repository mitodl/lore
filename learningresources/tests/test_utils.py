"""
Tests for utilities within the API.
"""

from unittest import TestCase

from lxml import etree

from learningresources.api import get_video_sub, _subs_filename

VIDEO_XML = """
<video youtube_id_1_0="p2Q6BrNhdh9"
display_name="Welcome"
sub="CCxmtcICYNc" />
"""

NO_SUB = """
<video youtube_id_1_0="p2Q6BrNhdh9"
display_name="Welcome" />
"""


class TestUtils(TestCase):
    """
    Test manipulation utilities.
    """

    def test_sub_language(self):
        """Test getting filename per language."""
        values = (
            ("", "subs_CCxmtcICYNc.srt.sjson"),
            ("en", "subs_CCxmtcICYNc.srt.sjson"),
            ("de", "de_subs_CCxmtcICYNc.srt.sjson"),
        )
        for lang, sub in values:
            self.assertEqual(sub, _subs_filename("CCxmtcICYNc", lang))

    def test_get_sub_name(self):
        """Test getting subtitle names."""
        values = (
            (VIDEO_XML, "subs_CCxmtcICYNc.srt.sjson"),
            (NO_SUB, ""),
        )
        for xml, result in values:
            self.assertEqual(get_video_sub(etree.fromstring(xml)), result)
