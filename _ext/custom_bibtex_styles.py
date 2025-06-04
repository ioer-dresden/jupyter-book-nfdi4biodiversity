# custom conf.py, needed for custom reference citation style


# Custom sphinxcontrib-bibtex referencing style for author-year citations, see:
# https://sphinxcontrib-bibtex.readthedocs.io/en/latest/usage.html#custom-inline-citation-references
#
# This was a rabbit hole. If the code below does not work anymore (due to upstream changes):
# temporary workaround is to revert back to `bibtex_reference_style  : author_year` in _config.yml
#
# with specific formatting:
# - :cite:t:`key` -> Author (Year) [Entirely linked]
# - :cite:alp:`key` -> Author Year [Entirely linked, no surrounding brackets]
# - :cite:p:`key` -> (Author Year) [Entirely linked, no comma]
# - "et al." is not italicized by this style.

from dataclasses import dataclass, field
from typing import List, Union, TYPE_CHECKING

import sphinxcontrib.bibtex.plugin
from sphinxcontrib.bibtex.style.referencing import (
    BracketStyle, PersonStyle, BaseReferenceStyle
)
from sphinxcontrib.bibtex.style.referencing.author_year import (
    AuthorYearReferenceStyle
)
from sphinxcontrib.bibtex.style.referencing.basic_author_year import (
    BasicAuthorYearTextualReferenceStyle,
    BasicAuthorYearParentheticalReferenceStyle
)
# Import other styles that AuthorYearReferenceStyle composes
from sphinxcontrib.bibtex.style.referencing.extra_author import (
    ExtraAuthorReferenceStyle
)
from sphinxcontrib.bibtex.style.referencing.extra_label import (
    ExtraLabelReferenceStyle
)
from sphinxcontrib.bibtex.style.referencing.extra_year import (
    ExtraYearReferenceStyle
)
from sphinxcontrib.bibtex.style.referencing.extra_empty import (
    ExtraEmptyReferenceStyle
)

from pybtex.richtext import BaseText, Text as PybtexText
from pybtex.style.template import (
    Node as PybtexTemplateNode, join as pybtex_join
)
# sphinxcontrib.bibtex specific template functions
from sphinxcontrib.bibtex.style.template import (
    reference as sbt_reference,
    year as sbt_year,
    pre_text,
    post_text,
    join2 as sbt_join2  # Renamed to avoid clash with pybtex_join
)

# For type hints (docutils nodes)
from docutils.nodes import Node as DocutilsNode

if TYPE_CHECKING:
    from pybtex.database import Entry as PybtexEntryType
else:
    # Runtime placeholder for type hint if not type checking
    PybtexEntryType = object


# --- Factory functions for custom BracketStyle instances ---
def round_brackets() -> BracketStyle:
    """Return BracketStyle for simple round parentheses."""
    return BracketStyle(left='(', right=')')


# --- Custom Basic Textual Style for full "Author (Year)" link ---
@dataclass
class CustomBasicTextualRefStyle(BasicAuthorYearTextualReferenceStyle):
    """Customizes the inner Pybtex template for textual citations
    to ensure "Author (Year)" is treated as a single reference unit.
    """

    def inner(self, role_name: str) -> PybtexTemplateNode:
        author_part = self.person.author_or_editor_or_title(
            full=("s" in role_name)
        )
        # self.bracket is textual_year_bracket_style from the main style
        year_part_with_brackets = pybtex_join[
            PybtexText(self.bracket.left),
            sbt_year,  # sphinxcontrib.bibtex's year template
            PybtexText(self.bracket.right)
        ]

        # Content for the reference: "Author<sep>(Year)"
        # self.text_reference_sep is " " from the main style
        content = pybtex_join(sep=self.text_reference_sep)[
            author_part,
            year_part_with_brackets
        ]

        # Wrap the entire content in sphinxcontrib-bibtex's reference template
        # and handle pre/post text.
        return sbt_join2(sep1=self.pre_text_sep, sep2=self.post_text_sep)[
            pre_text,
            sbt_reference[content],
            post_text,
        ]


# --- Main Custom Author-Year Referencing Style ---
@dataclass
class CustomAuthorYearStyle(AuthorYearReferenceStyle):
    """
    Custom author-year style:
    - Textual: "Author (Year)" (fully linked, et al. not italic)
    - Parenthetical: "(Author Year)" (fully linked, no comma)
    - Alp: "Author Year" (fully linked, no comma, no surrounding brackets)
    """

    # Use round brackets for the year part in "Author (Year)"
    bracket_textual: BracketStyle = field(default_factory=round_brackets)
    # Use round brackets for "(Author Year)"
    bracket_parenthetical: BracketStyle = field(default_factory=round_brackets)
    # Use round brackets for other parenthesized parts like (Author) or (Year)
    bracket_author: BracketStyle = field(default_factory=round_brackets)
    bracket_label: BracketStyle = field(default_factory=round_brackets)
    bracket_year: BracketStyle = field(default_factory=round_brackets)

    # Customize PersonStyle for "et al." (if you want to change it)
    # To remove italics from "et al.":
    # person: PersonStyle = field(
    #     default_factory=lambda: PersonStyle(other=PybtexText(" et al."))
    # )
    # If default PersonStyle (italic "et al.") is fine, this can be omitted
    # or set to default_factory=PersonStyle. Assuming default is fine as per your last comment.
    person: PersonStyle = field(default_factory=PersonStyle)


    # Separator between author and year in "(Author Year)" or "Author Year"
    author_year_sep: Union[BaseText, str] = " "  # Space, no comma

    # Separator between "Author" and "(Year)" in textual citations
    text_reference_sep: Union[BaseText, str] = " "

    # Separators for pre/post text within a citation (e.g., [{see}Ref1{p.10}])
    pre_text_sep: Union[BaseText, str] = " "
    post_text_sep: Union[BaseText, str] = ", " # Default is usually fine

    def __post_init__(self):
        # Initialize self.styles from GroupReferenceStyle's perspective
        super(AuthorYearReferenceStyle, self).__post_init__()

        # Populate self.styles, substituting our custom textual style
        self.styles.extend([
            BasicAuthorYearParentheticalReferenceStyle(
                bracket=self.bracket_parenthetical,
                person=self.person,
                author_year_sep=self.author_year_sep,
                pre_text_sep=self.pre_text_sep,
                post_text_sep=self.post_text_sep,
            ),
            CustomBasicTextualRefStyle(  # Use our custom class here
                bracket=self.bracket_textual,
                person=self.person,
                text_reference_sep=self.text_reference_sep,
                pre_text_sep=self.pre_text_sep,
                post_text_sep=self.post_text_sep,
            ),
            ExtraAuthorReferenceStyle(
                bracket=self.bracket_author, person=self.person
            ),
            ExtraLabelReferenceStyle(bracket=self.bracket_label),
            ExtraYearReferenceStyle(bracket=self.bracket_year),
            ExtraEmptyReferenceStyle(),
        ])

        # Rebuild the role_style mapping after modifying self.styles
        self.role_style.clear()
        self.role_style.update(
            (role_name, style)
            for style in self.styles
            for role_name in style.role_names()
        )


# --- Sphinx Setup Function ---
def setup(app):
    """Register the custom citation referencing style."""
    sphinxcontrib.bibtex.plugin.register_plugin(
        'sphinxcontrib.bibtex.style.referencing',
        'author_year_round_custom',  # Name used in _config.yml
        CustomAuthorYearStyle
    )
    return {'version': '0.1', 'parallel_read_safe': True}