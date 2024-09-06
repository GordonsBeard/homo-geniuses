var video_id = document.getElementById("vid").dataset.video_id;

const homo_button = document.querySelector("button.hvote");
const genius_button = document.querySelector("button.gvote");
const homo_votes = document.querySelector("span.hcount");
const genius_votes = document.querySelector("span.gcount");
const score_bar_cont = document.querySelector(".score-bar");
const score_bars = document.querySelectorAll(".score-bar .bar");
const already_voted = document.querySelector(".votes .already-voted");
const sentiment = document.querySelector(".sentiment");

function cast_vote(evt) {
    const vote_type = evt.currentTarget;
    if (vote_type.classList.contains("hvote")) {
        const vote_url = `/vid/${video_id}/hvote`;
        fetch(vote_url)
            .then(response => response.json())
            .then(data => {
                if (data.success == true) {
                    homo_votes.innerHTML = Number(homo_votes.innerHTML) + 1;
                    already_voted.innerHTML = "You have voted: homo";
                }
            });
            score_bars[0].dataset.votes = Number(score_bars[1].dataset.votes) + 1;
    }

    else if (vote_type.classList.contains("gvote")) {
        const vote_url = `/vid/${video_id}/gvote`;
        fetch(vote_url)
            .then(response => response.json())
            .then(data => {
                if (data.success == true) {
                    genius_votes.innerHTML = Number(genius_votes.innerHTML) + 1;
                    already_voted.innerHTML = "You have voted: genius";
                }
            });
            score_bars[1].dataset.votes = Number(score_bars[1].dataset.votes) + 1;
        }
    
    totalVotes = Number(score_bars[0].dataset.votes) +   Number(score_bars[1].dataset.votes);
    if (score_bar_cont.classList.contains("hidden")) { 
        sentiment.innerHTML = "Too few votes to certify results, 10 needed.";
        if (totalVotes >= 10){
            score_bar_cont.classList.remove("hidden");
        }
    }

    update_bar_widths();
}

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
        genius_width = 100;
        homo_width = 0;
    }
    else if (gvotes == 0) {
        homo_width = 100;
        genius_width = 0;
    }
    else if (hvotes == gvotes) {
        homo_width = 50;
        genius_width = 50;
    }
    else {
        total_votes = Number(hvotes) + Number(gvotes);
        homo_width = Math.floor((100 * hvotes) / total_votes);
        genius_width = 100 - homo_width;

    }

    score_bars[0].style.width = `${homo_width}%`;
    score_bars[1].style.width = `${genius_width}%`;
}

homo_button.addEventListener("click", cast_vote)
genius_button.addEventListener("click", cast_vote)
update_bar_widths();