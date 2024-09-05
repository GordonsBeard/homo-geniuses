"""Videos, the main interaction segment of the website (votes and stuff too)"""

import dataclasses
from functools import wraps
import random
import re

from flask import Blueprint, flash, redirect, render_template, request, url_for, session
import flask_login #type: ignore
from flask_login import login_required
from wtforms import Form, HiddenField, StringField, ValidationError #type: ignore

from homogeniuses import db

bp = Blueprint("videos", __name__, url_prefix="/vid")

YOUTUBE_REGEX = re.compile(r"^(?:https?:\/\/)?(?:m\.|www\.)?(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|shorts\/|watch\?.+&v=))((\w|-){11})(?:\S+)?$")

@dataclasses.dataclass
class Video:  # pylint: disable=missing-class-docstring
    video_id: str
    homo_votes: int = 0
    genius_votes: int = 0


def fetch_video(video_id) -> Video | None:
    """Returns a single video from a given video_id"""
    select_video_sql = (
        """SELECT video_id, homo_votes, genius_votes FROM videos WHERE video_id = ?"""
    )
    video = db.query_db(select_video_sql, (video_id,), one=True)
    return Video(*video) if video else None


def get_all_videos() -> list[Video]:
    """Returns all videos currently in database"""
    get_all_videos_sql = """SELECT video_id, homo_votes, genius_votes FROM videos;"""
    all_videos = db.query_db(get_all_videos_sql)
    all_videos_list = [Video(*row) for row in all_videos]
    return all_videos_list


def get_random_video(steam_id=None) -> Video:
    """Returns just a single video from the list of all videos"""
    # Grab a video that a user hasn't voted on
    get_user_votes_sql = """SELECT video_id FROM votes WHERE steam_id = ?"""
    get_user_votes = db.query_db(get_user_votes_sql, (steam_id,))
    videos_voted_on = [x["video_id"] for x in get_user_votes]
    all_videos = get_all_videos()
    filtered_videos = [x for x in all_videos if x.video_id not in videos_voted_on]
    if steam_id and any(filtered_videos):
        return random.choice(filtered_videos)
    
    return random.choice(get_all_videos())


def add_video_to_db(video_id) -> None:
    """Takes a video id and initializes it into the database."""
    insert_video_sql = """INSERT INTO videos (video_id) VALUES = (?)"""
    db.insert_db(insert_video_sql, (video_id,))


@bp.route("/")
def no_video_id(steam_id=None):
    """If no video id was supplied just throw them to a random page"""
    
    if steam_id:
        pass

    random_video_id = get_random_video(steam_id).video_id
    return redirect(url_for('videos.video_page', video_id=random_video_id))


@bp.route("/random")
def random_video():
    """Random video selection."""
    steam_id = request.args["steam_id"] if "steam_id" in request.args else None
    return no_video_id(steam_id)

def get_user_votes_for_video(steam_id, video_id):
    """Checks to see if a user can cast another vote on this video."""
    get_user_votes_sql = """SELECT * FROM votes WHERE steam_id = ? AND video_id = ?"""
    result = db.query_db(get_user_votes_sql, (steam_id, video_id), one=True)
    return result["vote"] if result else None

@bp.route("/<video_id>")
def video_page(video_id):
    """Default view/page for watching a video."""
    fetched_video = fetch_video(video_id)
    if fetched_video is None:
        return "Bad video_id"
    user_steam_id = flask_login.current_user.steam_id if flask_login.current_user.is_authenticated else None
    users_prev_vote = get_user_votes_for_video(user_steam_id, video_id)
    session["video_id"] = video_id

    return render_template("videos/video_page.html", 
                           video=fetched_video, 
                           user=flask_login.current_user, 
                           users_prev_vote=users_prev_vote)


def cast_vote(video_id, vote_type, steam_id) -> bool:
    """Writes the vote to the database"""
    hvote_sql = """UPDATE videos SET homo_votes = ? WHERE video_id = ?"""
    gvote_sql = """UPDATE videos SET genius_votes = ? WHERE video_id = ?"""
    user_vote_sql = """INSERT INTO votes (steam_id, video_id, vote) VALUES (?, ?, ?)"""
    success = False
    video = fetch_video(video_id)
    if video:
        if vote_type == "hvote":
            success = db.insert_db(hvote_sql, (video.homo_votes + 1, video_id))
            success = db.insert_db(user_vote_sql, (steam_id, video_id, 0))
        elif vote_type == "gvote":
            success = db.insert_db(gvote_sql, (video.genius_votes + 1, video_id))
            success = db.insert_db(user_vote_sql, (steam_id, video_id, 1))
            

    return success


@bp.route("/<video_id>/<vote_type>")
def vote_on_video(video_id, vote_type):
    """Cast the vote for a video, called from client-side"""
    result = {"message": "Unknown vote logged", "success": False}
    if not video_id:
        result["message"] = "Invalid video_id"
        result["success"] = False

    if vote_type == "hvote":
        result["message"] = "homo vote logged"
        result["success"] = cast_vote(video_id, vote_type, flask_login.current_user.steam_id)
    elif vote_type == "gvote":
        result["message"] = "genius vote logged"
        result["success"] = cast_vote(video_id, vote_type, flask_login.current_user.steam_id)
    else:
        result["message"] = "unknown vote"
        result["success"] = False

    return result

class SubmitForm(Form):
    video_url = StringField("YouTube Video URL")

    def validate_video_url(form, field):
        if not YOUTUBE_REGEX.match(field.data):
            raise ValidationError("Invalid YouTube URL.")

def get_id_from_video_url(video_url):
    return YOUTUBE_REGEX.match(video_url).group(1)

@bp.route("/submit", methods=['GET', 'POST'])
@login_required
def submit_clip():
    form = SubmitForm(request.form)
    if request.method == 'POST' and form.validate():
        video_url = get_id_from_video_url(form.video_url.data)
        insert_into_queue_sql = """INSERT INTO queue (video_id, approval_status, submitter_id) VALUES (?, ?, ?)"""
        db.insert_db(insert_into_queue_sql, (video_url, 0, flask_login.current_user.steam_id))
        flash("Video submitted.")
    return render_template("videos/submit.html", form=form, user=flask_login.current_user)

def admins_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if flask_login.current_user.steam_id == "76561197965801299": # it's me!!!! :3
            return f(*args, **kwargs)
        return redirect(url_for("videos.no_vid_id"))
    return decorated_function

@bp.route("/queue")
@admins_only
def approval_queue():
    return "Approval queue"
