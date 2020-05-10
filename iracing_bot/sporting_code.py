from io import StringIO, BytesIO
import re
from urllib.request import urlopen

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams


class SportingCode:
    """
    This provides an in-memory representation of the sporting code, broken down by
    sections. Each section has its page number and a reference to its parent and
    children's sections (if applicable).
    """

    # Used to find the section indexes in the PDF
    SECTION_IDX_REGEX = r'^[0-9](\.[0-9])?(\.[0-9])?(\.[0-9])?\.'
    SECTION_PART_SEPARATOR = '.'  # Separator that splits the indexes
    # Used internally to make page breaks easier to parse
    PAGE_BREAK_INDICATOR = '<!-- PAGE BREAK -->'

    def __init__(self, remote_pdf_url, start_parsing_at=3, formatter=None, format_overrides=None):
        self.url = remote_pdf_url                           # URL to the sporting code PDF
        self.start_page_parsing_at = start_parsing_at       # Skips pages 1...n-1 like cover & TOC
        self.raw_content = BytesIO()                        # Raw PDF contents
        self.raw_parsed_content = ''                        # Text contents of PDF minimally parsed
        self.sections = []                                  # Sections (rules) in the sporting code
        self.top_level_sections = []                        # Top level sections (1., 2., 3.)
        self.parsed = False                                 # ensure this only gets parsed once

        # The default formatter for a section
        self.default_formatter = formatter if formatter is not None else Formatter()
        # Any markdown format overrides that are in the form of {'section IDx': <formatter>}
        self.format_overrides = format_overrides if format_overrides else dict()

    def get_section(self, idx):
        """Linearly search for the section
        """
        if not idx.endswith('.'):
            idx = idx + '.'
        for section in self.sections:
            if section.idx == idx:
                return section
        return None

    def parse_pdf(self):
        """
        The meat of the SportingCode instance. This attempts to take the
        downloaded PDF contents and convert it into Python objects that can
        be more easily parsed, read, and manipulated.
        """
        if self.parsed:
            return

        self.raw_content.write(urlopen(self.url).read())
        out_io = StringIO()
        extract_text_to_fp(
            self.raw_content,
            out_io,
            laparams=LAParams(),
            output_type='text',
            strip_control=True,
            codec=None
        )
        # Saved directly as it was parsed by pdfminer.six
        self.raw_parsed_content = out_io.getvalue().strip().replace("", "")

        # We then run the content through a bunch of custom filters that will
        # massage the PDF contents into something more friendly to parse
        page_splitter = '\n\n'+self.PAGE_BREAK_INDICATOR

        # 1. Since each page has the same footer, we can use that to replace
        #    the hard to read page breaks with something that says `<! -- PAGE BREAK -->`
        self.parsed_content = re.sub(
            r'[\n ]*Version - 2018.09[\n ]*\d+[\n ]*',
            page_splitter,
            self.raw_parsed_content
        )

        # 2. Remove the first couple pages (title and table of contents) since we
        #    don't really care to parse these
        self.parsed_content = self.parsed_content.split(
            page_splitter,
            self.start_page_parsing_at-1
        )[self.start_page_parsing_at-1]

        # 3. Iterate through the sporting code and if the line contains a section ID or index
        #    then we will create a new section, or else we will keep appending to the current.
        self.parse_content_into_sections()

        # 4. Try to build a section hierarchy, meaning 1.1. is a child of 1.
        #    This will allow us to easily grab all sections including children
        self.build_section_hierarchy()

        # Uncomment this if you want to write the sporting code to a file to check it
        # with open('sporting_code.md', 'w') as f:
        #     f.write(self.markdown())

        self.parsed = True

    def parse_content_into_sections(self):
        """Parse the raw PDF output into defined, concrete sections that match section IDs
        """
        page = 1  # index starting at 1 for the plebs
        self.sections = []
        for line in map(lambda x: x.strip(), self.parsed_content.split('\n')):
            line = line.strip()
            if not line:  # remove empty lines
                continue

            # Line starts a new section
            if self.__line_starts_section(line):
                section_idx = self.__get_section_idx(line)
                if self.PAGE_BREAK_INDICATOR in line:
                    page += 1
                # Remove the section index and separator
                text = line.replace(section_idx, '').replace(self.PAGE_BREAK_INDICATOR, '').strip()
                self.sections.append(Section(
                    idx=section_idx,
                    page=page,
                    text=text,
                    formatter=self.format_overrides.get(section_idx, self.default_formatter)
                ))
                continue

            # Determine if the section spans multiple pages or not
            section = self.sections[-1]
            if self.PAGE_BREAK_INDICATOR in line:
                line = line.replace(self.PAGE_BREAK_INDICATOR, '').strip()
                page += 1
                section.continues_onto_page(page)

            # Add the continuation line to the existing section
            separator = ' '  # ensure that lines are space separates so words aren't bunched
            if section.text.endswith(' ') or line.startswith(' '):
                separator = ''
            section.text += f'{separator}{line}'

    def build_section_hierarchy(self):
        """Iterates through self.sections and creates the section hierarchy from section IDs
        """
        sep = self.SECTION_PART_SEPARATOR
        for section in self.sections:
            # Since the sections are already in order, checking is easy...only two
            # conditions must be met...
            idx_parts = [x for x in section.idx.split(sep) if x]
            parent_idx = sep.join(idx_parts[:-1]) + sep
            parent_section = self.get_section(parent_idx)
            if parent_section:
                parent_section.add_subsection(section)

        # List of top level sections (1.,2.,3....)
        self.top_level_sections = list(filter(lambda sec: sec.parent is None, self.sections))

    def __line_starts_section(self, line):
        """Returns whether or not the line represents a new section
        """
        parts = line.replace(self.PAGE_BREAK_INDICATOR, '').split(' ', 1)
        if not parts or len(parts) == 1:
            return False
        return re.match(self.SECTION_IDX_REGEX, parts[0])

    def __get_section_idx(self, line):
        """Given a line that starts a new section, this parses out the section IDx
        """
        parts = line.replace(self.PAGE_BREAK_INDICATOR, '').split(' ', 1)
        if not parts or len(parts) == 1:
            raise ValueError('Line does not represent a section index line')
        idx = parts[0]
        if not self.__line_starts_section(line):
            raise ValueError('Line does not represent a section index line')
        return idx.strip()

    def markdown(self):
        """Convert the entire sporting code into a markdown string
        """
        return '\n'.join([sec.markdown() for sec in self.top_level_sections])


class Section:
    """Represents a section of the sporting code that can easily be indexed and retrieved
    """

    def __init__(self, idx, text, page, formatter, parent=None):
        self.idx = idx
        self.children = []    # Child sections (1.2.3. is a direct child of 1.2.)
        self.text = text
        self.page = page      # Page number that the section is on OR a list of pages it spans
        self.formatter = formatter
        self.parent = parent    # Direct parent of the section (1.2. is a direct parent of 1.2.3)

    def continues_onto_page(self, additional_page):
        """Denotes that the section continues on to the given additional page
        """
        if isinstance(self.page, int):
            self.page = [self.page]
        self.page.append(additional_page)

    def add_subsection(self, section):
        """Adds a new child subsection to the current section
        """
        self.children.append(section)
        section.parent = self

    def depth(self):
        """Returns the depth of this section by returning how many parents it has
        """
        count = 0
        parent = self.parent
        while parent:
            parent = parent.parent
            count += 1
        return count

    def markdown(self):
        """Prettifies the section and its children for markdown consumption
        """
        current_section = self.formatter.format(self)
        return current_section + '\n\n' + '\n'.join([child.markdown() for child in self.children])


class Formatter:
    """
    Formatters are used to convert the raw sections into markdown that is nicely readable.
    """

    TITLE_MAX_LENGTH = 6

    def format(self, section):
        is_title = len(section.text.split(' ')) < self.TITLE_MAX_LENGTH
        if is_title:
            heading = '#' * (section.depth() + 1)
            current_section = f'{heading} {section.idx} {section.text}'
        else:
            current_section = f'**{section.idx}**: {section.text}'
        return current_section


class BulletFormatter(Formatter):
    """Makes the section a bullet point in an unordered list
    """

    def format(self, section):
        return f'* **{section.idx}**: {section.text}'


class ImageFormatter(Formatter):
    """
    Since some things just will never render correctly, we may have to show an
    external image link that contains the info we want to show
    """

    def __init__(self, image_url, cut_at=None):
        self.image_url = image_url
        self.cut_at = cut_at

    def format(self, section):
        text = section.text
        if self.cut_at:
            text = text.split(self.cut_at)[0]
        return (
            f'**{section.idx}**: {text.strip()}. This section links to a graphic from the '
            f'sporting code which can be viewed by [here]({self.image_url})'
        )
