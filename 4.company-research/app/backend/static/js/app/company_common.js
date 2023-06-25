// Copyright (c) Microsoft Corporation.
// Originally written by Haruo Shibuya on 2023/3/25.
// Licensed under the MIT license.

const SEARH_ROWS = 3;

function show_search_box() {
  // Disable Company Search Textbox and Button
  $("#searchCompanyText").show();
  $("#searchCompanyButton").show();
}

// search knowledge base API on Flask
async function search_knowledge_base(company_name) {
  const response = await axios.post(
    "/search_company",
    (body = {
      company_name: company_name,
    }),
    (config = {
      "Content-Type": "application/json",
    })
  );

  return response.data;
}

// text completion
async function completion_text(
  company_name,
  company_info,
  locale,
  question,
  n
) {
  const response = await axios.post(
    "/company_completion",
    (body = {
      company_name: company_name,
      company_info: company_info,
      locale: locale,
      question: question,
      n: n,
    }),
    (config = {
      "Content-Type": "application/json",
    })
  );

  return response.data;
}

// dispatch knowledge base data and ChatGPT result to HTML
function set_html_data(
  target,
  tag,
  set_label,
  company_name,
  company_info,
  locale,
  data
) {
  const keys = Object.keys(target);
  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];

    // Set label
    if (set_label) {
      if ($("#" + key + "_label").length)
        $("#" + key + "_label").html(target[key].text[locale]);
    }

    // Set value
    const element = $("#" + key + tag);
    if (element.length) {
      set_element_value(element, "");

      // Value form Knowledge base
      if (data.hasOwnProperty(key)) {
        set_element_html(element, data[key]);
      }
      //  Ask GPT
      else if (target[key].hasOwnProperty("question")) {
        const question = target[key]?.question[locale];

        completion_text(
          company_name,
          company_info,
          locale,
          question,
          SEARH_ROWS
        ).then((value) => {
          set_element_value(element, value);
        });
      }
      // Fixed value
      else if (target[key].hasOwnProperty("value")) {
        const value = target[key]?.value[locale];
        set_element_value(element, value);
      }
      // No attributes
      else {
        // do nothing, value is empty
      }
    }
  }
}

// get formatted HTML element value from json data
function set_element_html(element, item, unit = "") {
  let markup = "";
  let displayValue = "";

  if (Array.isArray(item)) {
    const itemNode = item[item.length - 1]; // Get the last element (e.g. [2020, 2021, 2022] take 2022)
    const keys = Object.keys(itemNode);
    displayValue = itemNode[keys[0]].toLocaleString();
  } else {
    displayValue = item.toLocaleString();
  }

  if (!isNaN(displayValue)) {
    if (parseInt(displayValue) < 0)
      markup = '<span style="color:red">' + displayValue + unit + "</span>";
    else markup = displayValue;
  } else {
    markup = displayValue;
  }

  set_element_value(element, markup);
}

// set value to html element
function set_element_value(element, value) {
  element.is("textarea") || element.is("input:text")
    ? element.val(value)
    : element.html(value);
}

function get_category_prompt(category, locale) {
  return category_company[category]["question"][locale];
}

const category_company = {
  caption_company: {
    text: {
      "en-us": "Company Information",
      "ja-jp": "企業分析",
    },
  },
  search_company: {
    text: {
      "en-us": "Company Information",
      "ja-jp": "企業情報",
    },
  },
  caption_proposal: {
    text: {
      "en-us": "Company Research Report",
      "ja-jp": "企業分析(レポート)",
    },
  },
  name: {
    text: {
      "en-us": "Company Name",
      "ja-jp": "会社名",
    },
  },
  representative: {
    text: {
      "en-us": "Representative",
      "ja-jp": "代表者",
    },
  },
  establishment_date: {
    text: {
      "en-us": "Established",
      "ja-jp": "設立",
    },
  },
  capital: {
    text: {
      "en-us": "Capital",
      "ja-jp": "資本金(百万)",
    },
  },
  major_shareholders: {
    text: {
      "en-us": "Major Shareholder",
      "ja-jp": "主要株主",
    },
  },
  business_description: {
    text: {
      "en-us": "Business Description",
      "ja-jp": "事業内容",
    },
  },
  number_of_employees: {
    text: {
      "en-us": "Number of Employees",
      "ja-jp": "従業員数",
    },
  },
  location: {
    text: {
      "en-us": "Address",
      "ja-jp": "所在地",
    },
  },
  listed_market: {
    text: {
      "en-us": "Listed Market",
      "ja-jp": "上場市場",
    },
  },
  financial_information: {
    text: {
      "en-us": "Financial Information",
      "ja-jp": "財務情報",
    },
  },
  revenue: {
    text: {
      "en-us": "Revenue",
      "ja-jp": "売上高(百万)",
    },
  },
  operating_profit: {
    text: {
      "en-us": "Operating Profit",
      "ja-jp": "営業利益(百万)",
    },
  },
  operating_profit_margin: {
    text: {
      "en-us": "Operating Profit Margin",
      "ja-jp": "営業利益率(%)",
    },
  },
  total_assets: {
    text: {
      "en-us": "Total Assets",
      "ja-jp": "総資産(百万)",
    },
  },
  equity_ratio: {
    text: {
      "en-us": "Equity Ratio(%)",
      "ja-jp": "自己資本比率(%)",
    },
  },

  business_description_report: {
    text: {
      "en-us": "Business Description",
      "ja-jp": "事業内容",
    },
    question: {
      "en-us":
        "Answer about this company's business, services offered, and products.",
      "ja-jp": "この企業の事業内容・提供サービス・商品",
    },
  },
  proprietor_report: {
    text: {
      "en-us": "Proprietor",
      "ja-jp": "経営者情報",
    },
    question: {
      "en-us": "About the management and board of directors of this company.",
      "ja-jp": "この企業の経営者・役員について",
    },
  },
  mid_term_management_plan: {
    text: {
      "en-us": "Mid-term management plan",
      "ja-jp": "中期経営計画",
    },
    question: {
      "en-us": "Answer about this company's mid-term management plan.",
      "ja-jp": "この企業の中期経営計画",
    },
  },
  recent_news: {
    text: {
      "en-us": "Recent news",
      "ja-jp": "最近のニュース",
    },
    question: {
      "en-us": "Recent news from this company.",
      "ja-jp": "この企業の最近のニュース",
    },
  },
  finance_analyze: {
    text: {
      "en-us": "Finance",
      "ja-jp": "財務状況",
    },
    question: {
      "en-us": "Analyze this company in terms of its financial condition.",
      "ja-jp": "この企業を財務状況の観点で分析して",
    },
  },
  market_trend: {
    text: {
      "en-us": "Market Trend",
      "ja-jp": "業界トレンド",
    },
    question: {
      "en-us": "Industry Trends for this Company.",
      "ja-jp": "この企業の業界トレンド",
    },
  },
};
