import spacy

from spacy.matcher import Matcher
from . import utils
import json
import os


class ResumeParser(object):

    def __init__(self, resume, skills_file=None, custom_regex=None):
        nlp = spacy.load("en_core_web_sm")
        self.__skills_file = skills_file
        self.__custom_regex = custom_regex
        self.__matcher = Matcher(nlp.vocab)
        self.__details = {
            "name": None,
            "email": None,
            "mobile_number": None,
            "skills": None,
            "college_name": None,
            "degree": None,
            "designation": None,
            "experience": None,
            "company_names": None,
            "no_of_pages": None,
            "total_experience": None,
        }
        self.__resume = resume

        self.__text_raw = utils.extract_raw_text(self.__resume)
        self.__text = " ".join(self.__text_raw.split())
        self.__nlp = nlp(self.__text)
        self.__noun_chunks = list(self.__nlp.noun_chunks)
        self.__get_basic_details()

    def get_extracted_data(self):
        return self.__details

    def __get_basic_details(self):
        name = utils.extract_name(self.__nlp, matcher=self.__matcher)
        email = utils.extract_email(self.__text)
        mobile = utils.extract_mobile_number(self.__text, self.__custom_regex)
        skills = utils.extract_skills(
            self.__nlp, self.__noun_chunks, self.__skills_file
        )
        linkedin_profile = utils.extract_linkedin(self.__text)
        gender = utils.extract_gender(self.__text)

        # entities = utils.extract_entity_sections_grad(self.__text_raw)

        # extract name
        self.__details["name"] = name

        # extract email
        self.__details["email"] = email

        # extract mobile number
        self.__details["mobile_number"] = mobile

        # extract skills
        self.__details["skills"] = skills

        self.__details["linkedin_profile"] = linkedin_profile

        self.__details["gender"] = gender

        # extract college name
        # try:
        #     self.__details["college_name"] = entities["College Name"]
        # except KeyError:
        #     pass

        # # extract education Degree
        # try:
        #     self.__details["degree"] = cust_ent["Degree"]
        # except KeyError:
        #     pass

        # # extract designation
        # try:
        #     self.__details["designation"] = cust_ent["Designation"]
        # except KeyError:
        #     pass

        # # extract company names
        # try:
        #     self.__details["company_names"] = cust_ent["Companies worked at"]
        # except KeyError:
        #     pass

        # try:
        #     self.__details["experience"] = entities["experience"]
        #     try:
        #         exp = round(utils.get_total_experience(entities["experience"]) / 12, 2)
        #         self.__details["total_experience"] = exp
        #     except KeyError:
        #         self.__details["total_experience"] = 0
        # except KeyError:
        #     self.__details["total_experience"] = 0
        # self.__details["no_of_pages"] = utils.get_number_of_pages(self.__resume)
        # return


if __name__ == "__main__":
    rs = ResumeParser("./data/resumes/kal.pdf")
    with open("output.json", "w", encoding="utf-8") as stream:
        stream.write(json.dumps(rs.get_extracted_data(), indent=4))
