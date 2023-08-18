# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

# Get the company description
# this function is important to generatig GPT embedding for company search. It is also used teaching knowledge to ChatGPT for "Prompt Learning".
# You must include competitor name (e.g. when Tesla, competiror is GM). When you search Tesla embedding on RediSearch, Tesla will be the first record, GM is second.
def get_company_description(locale, data, years, revenues, operating_profits, operating_profit_margins, total_assets, equity_ratios):
    description = ""
    
    if locale == "en-us":
        description = \
            f'The securities code is {data["securities_code"]}, ' + \
            f'the industry is {data["industry"]}, ' + \
            f'the representative is {data["representative"]}, ' + \
            f'the establishment date is {data["establishment_date"]}, ' + \
            f'the capital is {data["capital"]}, ' + \
            f'the major shareholders are {data["major_shareholders"]}, ' + \
            f'the business description is {data["business_description"]}, ' + \
            f'the number of employees is {data["number_of_employees"]}, ' + \
            f'the location is {data["location"]}, ' + \
            f'the revenue was {revenues[0]} in {years[0]}, {revenues[1]} in {years[1]}, and {revenues[2]} in {years[2]}, ' + \
            f'the operating profit was {operating_profits[0]} in {years[0]}, {operating_profits[1]} in {years[1]}, and {operating_profits[2]} in {years[2]}, ' + \
            f'the operating profit margin was {operating_profit_margins[0]} in {years[0]}, {operating_profit_margins[1]} in {years[1]}, and {operating_profit_margins[2]} in {years[2]}, ' + \
            f'the total assets was {total_assets[0]} in {years[0]}, {total_assets[1]} in {years[1]}, and {total_assets[2]} in {years[2]}, ' + \
            f'the equity ratio was {equity_ratios[0]} in {years[0]}, {equity_ratios[1]} in {years[1]}, and {equity_ratios[2]} in {years[2]}, ' + \
            f'the listed market is {data["listed_market"]}.'
    elif locale == "ja-jp":
        description = \
            f'証券コードは{data["securities_code"]}、' + \
            f'業種は{data["industry"]}、' + \
            f'代表者は{data["representative"]}、' + \
            f'設立年月日は{data["establishment_date"]}、' + \
            f'資本金は{data["capital"]}、' + \
            f'主要株主は{data["major_shareholders"]}、' + \
            f'事業内容は{data["business_description"]}、' + \
            f'従業員数は{data["number_of_employees"]}、' + \
            f'所在地は{data["location"]}、' + \
            f'売上高は{years[0]}年が{revenues[0]}、{years[1]}年が{revenues[1]}、{years[2]}年が{revenues[2]}、' + \
            f'営業利益は{years[0]}年が{operating_profits[0]}、{years[1]}年が{operating_profits[1]}、{years[2]}年が{operating_profits[2]}、' + \
            f'営業利益率は{years[0]}年が{operating_profit_margins[0]}、{years[1]}年が{operating_profit_margins[1]}、{years[2]}年が{operating_profit_margins[2]}、' + \
            f'総資産は{years[0]}年が{total_assets[0]}、{years[1]}年が{total_assets[1]}、{years[2]}年が{total_assets[2]}、' + \
            f'総資産は{years[0]}年が{equity_ratios[0]}、{years[1]}年が{equity_ratios[1]}、{years[2]}年が{equity_ratios[2]}、' + \
            f'上場市場は{data["listed_market"]} ' + \
            'です。'

    return description
