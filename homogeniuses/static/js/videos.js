var video_id = document.getElementById("vid").dataset.video_id;

const homo_button = document.querySelector("button.hvote");
const genius_button = document.querySelector("button.gvote");
const homo_votes = document.querySelector("span.hcount");
const genius_votes = document.querySelector("span.gcount");
const score_bars = document.querySelectorAll(".score-bar .bar")


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

function update_bar_widths() {
    if (score_bars.length != 2) {
        return;
    }

    hvotes = score_bars[0].dataset.votes;
    gvotes = score_bars[1].dataset.votes;

    if (hvotes == 0 && gvotes == 0) {
        return;
    }

    genius_width = 0;
    homo_width = 0;

    if (hvotes == 0) {
        console.log("Zero homo votes");
        genius_width = 100;
        homo_width = 0;
    }
    else if (gvotes == 0) {
        console.log("Zero genius votes");
        homo_width = 100;
        genius_width = 0;
    }
    else if (hvotes == gvotes) {
        console.log("Equal votes");
        homo_width = 50;
        genius_width = 50;
    }
    else {
        total_votes = Number(hvotes) + Number(gvotes);
        console.log(`total votes: ${total_votes}`);
        homo_width = (100 * hvotes) / total_votes;
        console.log(`homo width: ${homo_width}`);
        genius_width = 100 - homo_width;
        console.log(`genius width: ${genius_width}`);

    }
    console.log(homo_width);
    console.log(genius_width);

    // homo
    score_bars[0].style.width = `${homo_width}%`;
    score_bars[1].style.width = `${genius_width}%`;
}

update_bar_widths();