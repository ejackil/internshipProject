
    function myFunction() {
      var dots = document.getElementById("dotsId");
      var moreText = document.getElementById("moreId");
      var btnText = document.getElementById("btnId");

      if (dots.style.display == "none") {
          dots.style.display = "inline";
          btnText.innerHTML = "Read more";
          moreText.style.display ="none";
      } else {
          dots.style.display = "none";
          btnText.innerHTML = "Read less";
          moreText.style.display = "inline";
      }
   }