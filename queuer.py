from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Float, func, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class Queue(Base):
    __tablename__ = 'queue'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), nullable=False)
    message = Column(String(255), nullable=False)
    channel = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    enqueued = Column(Boolean, nullable=False, default=lambda: False)
    q_duration_s = Column(Float, nullable=False, default=0.0)
    last_update_ts = Column(DateTime, nullable=False, default=datetime.utcnow)


def _build_waitlist(session, channel):
    rows = session.query(
        Queue
    ).filter(Queue.channel == channel).filter(Queue.enqueued.is_(False)).order_by(Queue.created_at).all()
    if not rows:
        return "The queue is empty.. :weary:"
    return "\n".join([f"{q.user_id}: *{q.message}*" for q in rows])


def _next_in_line(session):
    rows = session.query(
        Queue
    ).filter(Queue.enqueued.is_(False)).order_by(Queue.created_at).all()
    if rows:
        return rows[0]


def nq(session: Session, user, text, channel):
    row = session.query(
        Queue
    ).filter(Queue.user_id == user).filter(Queue.enqueued == 0).first()
    if row:
        row.message = text or "No message"
        session.add(row)
        session.commit()
        return f"{user} is already in the q, changing the reason deployment reason.. :thinking_face:"
    session.add(Queue(user_id=user, message=text or "No message", channel=channel))
    session.commit()
    rows = session.query(
        Queue
    ).filter(Queue.channel == channel).filter(Queue.enqueued.is_(False)).order_by(Queue.created_at).all()
    if len(rows) == 1:
        return f"{user} you are next to deploy :zap:"
    return f"{user} was added to the queue :clock4:"


def dq(session: Session, user, text, channel):
    next_in_line = _next_in_line(session)
    if next_in_line and next_in_line.user_id == user:
        next_in_line.enqueued = True

        updated_utc_timestamp = _convert_datetime_to_utc_timestamp(next_in_line.last_update_ts)
        next_in_line.q_duration_s = (_get_utc_timestamp_now() - updated_utc_timestamp)
        session.add(next_in_line)
        session.commit()

        # update next in line updated timestamp - this is done so that we will know when someone started blocking the q
        next_in_line = _next_in_line(session)
        if next_in_line:
            next_in_line.q_duration_s = 1
            session.add(next_in_line)
            session.commit()

        s = f"{user} finished to deploy :done1:"
        if next_in_line:
            s += f" {next_in_line.user_id} you are next in line. :checkered_flag:"
        return s
    row = session.query(
        Queue
    ).filter(Queue.channel == channel).filter(Queue.enqueued.is_(False)).filter(Queue.user_id == user).order_by(
        Queue.created_at).first()
    if not row:
        return f"{user} is not in the queue :blob-no: are you trying to trick me? :thinkingheads:"
    row.enqueued = True
    session.add(row)
    session.commit()
    return f"{user} just left the queue :cry: Please dont leave me like that again :broken_heart:"


def q(session, user, message, channel):
    return _build_waitlist(session, channel)


def resetq(session, user, message, channel):
    session.query(
        Queue
    ).filter(Queue.channel == channel).filter(Queue.enqueued.is_(False)).update({Queue.enqueued: True})
    session.commit()
    return f"{user} reset the queue.."


def credits(session, user, message, channel):
    return """
Yo im the the slack-queuer, you can add me to any channel and I will implement a FIFO Queue for you.. 
you just need to invite me to your deployment channel and I will start working like a charm!
the bot support the following commands:
`@raslasher q?` to get the current queue
`@raslasher nq <DEPLOY MESSAGE>` to take a ticket to the queue
`@raslasher dq` to leave the queue
`@raslasher blame` return statistics of users blocking the queue
`@raslasher resetq` to reset the q
the bot is running on lambda `slackbot-dev-hello` and store its state on ras-sandbox db under qq schema
if something doesnt work, you can blame :omer_sh: but try to fix it by yourself..
you can find the code here: <https://git.ridewithvia.dev/arch/via-q-bot|Via Q Bot @ gitlab>
and the logs here <https://us-east-1.console.aws.amazon.com/cloudwatch/home?region=us-east-1#logsV2:log-groups/log-group/$252Faws$252Flambda$252Fslackbot-dev-hello/log-events|Cloudwatch>
just verify you are under `rider-dev` aws account."""


def _days_to_secs(days: int) -> int:
    return days * 24 * 60 * 60


def _sec_to_hours(seconds: int) -> float:
    return seconds / 60 / 60


def _get_utc_timestamp_now() -> float:
    dt = datetime.now(timezone.utc)
    utc_time = dt.replace(tzinfo=timezone.utc)
    return utc_time.timestamp()


def _convert_datetime_to_utc_timestamp(dt: datetime) -> float:
    utc_time = dt.replace(tzinfo=timezone.utc)
    return utc_time.timestamp()


def blame(session: Session, user, text, channel) -> str:
    """
    The blame command returns a list of the top `num_of_user_to_return` users that have been in the queue in the past
    `blame_look_back_duration_days` days
    """
    num_of_user_to_blame = 3           # num of user that will be blamed
    blame_look_back_duration_days = 30  # num of days to look back for blame command
    q_duration_sum_label = "q_duration_sum"

    blame_look_back_duration_sec = _days_to_secs(blame_look_back_duration_days)
    look_back_timestamp = (_get_utc_timestamp_now() - blame_look_back_duration_sec)

    rows = session.query(Queue.user_id, func.sum(Queue.q_duration_s).label(q_duration_sum_label))\
        .filter(Queue.channel == channel).filter(Queue.created_at >= look_back_timestamp)\
        .group_by(Queue.user_id)\
        .order_by(desc(q_duration_sum_label))\
        .all()

    if not rows:
        return f"No one was in queue for the past {blame_look_back_duration_days} day, please dont forget about " \
               f"me :omer_sh: :crying_shock:"

    if len(rows) > num_of_user_to_blame:
        rows = rows[:num_of_user_to_blame]

    s = "Your top blamers are:\n"
    for (user, q_duration_s) in rows:
        hours_in_q = _sec_to_hours(q_duration_s)
        s += f"{user} with {hours_in_q} hours in queue :hourglass:\n"
    s += "no :coffee: breaks when you are in the queue"
    return s
