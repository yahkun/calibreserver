from flask import Flask, render_template, session, request, redirect, url_for, send_from_directory, make_response
from cps import db
import os
from sqlalchemy.sql.expression import func


app = (Flask(__name__))



@app.route("/feed")
def feed_index():
    entries = db.session.query(db.Books).limit(50)
    xml = render_template('feed.xml', entries=entries)
    response= make_response(xml)
    response.headers["Content-Type"] = "application/xml"
    return response

@app.route("/")
def index():
    random = db.session.query(db.Books).order_by(func.random()).limit(6)
    entries = db.session.query(db.Books).limit(50)
    return render_template('index.html', random=random, entries=entries)

@app.route("/hot")
def hot_books():
    random = db.session.query(db.Books).order_by(func.random()).limit(6)
    entries = db.session.query(db.Books).filter(db.Books.ratings.any(db.Ratings.rating > 9)).limit(50)
    return render_template('index.html', random=random, entries=entries)

@app.route("/category/<name>")
def category(name):
    random = db.session.query(db.Books).order_by(func.random()).limit(6)
    if name != "all":
        entries = db.session.query(db.Books).filter(db.Books.tags.any(db.Tags.name.like("%" +name + "%" ))).all()
    else:
        entries = db.session.query(db.Books).all()
    return render_template('index.html', random=random, entries=entries)

@app.route("/admin/")
def admin():
    return "Admin ONLY!"

def title_sort(title):
    return title

@app.route("/search/<term>")
def search(term):
    pass
    #entries = db.sessions.query(db.Books).filter(db.Books.any)

@app.route("/author/<name>")
def author(name):
    entries = db.session.query(db.Books).filter(db.Books.authors.any(db.Authors.name.like("%" +  name + "%"))).all()
    return render_template('index.html', entries=entries)

@app.route("/cover/<path:cover_path>")
def get_cover(cover_path):
    return send_from_directory(os.path.join("/Users/workstation/Calibre Library", cover_path), "cover.jpg")

@app.route("/download/<path:dl_path>/<name>/<format>")
def get_download_link(dl_path, name, format):
    response = make_response(send_from_directory(os.path.join("/Users/workstation/Calibre Library", dl_path), name + "." +format))
    response.headers["Content-Disposition"] = "attachment; filename=%s.%s" % (name, format)
    return response

@app.route("/admin/book/<int:book_id>", methods=['GET', 'POST'])
def edit_book(book_id):
    book = db.session.query(db.Books).filter(db.Books.id == book_id).first()
    if request.method == 'POST':

        to_save = request.form.to_dict()
        print to_save
        #print title_sort(to_save["book_title"])
        book.title = to_save["book_title"]
        book.comments[0].text = to_save["description"]
        for tag in to_save["tags"].split(","):
            if tag.strip():
                print tag
                is_tag = db.session.query(db.Tags).filter(db.Tags.name.like('%' + tag.strip() + '%')).first()
                if is_tag:
                    book.tags.append(is_tag)
                else:
                    new_tag = db.Tags(name=tag.strip())
                    book.tags.append(new_tag)
        if to_save["series"].strip():
            is_series = db.session.query(db.Series).filter(db.Series.name.like('%' + to_save["series"].strip() + '%')).first()
            if is_series:
                book.series.append(is_series)
            else:
                new_series = db.Series(name=to_save["series"].strip(), sort=to_save["series"].strip())
                book.series.append(new_series)
        if to_save["rating"].strip():
            is_rating = db.session.query(db.Ratings).filter(db.Ratings.rating == int(to_save["rating"].strip())).first()
            if is_rating:
                book.ratings[0] = is_rating
            else:
                new_rating = db.Ratings(rating=int(to_save["rating"].strip()))
                book.ratings[0] = new_rating
        db.session.commit()
        return render_template('edit_book.html', book=book)
    else:
        return render_template('edit_book.html', book=book)

