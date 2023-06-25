// Copyright (c) Microsoft Corporation.
// Originally written by Haruo Shibuya on 2023/3/25.
// Licensed under the MIT license.

// Global variables
let g_locale = "";
let g_company_name = "";
let g_company_info = "";

$(document).ready(function () {
  $("#warning").hide();
  $("#demo-container").show();

  show_search_box();

  $("#searchCompanyText").keypress(function (e) {
    if (e.which == 13) {
      $("#searchCompanyButton").click();
    }
  });
  $("#searchCompanyButton").click(async function () {
    let company_name = $("#searchCompanyText").val();
    if (company_name.length > 0) {
      $("#tableMain").addClass("hide");

      const response = await search_knowledge_base(company_name);
      const data = response[0];

      // locale (e.g. en-us, ja-jp)
      g_locale = data.locale;
      // company name
      g_company_name = data.name;
      // company info
      g_company_info = data.text;
      // dispatch knowledge base data and ChatGPT result to HTML
      // category_company is defined in wwwroot\js\app\locale.js
      set_html_data(
        category_company,
        "",
        true,
        g_company_name,
        g_company_info,
        g_locale,
        data
      );

      $("#tableMain").removeClass("hide");
      $("#tableAnalysis").removeClass("hide");
    }
  });
  $("#finance_analyze_feedback_text, #market_trend_feedback_text").keypress(
    function (e) {
      if (e.which == 13) {
        const match = $(this)
          .attr("id")
          .match(/(\w+)_feedback_text/);
        match ? $("#" + match[1] + "_feedback_button").click() : null;
      }
    }
  );
  $("#finance_analyze_feedback_button, #market_trend_feedback_button").click(
    async function () {
      const match = $(this)
        .attr("id")
        .match(/(\w+)_feedback_button/);
      match ? send_analysis_feedback(match[1]) : null;
    }
  );
});

async function send_analysis_feedback(category) {
  const input_element = $("#" + category + "_feedback_text");
  const display_element = $("#" + category);

  const source = display_element.html();
  const question = get_category_prompt(category, g_locale);
  const feedback = input_element.val();

  const response = await axios.post(
    "/analysis_feedback",
    (body = {
      locale: g_locale,
      company_name: g_company_name,
      company_info: g_company_info,
      question: question,
      source: source,
      feedback: feedback,
      n: SEARH_ROWS,
    }),
    (config = {
      "Content-Type": "application/json",
    })
  );

  input_element.val("");
  display_element.html(response.data);
}
