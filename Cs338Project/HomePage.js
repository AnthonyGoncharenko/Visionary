
   

    
  let testHeader = "Blog Title - Post title ";
  let testImage = "https://www.multimediaxp.com/images/article_190508124638.1557333998.jpg";
  let testString  = " Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam aliquam, sem id porttitor congue, nunc leo consequat diam, non euismod magna justo at risus. Ut vel lobortis odio. Sed sollicitudin placerat porttitor.Suspendisse posuere justo sed turpis dictum, sit amet imperdiet magna scelerisque. Aliquam erat volutpat.Integer consequat iaculis laoreet. Curabitur placerat leo leo, at varius justo congue imperdiet. Nulla mattismolestie augue id rhoncus. Nulla dictum bibendum neque, quis commodo elit ultrices et. Aenean fermentum tortorid lorem lacinia, a elementum neque ultrices. Donec mattis libero in nulla venenatis, ut iaculis est efficitur."

  function FillPost(PH,PI,PS) //fills post element to left side of homepage
    {
      //header
      let PostHeader = document.getElementById("PostHeader")
      PostHeader.className = "Postheader";
      PostHeader.textContent = PH;

      //image
      let PostImage = document.getElementById("PostImage")
      PostImage.className = "PostImage";
      PostImage.src = PI;

      //TextContent
      let PostText = document.getElementById("PostText")
      PostText.className = "PostText";
      PostText.textContent = PS;
      
    }
  FillPost(testHeader,testImage,testString);
    
