var video_id = document.getElementById("vid").dataset.video_id;

const homo_button = document.querySelector("button.hvote");
const genius_button = document.querySelector("button.gvote");
const homo_votes = document.querySelector("span.hcount");
const genius_votes = document.querySelector("span.gcount");


function cast_vote(evt) {
    const vote_type = evt.currentTarget;
    if (vote_type.classList.contains("hvote")) {
        const vote_url = `/vid/${video_id}/hvote`;
        fetch(vote_url)
            .then(response => response.json())
            .then(data => {
                if (data.success == true) {
                    homo_votes.innerHTML = Number(homo_votes.innerHTML) + 1;
                }
            });
    }

    else if (vote_type.classList.contains("gvote")) {
        const vote_url = `/vid/${video_id}/gvote`;
        fetch(vote_url)
            .then(response => response.json())
            .then(data => {
                if (data.success == true) {
                    genius_votes.innerHTML = Number(genius_votes.innerHTML) + 1;
                }
            });
    }
}

homo_button.addEventListener("click", cast_vote)
genius_button.addEventListener("click", cast_vote)

