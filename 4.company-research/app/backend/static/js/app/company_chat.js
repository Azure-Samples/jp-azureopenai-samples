// Copyright (c) Microsoft Corporation.
// Licensed under the MIT license.

// Global variables
let g_locale = "";
let g_company_name = "";
let g_messages = [];

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
    let input_name = $("#searchCompanyText").val();
    if (input_name.length > 0) {
      $("#tableCompany").hide();
      $("#divChatData").empty();
      $("#displayChat").html($("#divChatData").val());

      await search_company(input_name, "");
      $("#sendChatText").val("");
      $("#sendChatText").focus();
    }
  });
  $("#sendChatText").keypress(function (e) {
    if (e.which == 13) {
      $("#sendChatButton").click();
    }
  });
  $("#sendChatButton").click(async function () {
    const input_text = $("#sendChatText").val();
    if (input_text.length > 0) send_chat(input_text);
  });
  $(document).on("click", ".btn-question", async function () {
    $("#sendChatText").val($(this).text());
    $("#sendChatButton").click();
  });
});

// Search company and fill the values.
async function search_company(company_name) {
  const items = await search_knowledge_base(company_name);
  const data = items[0];

  // locale (e.g. en-us, ja-jp)
  g_locale = data.locale;
  // company name
  g_company_name = data.name;
  // company info
  g_company_info = data.text;
  // message history
  g_messages = [];
  // dispatch knowledge base data and ChatGPT result to HTML
  // set_html_data is defined in wwwroot\js\app\company_common.js
  set_html_data(
    category_company,
    "_00",
    true,
    g_company_name,
    g_company_info,
    g_locale,
    data
  );

  $("#chatInputArea").show();
  $("#tableCompany").show();
}

// Chat with ChatGPT
async function send_chat(input_text) {
  // append your prompt the list
  add_prompt("user", input_text);

  // send prompt to ChatGPT
  const response = await axios.post(
    "/company_chat",
    (body = {
      locale: g_locale,
      company_name: g_company_name,
      company_info: g_company_info,
      messages: g_messages,
      n: SEARH_ROWS,
    }),
    (config = {
      "Content-Type": "application/json",
    })
  );

  // append ChatGPT response to the list
  add_prompt("assistant", response.data.content);

  set_datasource_links(response.data.data_source);

  // update chat conversation
  const current_time = new Date();
  const time_label = current_time.toLocaleString("en-US", {
    timeStyle: "medium",
    hour12: false,
  });

  $("#sendChatText").val("");
  $("#divChatData").prepend(
    "[" + time_label + "] " + input_text + "\n" + response.data.content + "\n\n"
  );
  $("#displayChat").html($("#divChatData").val());
  $("#displayChat").scrollTop(0);
}

// get prompt json
function add_prompt(role, text) {
  g_messages.push({
    role: role,
    content: text,
  });
}

// initialize datasource links
function set_datasource_links(topics, locale) {
  $("#dataSourceLinks").hide();
  $("#dataSourceLinks").empty();

  for (let i = 0; i < topics.length; i++) {
    const item = topics[i];
    const source = item.source;
    const label = item.label;
    if (source.length > 0 && label.length > 0) {
      let link_html =
        '<a href="' +
        source +
        '" class="link-primary" target="_blank">' +
        "[" +
        label +
        "]" +
        "</a> ";
      $("#dataSourceLinks").append(link_html);
    }
  }

  if ($("#dataSourceLinks a").length > 0) {
    switch (locale) {
      case "en-us":
        citation = "citation";
        break;
      default:
        citation = "引用";
        break;
    }

    $("#dataSourceLinks").prepend(citation + ": ");
    $("#dataSourceLinks").show();
  }
}
