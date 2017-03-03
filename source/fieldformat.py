#!/usr/bin/env python3

#******************************************************************************
# fieldformat.py, provides a class to handle field format types
#
# TreeLine, an information storage program
# Copyright (C) 2017, Douglas W. Bell
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License, either Version 2 or any later
# version.  This program is distributed in the hope that it will be useful,
# but WITTHOUT ANY WARRANTY.  See the included LICENSE file for details.
#******************************************************************************

import re
import xml.sax.saxutils
import gennumber
import genboolean

fieldTypes = [N_('Text'), N_('HtmlText'), N_('OneLineText'), N_('SpacedText'),
              N_('Number'), N_('Boolean'), N_('Choice'), N_('Combination'),
              N_('RegularExpression')]
_errorStr = '#####'


class TextField:
    """Class to handle a rich-text field format type.

    Stores options and format strings for a text field type.
    Provides methods to return formatted data.
    """
    typeName = 'Text'
    defaultFormat = ''
    showRichTextInCell = True
    evalHtmlDefault = False
    fixEvalHtmlSetting = True
    defaultNumLines = 1
    editorClassName = 'RichTextEditor'
    formatHelpMenuList = []
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        self.name = name
        if not formatData:
            formatData = {}
        self.setFormat(formatData.get('format', type(self).defaultFormat))
        self.prefix = formatData.get('prefix', '')
        self.suffix = formatData.get('suffix', '')
        self.initDefault = formatData.get('init', '')
        self.numLines = formatData.get('lines', type(self).defaultNumLines)
        self.sortKeyNum = formatData.get('sortkeynum', 0)
        self.sortKeyForward = formatData.get('sortkeyfwd', True)
        self.evalHtml = self.evalHtmlDefault
        if not self.fixEvalHtmlSetting:
            self.evalHtml = formatData.get('evalhtml', self.evalHtmlDefault)
        self.useFileInfo = False
        self.showInDialog = True

    def formatData(self):
        """Return a dictionary of this field's format settings.
        """
        formatData = {'fieldname': self.name, 'fieldtype': self.typeName}
        if self.format:
            formatData['format'] = self.format
        if self.prefix:
            formatData['prefix'] = self.prefix
        if self.suffix:
            formatData['suffix'] = self.suffix
        if self.initDefault:
            formatData['init'] = self.initDefault
        if self.numLines != self.defaultNumLines:
            formatData['lines'] = self.numLines
        if self.sortKeyNum > 0:
            formatData['sortkeynum'] = self.sortKeyNum
        if not self.sortKeyForward:
            formatData['sortkeyfwd'] = False
        if (not self.fixEvalHtmlSetting and
            self.evalHtml != self.evalHtmlDefault):
            formatData['evalhtml'] = self.evalHtml
        return formatData

    def setFormat(self, format):
        """Set the format string and initialize as required.

        Derived classes may raise a ValueError if the format is illegal.
        Arguments:
            format -- the new format string
        """
        self.format = format

    def outputText(self, node, titleMode, formatHtml):
        """Return formatted output text for this field in this node.

        Arguments:
            node -- the tree item storing the data
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        if self.useFileInfo:
            node = node.modelRef.fileInfoNode
        storedText = node.data.get(self.name, '')
        if storedText:
            return self.formatOutput(storedText, titleMode, formatHtml)
        return ''

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        prefix = self.prefix
        suffix = self.suffix
        if titleMode:
            storedText = removeMarkup(storedText)
            if formatHtml:
                prefix = removeMarkup(prefix)
                suffix = removeMarkup(suffix)
        elif not formatHtml:
            prefix = xml.sax.saxutils.escape(prefix)
            suffix = xml.sax.saxutils.escape(suffix)
        return '{0}{1}{2}'.format(prefix, storedText, suffix)

    def editorText(self, node):
        """Return text formatted for use in the data editor.

        The function for default text just returns the stored text.
        Overloads may raise a ValueError if the data does not match the format.
        Arguments:
            node -- the tree item storing the data
        """
        storedText = node.data.get(self.name, '')
        return self.formatEditorText(storedText)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        The function for default text just returns the stored text.
        Overloads may raise a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        return storedText

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        The function for default text field just returns the editor text.
        Overloads may raise a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        return editorText

    def storedTextFromTitle(self, titleText):
        """Return new text to be stored based on title text edits.

        Overloads may raise a ValueError if the data does not match the format.
        Arguments:
            titleText -- the new title text
        """
        return self.storedText(xml.sax.saxutils.escape(titleText))

    def getInitDefault(self):
        """Return the initial stored value for newly created nodes.
        """
        return self.initDefault

    def setInitDefault(self, editorText):
        """Set the default initial value from editor text.

        The function for default text field just returns the stored text.
        Arguments:
            editorText -- the new text entered into the editor
        """
        self.initDefault = self.storedText(editorText)

    def getEditorInitDefault(self):
        """Return initial value in editor format.

        The function for default text field just returns the initial value.
        """
        return self.formatEditorText(self.initDefault)

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default.
        """
        return []

    def mathValue(self, node, zeroBlanks=True):
        """Return a value to be used in math field equations.

        Return None if blank and not zeroBlanks.
        Arguments:
            node -- the tree item storing the data
            zeroBlanks -- accept blank field values if True
        """
        storedText = node.data.get(self.name, '')
        storedText = removeMarkup(storedText)
        return storedText if storedText or zeroBlanks else None

    def compareValue(self, node):
        """Return a value for comparison to other nodes and for sorting.

        Returns lowercase text for text fields or numbers for non-text fields.
        Arguments:
            node -- the tree item storing the data
        """
        storedText = node.data.get(self.name, '')
        storedText = removeMarkup(storedText)
        return storedText.lower()

    def sortKey(self, node):
        """Return a tuple with field type and comparison value for sorting.

        Allows different types to be sorted.
        Arguments:
            node -- the tree item storing the data
        """
        return ('80_text', self.compareValue(node))

    def adjustedCompareValue(self, value):
        """Return value adjusted like the compareValue for use in conditionals.

        Text version removes any markup and goes to lower case.
        Arguments:
            value -- the comparison value to adjust
        """
        value = removeMarkup(value)
        return value.lower()

    def changeType(self, newType):
        """Change this field's type to newType with a default format.

        Arguments:
            newType -- the new type name, excluding "Field"
        """
        self.__class__ = globals()[newType + 'Field']
        self.setFormat(self.defaultFormat)
        if self.fixEvalHtmlSetting:
            self.evalHtml = self.evalHtmlDefault

    def sepName(self):
        """Return the name enclosed with {* *} separators
        """
        if self.useFileInfo:
            return '{{*!{0}*}}'.format(self.name)
        return '{{*{0}*}}'.format(self.name)

    def getFormatHelpMenuList(self):
        """Return the list of descriptions and keys for the format help menu.
        """
        return self.formatHelpMenuList


class HtmlTextField(TextField):
    """Class to handle an HTML text field format type

    Stores options and format strings for an HTML text field type.
    Does not use the rich text editor.
    Provides methods to return formatted data.
    """
    typeName = 'HtmlText'
    showRichTextInCell = False
    evalHtmlDefault = True
    editorClassName = 'HtmlTextEditor'
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def storedTextFromTitle(self, titleText):
        """Return new text to be stored based on title text edits.

        Overloads may raise a ValueError if the data does not match the format.
        Arguments:
            titleText -- the new title text
        """
        return self.storedText(titleText)


class OneLineTextField(TextField):
    """Class to handle a single-line rich-text field format type.

    Stores options and format strings for a text field type.
    Provides methods to return formatted data.
    """
    typeName = 'OneLineText'
    editorClassName = 'OneLineTextEditor'
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        text = storedText.split('<br />', 1)[0]
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        return storedText.split('<br />', 1)[0]


class SpacedTextField(TextField):
    """Class to handle a preformatted text field format type.

    Stores options and format strings for a spaced text field type.
    Uses <pre> tags to preserve spacing.
    Does not use the rich text editor.
    Provides methods to return formatted data.
    """
    typeName = 'SpacedText'
    showRichTextInCell = False
    editorClassName = 'PlainTextEditor'
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        if storedText:
            storedText = '<pre>{0}</pre>'.format(storedText)
        return super().formatOutput(storedText, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Arguments:
            storedText -- the source text to format
        """
        return xml.sax.saxutils.unescape(storedText)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Arguments:
            editorText -- the new text entered into the editor
        """
        return xml.sax.saxutils.escape(editorText)

    def storedTextFromTitle(self, titleText):
        """Return new text to be stored based on title text edits.

        Arguments:
            titleText -- the new title text
        """
        return self.storedText(titleText)


class NumberField(HtmlTextField):
    """Class to handle a general number field format type.

    Stores options and format strings for a number field type.
    Provides methods to return formatted data.
    """
    typeName = 'Number'
    defaultFormat = '#.##'
    evalHtmlDefault = False
    editorClassName = 'LineEditor'
    formatHelpMenuList = [(_('Optional Digit\t#'), '#'),
                          (_('Required Digit\t0'), '0'),
                          (_('Digit or Space (external)\t<space>'), ' '),
                          ('', ''),
                          (_('Decimal Point\t.'), '.'),
                          (_('Decimal Comma\t,'), ','),
                          ('', ''),
                          (_('Comma Separator\t\,'), '\,'),
                          (_('Dot Separator\t\.'), '\.'),
                          (_('Space Separator (internal)\t<space>'), ' '),
                          ('', ''),
                          (_('Optional Sign\t-'), '-'),
                          (_('Required Sign\t+'), '+'),
                          ('', ''),
                          (_('Exponent (capital)\tE'), 'E'),
                          (_('Exponent (small)\te'), 'e')]

    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        try:
            text = gennumber.GenNumber(storedText).numStr(self.format)
        except ValueError:
            text = _errorStr
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if not storedText:
            return ''
        return gennumber.GenNumber(storedText).numStr(self.format)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if not editorText:
            return ''
        return repr(gennumber.GenNumber().setFromStr(editorText, self.format))

    def mathValue(self, node, zeroBlanks=True):
        """Return a numeric value to be used in math field equations.

        Return None if blank and not zeroBlanks,
        raise a ValueError if it isn't a number.
        Arguments:
            node -- the tree item storing the data
            zeroBlanks -- replace blank field values with zeros if True
        """
        storedText = node.data.get(self.name, '')
        if storedText:
            return gennumber.GenNumber(storedText).num
        return 0 if zeroBlanks else None

    def compareValue(self, node):
        """Return a value for comparison to other nodes and for sorting.

        Returns lowercase text for text fields or numbers for non-text fields.
        Arguments:
            node -- the tree item storing the data
        """
        storedText = node.data.get(self.name, '')
        try:
            return gennumber.GenNumber(storedText).num
        except ValueError:
            return 0

    def sortKey(self, node):
        """Return a tuple with field type and comparison values for sorting.

        Allows different types to be sorted.
        Arguments:
            node -- the tree item storing the data
        """
        return ('20_num', self.compareValue(node))

    def adjustedCompareValue(self, value):
        """Return value adjusted like the compareValue for use in conditionals.

        Number version converts to a numeric value.
        Arguments:
            value -- the comparison value to adjust
        """
        try:
            return gennumber.GenNumber(value).num
        except ValueError:
            return 0


class ChoiceField(HtmlTextField):
    """Class to handle a field with pre-defined, individual text choices.

    Stores options and format strings for a choice field type.
    Provides methods to return formatted data.
    """
    typeName = 'Choice'
    editSep = '/'
    defaultFormat = '1/2/3/4'
    evalHtmlDefault = False
    fixEvalHtmlSetting = False
    editorClassName = 'ComboEditor'
    numChoiceColumns = 1
    autoAddChoices = False
    formatHelpMenuList = [(_('Separator\t/'), '/'), ('', ''),
                          (_('"/" Character\t//'), '//'), ('', ''),
                          (_('Example\t1/2/3/4'), '1/2/3/4')]
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def setFormat(self, format):
        """Set the format string and initialize as required.

        Arguments:
            format -- the new format string
        """
        super().setFormat(format)
        self.choiceList = self.splitText(self.format)
        if self.evalHtml:
            self.choices = set(self.choiceList)
        else:
            self.choices = set([xml.sax.saxutils.escape(choice) for choice in
                                self.choiceList])

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        if storedText not in self.choices:
            storedText = _errorStr
        return super().formatOutput(storedText, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if storedText and storedText not in self.choices:
            raise ValueError
        if self.evalHtml:
            return storedText
        return xml.sax.saxutils.unescape(storedText)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if not self.evalHtml:
            editorText = xml.sax.saxutils.escape(editorText)
        if not editorText or editorText in self.choices:
            return editorText
        raise ValueError

    def comboChoices(self):
        """Return a list of choices for the combo box.
        """
        return self.choiceList

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default.
        """
        return self.choiceList

    def splitText(self, textStr):
        """Split textStr using editSep, return a list of strings.

        Double editSep's are not split (become single).
        Removes duplicates and empty strings.
        Arguments:
            textStr -- the text to split
        """
        result = []
        textStr = textStr.replace(self.editSep * 2, '\0')
        for text in textStr.split(self.editSep):
            text = text.strip().replace('\0', self.editSep)
            if text and text not in result:
                result.append(text)
        return result


class CombinationField(ChoiceField):
    """Class to handle a field with multiple pre-defined text choices.

    Stores options and format strings for a combination field type.
    Provides methods to return formatted data.
    """
    typeName = 'Combination'
    editorClassName = 'CombinationEditor'
    numChoiceColumns = 2
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def setFormat(self, format):
        """Set the format string and initialize as required.

        Arguments:
            format -- the new format string
        """
        TextField.setFormat(self, format)
        if not self.evalHtml:
            format = xml.sax.saxutils.escape(format)
        self.choiceList = self.splitText(format)
        self.choices = set(self.choiceList)
        self.outputSep = ''

    def outputText(self, node, titleMode, formatHtml):
        """Return formatted output text for this field in this node.

        Sets output separator prior to calling base class methods.
        Arguments:
            node -- the tree item storing the data
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        self.outputSep = node.nodeFormat().outputSeparator
        return super().outputText(node, titleMode, formatHtml)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        selections, valid = self.sortedSelections(storedText)
        if valid:
            result = self.outputSep.join(selections)
        else:
            result = _errorStr
        return TextField.formatOutput(self, result, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        selections = set(self.splitText(storedText))
        if selections.issubset(self.choices):
            if self.evalHtml:
                return storedText
            return xml.sax.saxutils.unescape(storedText)
        raise ValueError

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if not self.evalHtml:
            editorText = xml.sax.saxutils.escape(editorText)
        selections, valid = self.sortedSelections(editorText)
        if not valid:
            raise ValueError
        return self.joinText(selections)

    def comboChoices(self):
        """Return a list of choices for the combo box.
        """
        if self.evalHtml:
            return self.choiceList
        return [xml.sax.saxutils.unescape(text) for text in self.choiceList]

    def comboActiveChoices(self, editorText):
        """Return a sorted list of choices currently in editorText.

        Arguments:
            editorText -- the text entered into the editor
        """
        selections, valid = self.sortedSelections(xml.sax.saxutils.
                                                  escape(editorText))
        if self.evalHtml:
            return selections
        return [xml.sax.saxutils.unescape(text) for text in selections]

    def initDefaultChoices(self):
        """Return a list of choices for setting the init default.
        """
        return []

    def sortedSelections(self, inText):
        """Split inText using editSep and sort like format string.

        Return a tuple of resulting selection list and bool validity.
        Valid if all choices are in the format string.
        Arguments:
            inText -- the text to split and sequence
        """
        selections = set(self.splitText(inText))
        result = [text for text in self.choiceList if text in selections]
        return (result, len(selections) == len(result))

    def joinText(self, textList):
        """Join the text list using editSep, return the string.

        Any editSep in text items become double.
        Arguments:
            textList -- the list of text items to join
        """
        return self.editSep.join([text.replace(self.editSep, self.editSep * 2)
                                  for text in textList])


class BooleanField(ChoiceField):
    """Class to handle a general boolean field format type.

    Stores options and format strings for a boolean field type.
    Provides methods to return formatted data.
    """
    typeName = 'Boolean'
    defaultFormat = _('yes/no')
    evalHtmlDefault = False
    fixEvalHtmlSetting = True
    formatHelpMenuList = [(_('true/false'), 'true/false'),
                          (_('T/F'), 'T/F'), ('', ''),
                          (_('yes/no'), 'yes/no'),
                          (_('Y/N'), 'Y/N'), ('', ''),
                          ('1/0', '1/0')]
    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        try:
            text =  genboolean.GenBoolean(storedText).boolStr(self.format)
        except ValueError:
            text = _errorStr
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if not storedText:
            return ''
        return genboolean.GenBoolean(storedText).boolStr(self.format)

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        if not editorText:
            return ''
        try:
            return repr(genboolean.GenBoolean().setFromStr(editorText,
                                                           self.format))
        except ValueError:
            return repr(genboolean.GenBoolean(editorText))

    def mathValue(self, node, zeroBlanks=True):
        """Return a value to be used in math field equations.

        Return None if blank and not zeroBlanks,
        raise a ValueError if it isn't a valid boolean.
        Arguments:
            node -- the tree item storing the data
            zeroBlanks -- replace blank field values with zeros if True
        """
        storedText = node.data.get(self.name, '')
        if storedText:
            return genboolean.GenBoolean(storedText).value
        return False if zeroBlanks else None

    def compareValue(self, node):
        """Return a value for comparison to other nodes and for sorting.

        Returns lowercase text for text fields or numbers for non-text fields.
        Bool fields return True or False values.
        Arguments:
            node -- the tree item storing the data
        """
        storedText = node.data.get(self.name, '')
        try:
            return genboolean.GenBoolean(storedText).value
        except ValueError:
            return False

    def sortKey(self, node):
        """Return a tuple with field type and comparison values for sorting.

        Allows different types to be sorted.
        Arguments:
            node -- the tree item storing the data
        """
        return ('30_bool', self.compareValue(node))

    def adjustedCompareValue(self, value):
        """Return value adjusted like the compareValue for use in conditionals.

        Bool version converts to a bool value.
        Arguments:
            value -- the comparison value to adjust
        """
        try:
            return genboolean.GenBoolean().setFromStr(value, self.format).value
        except ValueError:
            try:
                return genboolean.GenBoolean(value).value
            except ValueError:
                return False


class RegularExpressionField(HtmlTextField):
    """Class to handle a field format type controlled by a regular expression.

    Stores options and format strings for a number field type.
    Provides methods to return formatted data.
    """
    typeName = 'RegularExpression'
    defaultFormat = '.*'
    evalHtmlDefault = False
    fixEvalHtmlSetting = False
    editorClassName = 'LineEditor'
    formatHelpMenuList = [(_('Any Character\t.'), '.'),
                          (_('End of Text\t$'), '$'),
                          ('', ''),
                          (_('0 Or More Repetitions\t*'), '*'),
                          (_('1 Or More Repetitions\t+'), '+'),
                          (_('0 Or 1 Repetitions\t?'), '?'),
                          ('', ''),
                          (_('Set of Numbers\t[0-9]'), '[0-9]'),
                          (_('Lower Case Letters\t[a-z]'), '[a-z]'),
                          (_('Upper Case Letters\t[A-Z]'), '[A-Z]'),
                          (_('Not a Number\t[^0-9]'), '[^0-9]'),
                          ('', ''),
                          (_('Or\t|'), '|'),
                          (_('Escape a Special Character\t\\'), '\\')]

    def __init__(self, name, formatData=None):
        """Initialize a field format type.

        Arguments:
            name -- the field name string
            formatData -- the dict that defines this field's format
        """
        super().__init__(name, formatData)

    def setFormat(self, format):
        """Set the format string and initialize as required.

        Raise a ValueError if the format is illegal.
        Arguments:
            format -- the new format string
        """
        try:
            re.compile(format)
        except re.error:
            raise ValueError
        super().setFormat(format)

    def formatOutput(self, storedText, titleMode, formatHtml):
        """Return formatted output text from stored text for this field.

        Arguments:
            storedText -- the source text to format
            titleMode -- if True, removes all HTML markup for tree title use
            formatHtml -- if False, escapes HTML from prefix & suffix
        """
        match = re.match(self.format, xml.sax.saxutils.unescape(storedText))
        if not storedText or match:
            text = storedText
        else:
            text = _errorStr
        return super().formatOutput(text, titleMode, formatHtml)

    def formatEditorText(self, storedText):
        """Return text formatted for use in the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            storedText -- the source text to format
        """
        if not self.evalHtml:
            storedText = xml.sax.saxutils.unescape(storedText)
        match = re.match(self.format, storedText)
        if not storedText or match:
            return storedText
        raise ValueError

    def storedText(self, editorText):
        """Return new text to be stored based on text from the data editor.

        Raises a ValueError if the data does not match the format.
        Arguments:
            editorText -- the new text entered into the editor
        """
        match = re.match(self.format, editorText)
        if not editorText or match:
            if self.evalHtml:
                return editorText
            return xml.sax.saxutils.escape(editorText)
        raise ValueError


####  Utility Functions  ####

_stripTagRe = re.compile('<.*?>')

def removeMarkup(text):
    """Return text with all HTML Markup removed and entities unescaped.
    """
    text = _stripTagRe.sub('', text)
    return xml.sax.saxutils.unescape(text)