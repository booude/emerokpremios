import app


def add_prize(name, prize, channel):
    b_id = app.db.session.query(app.Broadcaster).where(
        app.Broadcaster.twitch_id == channel).first()
    app.db.session.add(app.Prize(name=name, prize=prize,
                       broadcaster=b_id, checkAlert=True))
    app.db.session.commit()
    return
