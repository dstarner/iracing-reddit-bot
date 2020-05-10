from unittest import TestCase

from ..sporting_code import SportingCode, Section


class SectionHierarchyTestCase(TestCase):

    def test_get_section(self):
        sporting_code = SportingCode('')
        section_one = Section('1.', 'no-text', 0, formatter=object())
        section_one_one = Section('1.1.', 'no-text', 0, formatter=object())
        sporting_code.sections = [
            section_one,
            section_one_one,
        ]
        self.assertEqual(section_one, sporting_code.get_section('1.'))
        # Test without the suffix'ed period
        self.assertEqual(section_one_one, sporting_code.get_section('1.1'))

    def test_build_section_hierarchy__has_direct_relation(self):
        sporting_code = SportingCode('')
        sporting_code.sections = [
            Section('1.', 'no-text', 0, formatter=object()),
            Section('1.1.', 'no-text', 0, formatter=object())
        ]
        sporting_code.build_section_hierarchy()
        child_section = sporting_code.get_section('1.1.')
        parent_section = sporting_code.get_section('1.')
        self.assertEqual(child_section.parent, parent_section)
        self.assertTrue(child_section in parent_section.children)

    def test_build_section_hierarchy__has_indirect_relation(self):
        sporting_code = SportingCode('')
        sporting_code.sections = [
            Section('1.', 'no-text', 0, formatter=object()),
            Section('1.1.', 'no-text', 0, formatter=object()),
            Section('1.1.1.', 'no-text', 0, formatter=object())
        ]
        sporting_code.build_section_hierarchy()
        child_section = sporting_code.get_section('1.1.1.')
        parent_section = sporting_code.get_section('1.')
        self.assertEqual(child_section.parent.parent, parent_section)

    def test_build_section_hierarchy__has_no_direct(self):
        sporting_code = SportingCode('')
        sporting_code.sections = [
            Section('1.', 'no-text', 0, formatter=object()),
            Section('2.1.', 'no-text', 0, formatter=object())
        ]
        sporting_code.build_section_hierarchy()
        section_two = sporting_code.get_section('2.1.')
        section_one = sporting_code.get_section('1.')
        self.assertTrue(section_two not in section_one.children)
        self.assertIsNone(section_two.parent)
