

function SubmitPostFunc() {
  document.getElementById("makePost").submit();
}


//counter for post box
document.querySelector("#description1").addEventListener("input", function countWord() // source https://www.geeksforgeeks.org/how-to-make-a-word-count-in-textarea-using-javascript/
{
  let res = [];
  let str = this.value.replace(/[\t\n\r\.\?\!]/gm, " ").split(" ");
  str.map((s) => {
    let trimStr = s.trim();
    if (trimStr.length > 0) {
      res.push(trimStr);
    }
  });
  document.querySelector("#wordcount").innerText = res.length;
});



//////code for image display element
const image_input = document.querySelector("#image_input"); //get image input
var image = "";
image_input.addEventListener("change", function () {
  const reader = new FileReader(); //use file reader object to read file
  reader.addEventListener("load", () => //add event listener load
  {
    image = reader.result; //set global variable to uploaded file in reader
    document.querySelector("#display_image").style.backgroundImage = `url(${image})`; //set display_image element to uploaded image 
  });
  reader.readAsDataURL(this.files[0]);
});