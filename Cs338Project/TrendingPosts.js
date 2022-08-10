function CreatePostTable(col) //generate inital state
{
  let board = document.getElementById("TrendingPostTable");

  let tr = document.createElement("tr");


  //add eleements to post table
  for (let c1 = 0; c1 < 1; c1++) {
    let th = document.createElement("th");
    for (let c2 = 0; c2 <= col; c2++) {
      if (c2 == 0) {
        //Post Table head element
        let head = document.createElement("div");
        head.className = 'PostListHead';
        head.textContent = "Trending Posts";
        th.append(head);
      }
      else {
        th.className = 'PostListElement';
        let PostTableBtn = document.createElement("button")
        PostTableBtn.className = 'PostTableButton';
        PostTableBtn.textContent = "Post Title";
        th.append(PostTableBtn);
      }


    }
    tr.append(th);
  }

  board.append(tr);
}

CreatePostTable(10) //creates a table of 10 posts (Excluding head element or "TRENDING POSTS" block)