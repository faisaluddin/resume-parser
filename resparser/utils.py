from pdfminer.high_level import extract_text
import docx2txt
from . import constants as cs
import re
import pandas as pd
import os
from typing import Optional


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF document.

    Parameters:
    - pdf_path (str): The path to the PDF file.

    Returns:
    - str: Extracted text from the PDF.
    """
    return extract_text(pdf_path)


def extract_text_from_docx(docx_path: str) -> str:
    """
    Extract text from a Word document.

    Parameters:
    - docx_path (str): The path to the Word document (.docx).

    Returns:
    - str: Extracted text from the Word document.
    """
    return docx2txt.process(docx_path)


def extract_raw_text(file_path: str) -> None:
    """
    Parse a resume from either a PDF or Word document.

    Parameters:
    - file_path (str): The path to the resume file (PDF or DOCX).
    """
    if file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Please provide a PDF or DOCX file.")

    return text


def extract_name(nlp_text, matcher):
    """
    Helper function to extract name from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :param matcher: object of `spacy.matcher.Matcher`
    :return: string of full name
    """

    matcher.add("NAME", [cs.NAME_PATTERN])

    matches = matcher(nlp_text)

    for _, start, end in matches:
        span = nlp_text[start:end]
        if "name" not in span.text.lower():
            return span.text


def extract_email(text):
    """
    Helper function to extract email id from text

    :param text: plain text extracted from resume file
    """
    email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if email:
        try:
            return email[0].split()[0].strip(";")
        except IndexError:
            return None


def extract_mobile_number(text, custom_regex=None):
    """
    Helper function to extract mobile number from text

    :param text: plain text extracted from resume file
    :return: string of extracted mobile numbers
    """
    # Found this complicated regex on :
    # https://zapier.com/blog/extract-links-email-phone-regex/
    # mob_num_regex = r'''(?:(?:\+?([1-9]|[0-9][0-9]|
    #     [0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|
    #     [2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|
    #     [0-9]1[02-9]|[2-9][02-8]1|
    #     [2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|
    #     [2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{7})
    #     (?:\s*(?:#|x\.?|ext\.?|
    #     extension)\s*(\d+))?'''
    if not custom_regex:
        mob_num_regex = r"""(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)
                        [-\.\s]*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})"""
        phone = re.findall(re.compile(mob_num_regex), text)
    else:
        phone = re.findall(re.compile(custom_regex), text)
    if phone:
        number = "".join(phone[0])
        return number


def extract_skills(nlp_text, noun_chunks, skills_file=None):
    """
    Helper function to extract skills from spacy nlp text

    :param nlp_text: object of `spacy.tokens.doc.Doc`
    :param noun_chunks: noun chunks extracted from nlp text
    :return: list of skills extracted
    """
    tokens = [token.text for token in nlp_text if not token.is_stop]
    if not skills_file:
        data = pd.read_csv("./data/skills.csv")
    else:
        data = pd.read_csv(skills_file)
    skills = list(data.columns.values)
    skillset = []
    # check for one-grams
    for token in tokens:
        if token.lower() in skills:
            skillset.append(token)

    # check for bi-grams and tri-grams
    for token in noun_chunks:
        token = token.text.lower().strip()
        if token in skills:
            skillset.append(token)
    return [i.capitalize() for i in set([i.lower() for i in skillset])]


def extract_entity_sections_grad(text):
    """
    Helper function to extract all the raw text from sections of
    resume specifically for graduates and undergraduates

    :param text: Raw text of resume
    :return: dictionary of entities
    """
    text_split = [i.strip() for i in text.split("\n")]
    # sections_in_resume = [i for i in text_split if i.lower() in sections]
    entities = {}
    key = False
    for phrase in text_split:
        if len(phrase) == 1:
            p_key = phrase
        else:
            p_key = set(phrase.lower().split()) & set(cs.RESUME_SECTIONS_GRAD)
        try:
            p_key = list(p_key)[0]
        except IndexError:
            pass
        if p_key in cs.RESUME_SECTIONS_GRAD:
            entities[p_key] = []
            key = p_key
        elif key and phrase.strip():
            entities[key].append(phrase)

    # entity_key = False
    # for entity in entities.keys():
    #     sub_entities = {}
    #     for entry in entities[entity]:
    #         if u'\u2022' not in entry:
    #             sub_entities[entry] = []
    #             entity_key = entry
    #         elif entity_key:
    #             sub_entities[entity_key].append(entry)
    #     entities[entity] = sub_entities

    # pprint.pprint(entities)

    # make entities that are not found None
    # for entity in cs.RESUME_SECTIONS:
    #     if entity not in entities.keys():
    #         entities[entity] = None
    return entities


def extract_linkedin(text: str) -> Optional[str]:
    """
    Extract LinkedIn profile URL from the resume text.

    Args:
        resume_text (str): The text of the resume.

    Returns:
        Optional[str]: The LinkedIn profile URL if found, otherwise None.
    """
    linkedin_url = None
    pattern = re.compile(r"linkedin.com/in/([A-Za-z0-9_-]+)")
    matches = pattern.findall(text)
    if matches:
        linkedin_url = "https://www.linkedin.com/in/" + matches[0]
    return linkedin_url


def extract_gender(text: str) -> Optional[str]:
    """
    Extract gender from the resume text if it's mentioned suffixed with 'gender' or 'sex'.

    Args:
        resume_text (str): The text of the resume.

    Returns:
        Optional[str]: The gender if found, otherwise None.
    """
    gender = None
    pattern = re.compile(r"(gender|sex)\s*:\s*(male|female)", re.IGNORECASE)
    match = pattern.search(text)
    if match:
        gender = match.group(2).lower()
    return gender
