 
    //submit function

    function SubmiSignUpFunc() {
    document.getElementById("SignUp").submit();
  }

    //String check if strings are same, not working, not sure how to approach //referenced source: https://codepen.io/diegoleme/pen/qBpyvr?editors=1111
    var password = document.getElementById("password")
    var confirm_password = document.getElementById("confirm_password");
    var email = document.getElementById("email")
    var confirm_email = document.getElementById("confirm_email");

    function ValidateString() {
      if (password.value != confirm_password.value || email.value != confirm_email.value) //
      {
        //strings dont match
      }
      else {
        //strings match
      }
    }

    password.onchange = ValidateString; //when even happens
    confirm_password.onkeyup = ValidateString; //as soon as person finished typing and lifts finger off key calss function

    email.onchange = ValidateString;
    confirm_email.onkeyup = ValidateString;
  