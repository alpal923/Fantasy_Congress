from bs4 import BeautifulSoup
import requests, re
from openai import OpenAI
import numpy as np
import csv


def get_bill_rating(statement):
    client = OpenAI()
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "You are to evaluate how authoritarian or libertarian a proposed bill is. Rate it on a scale to -1 to 1 where -1 is the most libertarian and 1 is the most authoritarian. Please answer with a number between -1 and 1. If you cannot evaluate it based on the given information, answer with a 0."},
        {"role": "user", "content": statement[:4097]}
        ]
    )
    generated_text_gov = completion.choices[0].message.content
    print(generated_text_gov)
    ratings = re.findall(r"-?0\.?[0-9]?", generated_text_gov)
    auth_lib_rate = np.mean([float(rating) for rating in ratings]) if len(ratings) > 0 else 0.0
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "You are to evaluate how left or right wing a proposed bill is. Rate it on a scale to -1 to 1 where -1 is the most left wing and 1 is the most right wing in the context of American politics. Please answer with a value between -1 and 1. If you cannot evaluate it based on the given information, answer with a 0."},
        {"role": "user", "content": statement[:4097]}
        ]
    )
    generated_text_pos = completion.choices[0].message.content
    print(generated_text_pos)
    ratings = re.findall(r"-?0\.?[0-9]?", generated_text_pos)
    left_right_rate = np.mean([float(rating) for rating in ratings]) if len(ratings) > 0 else 0.0
    return left_right_rate, auth_lib_rate


def generate_issues_csv():
    bill_statements = ["""This resolution impeaches President Joseph Robinette Biden for abuse of power by enabling bribery and other high crimes and misdemeanors.

    Specifically, the resolution sets forth an article of impeachment stating that, in his former role as Vice President, President Biden abused the power of that office through enabling bribery and other high crimes and misdemeanors by allowing his son Hunter Biden to influence the domestic policy of a foreign nation and accept benefits from foreign nationals in exchange for favors.

    The article states that, by such conduct, President Biden

        endangered the security of the United States and its institutions of government;
        threatened the integrity of the democratic system;
        interfered with the peaceful transition of power;
        imperiled a coordinate branch of government; and
        demonstrated that he will remain a threat to national security, democracy, and the Constitution if allowed to remain in office.

    The article also states that this conduct warrants immediate impeachment, trial, and removal from office and disqualification to hold and enjoy any office of honor, trust, or profit under the United States. """,
    """This bill repeals provisions that reduce Social Security benefits for individuals who receive other benefits, such as a pension from a state or local government.

    The bill eliminates the government pension offset, which in various instances reduces Social Security benefits for spouses, widows, and widowers who also receive government pensions of their own.

    The bill also eliminates the windfall elimination provision, which in some instances reduces Social Security benefits for individuals who also receive a pension or disability benefit from an employer that did not withhold Social Security taxes.

    These changes are effective for benefits payable after December 2023.""",
    """This bill addresses issues concerning family- and employment-based visas.

    The bill increases the annual per-country cap on family-based immigrant visas from 7% of the total number of such visas available to 15% and eliminates the per-country cap for employment-based immigrant visas.

    The bill establishes transition rules for employment-based visas such as (1) reserving a percentage of EB-2 (workers with advanced degrees or exceptional ability) and EB-3 (skilled and other workers) visas for individuals not from the two countries with the largest number of recipients of such visas, and (2) allotting a number of visas for professional nurses and physical therapists.

    The bill imposes additional requirements for H-1B visas, such as prohibiting (1) an employer from advertising that a position is limited to H-1B applicants or that H-1B applicants are preferred, and (2) certain employers from having more than half of their employees as nonimmigrant visa workers.

    The Department of Labor shall create a publicly available website where an employer seeking an H-1B visa must post information about the open position.

    The bill also expands Labor's authority to investigate H-1B applications for fraud or misrepresentations.

    The bill also prohibits H-1B or H-3 (trainee or special education exchange) visas for nationals of a foreign adversary country for employment in any matter vital to U.S. national interests.

    The bill also allows certain nonimmigrant visa holders to obtain lawful permanent resident status if the individual (1) has an approved immigrant visa petition, and (2) has waited at least two years for a visa. """]

    position_data = [["Ratings", "Presidential Impeachment", "Social Security", "Immigrant Visas"]]
    left_right_row = ["Left/Right"]
    auth_lib_row = ["Auth/Lib"]
    for statement in bill_statements:
        left_right_rate, auth_lib_rate = get_bill_rating(statement)
        left_right_row += [left_right_rate]
        auth_lib_row += [auth_lib_rate]
    position_data += [left_right_row]
    position_data += [auth_lib_row]
    print(position_data)
    with open("bill_ratings.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(position_data)


if __name__ == "__main__":
    generate_issues_csv()
