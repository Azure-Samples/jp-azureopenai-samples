/*
Copyright (C) Haruo Shibuya 2023/3/25
Created for Microsoft Open AI Solutions Demo
*/

// ================================================================================
// Setup
// ================================================================================
// default ingredients list
const INGREDIENTS_HAVE_LIST = [
  "豚ひき肉",
  "牛すね肉",
  "鶏むね肉",
  "レタス",
  "きゅうり",
  "玉ねぎ",
  "米",
  "パン",
  "卵",
  "豆",
  "牛乳",
  "りんご",
  "パスタ麺",
];

$(() => {
  // initialize UI
  $("#warning").hide();
  $("#demo-container").show();
  // set ingredients have list
  $("#ingredients_have").val(INGREDIENTS_HAVE_LIST.join("\n"));
  drawShopFloorLayout();

  // set menu button event
  $("#menu_button").click(async () => {
    $("#loading_text").html("AI がおすすめメニューを思考中 ...");
    await createMenu()
  });

  // set advisory button event
  $("#advisory_button").click(async () => {
    $("#loading_text").html("AI が栄養アドバイスを思考中 ...");
    $("#warning").show();
    createNutritionAdvisory();
    $("#warning").hide();
  });

  // set stock table hover event
  $(document).on("mouseover", ".stock_row", function() {
    highlightBlock($(this));
  });

  // set stock table unhover event
  $(document).on("mouseout", ".stock_row", async () => {
    removeHighlight();
  });
});


//================================================================================================================================================
// main function
//================================================================================================================================================
const createMenu = async () => {
  $("#warning").show();
  // hide UI
  $("#menu_image").hide();
  $("#tableMenu").hide();
  // create menu text contents
  const response = await getRecommendMenuFromGPT()
  setRecommendMenu(response)
  $("#tableMenu").show();
  $("#warning").hide();
  
  // create menu image contents
  const image_url = await getMainDishImage(response.main_dish)
  setMainDishImage(image_url)
  $("#menu_image").show();
}

const createNutritionAdvisory = async () => {
  $("#tableAdvisor").hide();
  const family_profile = getFamilyProfile();
  const [health_data, missing_nutrient] = generateRandomMissingNutrient();
  const data = await getAdvisoryFromGPT(family_profile, missing_nutrient);
  setAdvisory(data, missing_nutrient)
  drawRadarChart(health_data)
  $("#tableAdvisor").show();
}

//================================================================================================================================================
// Menu
//===============================================================================================================================================
// get menu recommendation from GPT
const getRecommendMenuFromGPT = async () => {
  const url = "/food_receipe";
  const body = {
    family_profile: getFamilyProfile(),
    ingredients_have: $("#ingredients_have").val().split("\n"),
    user_menu_request: $("#user_menu_request").val(),
  };

  const header = {
    "Content-Type": "application/json",
  };

  // get menue recommendation from API
  try {
    const {data} = await axios.post(url, body, header)
    return data
  } catch (error) {
    console.error(`failed to get menu recommendation: ${error}`);
  }
}

// set menu recommendation to UI
const setRecommendMenu = (data) => {
  // set recommend menu to UI
  $("#menu").val(data.menu.trim());
  // set recommend reason to UI
  $("#reason").val(data.reason.trim().replace(/(\r\n|\n|\r)/gm, ""));
  // set recommend ingredients to UI
  $("#ingredients").val(data.ingredients_with_amount.trim());
  
  // set recommend recipe to UI
  const recipeContent = data.recipes.map((recipe) => {
    return `[${recipe.menu.trim()}]\n${recipe.step.trim()}`
  }).join('\n')
  $("#recipe").val(recipeContent);

  // Render stock table
  const ingredients_not_have_list = data.ingredients_not_have
  .trim()
  .replace(/['\[\]]/g, "")
  .split(/[,、・]/)
  .map((s) => s.trim());
  renderStockTable(ingredients_not_have_list);
}

//================================================================================================================================================
// Image
//================================================================================================================================================
const getMainDishImage = async (main_dish_name) => {
  const url = "/food_image";
  const body = {
    food_name: main_dish_name,
  };
  const header = {
    "Content-Type": "application/json",
  };

  try {
    const {data} = await axios.post(url, body, header)
    return data
  } catch (error) {
    console.error(`failed to get image generation: ${error}`);
  }
}

const setMainDishImage = (image_url) => {
  $("#menu_image").attr("src", image_url);
  $("#menu_image").show();
}

//================================================================================================================================================
// Advisory
//================================================================================================================================================
// generate advisory from GPT
const getAdvisoryFromGPT = async(family_profile, missing_nutrient) => {
  const url = "/food_advisory";
  const body = {
    family_profile: family_profile,
    missing_nutrient: missing_nutrient,
  };
  const header = {
    "Content-Type": "application/json",
  };

  try {
    const {data} = await axios.post(url, body, header)
    return data
  } catch (error) {
    console.error(`failed to get advisory: ${error}`);
  }
}

// set advisory to UI
const setAdvisory = (data, missing_nutrient) => {
  const adviseText = `${missing_nutrient}
    ${data.recommend_reason}
    おすすめの食材は以下の通りです。\n
    ${data.recommended_ingredients}\n
    ${data.recommend_ingredients_reason}\n
    ${data.recommend_ingredients_cooking}`
  $("#advisory").val(adviseText);
  
  // Render eCommerce table
  const recommended_ingredients_list = data.recommended_ingredients
    .trim()
    .replace(/^\s+/, "")
    .split(/[,、・]/)
    .map((s) => s.trim());
  renderECommerceTable(recommended_ingredients_list);
}

// generate random missing nutrient from HEALTH_NUTRIENT
const generateRandomMissingNutrient = () => {
  const HEALTH_NUTRIENT = [
    "タンパク質",
    "脂質",
    "炭水化物",
    "食物繊維",
    "ビタミン",
    "ミネラル",
  ];

   // create random nutrient values
   const nutrient_values = [];
   for (let i = 0; i < HEALTH_NUTRIENT.length; i++) {
     const random_value = Math.floor(Math.random() * (9 - 5 + 1)) + 5;
     nutrient_values.push(random_value);
   }
   const min_index = nutrient_values.indexOf(Math.min(...nutrient_values));
   return [nutrient_values, HEALTH_NUTRIENT[min_index]];
}

// render eCommerce table
const renderECommerceTable = (recommended_ingredients_list) => {
  const tableHTML = recommended_ingredients_list.map((item) => {
    return `
    <tr>
      <td>${item.trim()}</td>
      <td><a href='https://www.microsoft.com/' target='_blank'>定期購入</a></td>
    </tr>
    `
  })
  $("#ecommerce_table").html(tableHTML);
}

const drawRadarChart = (health_data) => {
  const elem = document.getElementById("healthChart");
  var clone = elem.cloneNode(false);
  elem.parentNode.replaceChild(clone, elem);

  recommended_health_data = [8, 8, 8, 8, 8, 8];

  // chart data
  const chartData = {
    labels: [
      "タンパク質",
      "脂質",
      "炭水化物",
      "食物繊維",
      "ビタミン",
      "ミネラル",
    ],
    datasets: [
      {
        label: "ご家族 健康スコア",
        data: health_data,
        backgroundColor: "rgba(255, 255, 255, 0.2)",
        borderColor: "rgba(255, 99, 132, 1)",
        borderWidth: 3,
      },
      {
        label: "望ましい健康スコア",
        data: recommended_health_data,
        backgroundColor: "rgba(255, 255, 255, 0.2)",
        borderColor: "rgba(99, 255, 132, 1)",
        borderWidth: 2,
      },
    ],
  };

  // chart options
  const chartOptions = {
    scales: {
      r: {
        max: 10,
        min: 0,
        ticks: {
          stepSize: 1,
        },
        pointLabels: { fontSize: 18 },
      },
    },
    legend: { position: "bottom" },
  };

  // draw chart
  const ctx = document.getElementById("healthChart").getContext("2d");
  new Chart(ctx, {
    type: "radar",
    data: chartData,
    options: chartOptions,
  });
}

//================================================================================================================================================
// Floor Layout
//================================================================================================================================================
const drawShopFloorLayout = () => {
  const floor_block_list = ["A", "B", "C", "D", "E"];

  const width = 150;
  const height = 200;
  const margin = 30;
  const aisle = 50;

  f_width = width * floor_block_list.length + aisle * floor_block_list.length;
  f_height = width / 2;

  let x = margin;
  let y1 = f_height + aisle;
  let y2 = y1 + height + aisle;
  const fontsize = 96;

  const svg =`
  <svg xmlns='http://www.w3.org/2000/svg' id='product-map' class='floor' viewBox='0 0 1200 800'>
    <rect x="${margin}" y="${0}" width="${f_width}" height="${f_height}" id="F1" class="block" />
    <text x="${f_width / 2}" y="${f_height / 2}" font-size="${fontsize}" class="block-text">F1</text>
    ${floor_block_list.map((item) => {
      const content = `
      <rect x="${x}" y="${y1}" width="${width}" height="${height}" id="${item}1" class="block" />
      <text x="${x + width / 2}" y="${y1 + height / 2}" font-size="${fontsize}" class="block-text">${item}1</text>
      <rect x="${x}" y="${y2}" width="${width}" height="${height}" id="${item}2" class="block" />
      <text x="${x + width / 2}" y="${y2 + height / 2}" font-size="${fontsize}" class="block-text">${item}2</text>
      `
    x += width + margin * 2;
    return content
    })}
    <rect x="${margin}" y="${y2 + height + aisle}" width="${f_width}" height="${f_height}" id="F2" class="block" />
    <text x="${margin + f_width / 2}" y="${y2 + height + aisle + f_height / 2}" font-size="${fontsize}" class="block-text">F2</text>
  </svg>
  `

  $("#floor_layout").html(svg);
  removeHighlight(null);
}

const renderStockTable = (ingredients_not_have_list) => {
  const stock_label = ["在庫あり", "在庫わずか"];
  const stock_point = ["ポイント2倍", ""];
  const floor_block_list = ["A", "B", "C", "D", "E", "F"];

  let tableHTML = "<tr><th>商品</th><th>在庫</th><th>エリア</th><th></th></tr>";

  ingredients_not_have_list.forEach((item) => {
    if (item.trim() !== "") {
      tableHTML += `
      <tr class='stock_row'>
        <td>${item.trim()}</td>
        <td>${stock_label[Math.floor(Math.random() * stock_label.length)]}</td>
        <td>${floor_block_list[Math.floor(Math.random() * floor_block_list.length)]}${Math.floor(Math.random() * 2) + 1}</td>
        <td style='color:red'>${stock_point[Math.floor(Math.random() * stock_point.length)]}</td>
      </tr>
      `
    }
  });
  $("#stock_table").html(tableHTML);
}

const highlightBlock = (event) => {
  const row = event[0];
  
  const cells = row.cells;
  const cell = cells[2];
  const area = cell.innerText;

  const blocks = document.querySelectorAll(".block");
  for (let i = 0; i < blocks.length; i++) {
    blocks[i].setAttribute("stroke", "none");
  }

  const block = document.getElementById(area);
  block.setAttribute("fill", "LightSkyBlue");
}

const removeHighlight = () => {
  const blocks = document.querySelectorAll(".block");
  for (let i = 0; i < blocks.length; i++) {
    blocks[i].setAttribute("fill", "none");
  }
}

//================================================================================================================================================
// Util functions
// =================================================================================================================================================

// get ingredients list from form input
const getFamilyProfile = () => {
  const family_name_01 = $("#family_name_01").html();
  const family_profile_01 = $("#family_profile_01").val();
  const family_name_02 = $("#family_name_02").html();
  const family_profile_02 = $("#family_profile_02").val();
  const family_name_03 = $("#family_name_03").html();
  const family_profile_03 = $("#family_profile_03").val();
  const family_name_04 = $("#family_name_04").html();
  const family_profile_04 = $("#family_profile_04").val();

  return `${family_name_01}と${family_name_02}と${family_name_03}と${family_name_04}です。${family_name_01}は${family_profile_01}、${family_name_02}は${family_profile_02}、${family_name_03}は${family_profile_03}、${family_name_04}は${family_profile_04}`;
}