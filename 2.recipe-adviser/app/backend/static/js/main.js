/**
 * Copyright (c) Microsoft Corporation.
 * Licensed under the MIT License.
 */

/*  ---------------------------------------------------
  Template Name: Deerhost
  Description:  Deerhost Hosting HTML Template
  Author: Colorlib
  Author URI: https://colorlib.com
  Version: 1.0
  Created: Colorlib
---------------------------------------------------------  */

"use strict";

(function ($) {
  /*------------------
        Preloader
    --------------------*/
  $(window).on("load", () => {
    $(".loader").fadeOut();
    $("#preloder").delay(200).fadeOut("slow");
  });

  /*------------------
        Background Set
    --------------------*/
  $(".set-bg").each(() => {
    var bg = $(this).data("setbg");
    $(this).css("background-image", "url(" + bg + ")");
  });

  //Canvas Menu
  $(".canvas__open").on("click", () => {
    $(".offcanvas__menu__wrapper").addClass("show__offcanvas__menu");
    $(".offcanvas__menu__overlay").addClass("active");
  });

  $(".canvas__close, .offcanvas__menu__overlay").on("click", () => {
    $(".offcanvas__menu__wrapper").removeClass("show__offcanvas__menu");
    $(".offcanvas__menu__overlay").removeClass("active");
  });

  /*------------------
        Accordin Active
    --------------------*/
  $(".collapse").on("shown.bs.collapse", () => {
    $(this).prev().addClass("active");
  });

  $(".collapse").on("hidden.bs.collapse", () => {
    $(this).prev().removeClass("active");
  });

  /*------------------
        Radio btn
    --------------------*/
  $(".pricing__swipe-btn label").on("click", function (e) {
    $(".pricing__swipe-btn label").removeClass("active");
    $(this).addClass("active");

    if (e.target.htmlFor == "month") {
      $(".yearly__plans").removeClass("active");
      $(".monthly__plans").addClass("active");
    } else if (e.target.htmlFor == "yearly") {
      $(".monthly__plans").removeClass("active");
      $(".yearly__plans").addClass("active");
    }
  });

  /*------------------
        Achieve Counter
    --------------------*/
  $(".achieve-counter").each(() => {
    $(this)
      .prop("Counter", 0)
      .animate(
        {
          Counter: $(this).text(),
        },
        {
          duration: 4000,
          easing: "swing",
          step: function (now) {
            $(this).text(Math.ceil(now));
          },
        }
      );
  });
})(jQuery);
