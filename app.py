from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from models import db, User, Artikel
from forms import RegistrationForm, LoginForm, ChangePasswordForm, DeleteAccountForm, ArtikelForm
from config import Config
import secrets

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_user_from_token(token):
    if not token:
        return None
    return User.query.filter_by(token=token).first()

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    return redirect(url_for("login"))

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    form = ArtikelForm()

    if request.method == "POST":
        artikel_id = request.form.get("artikel_id")
        name = form.name.data.strip()

        if artikel_id:
            artikel = Artikel.query.get_or_404(artikel_id)
            duplicate = Artikel.query.filter(Artikel.name == name, Artikel.id != artikel.id).first()
            if duplicate:
                flash("⚠️ Ein Artikel mit diesem Namen existiert bereits!", "warning")
                return redirect(url_for("home"))

            if form.validate_on_submit():
                artikel.name = name
                artikel.menge = form.menge.data
                artikel.kommentar = form.kommentar.data
                db.session.commit()
                flash("✅ Artikel bearbeitet!", "success")
                return redirect(url_for("home"))

        else:
            duplicate = Artikel.query.filter_by(name=name).first()
            if duplicate:
                flash("⚠️ Ein Artikel mit diesem Namen existiert bereits!", "warning")
                return redirect(url_for("home"))

            if form.validate_on_submit():
                neuer_artikel = Artikel(
                    name=name,
                    menge=form.menge.data,
                    kommentar=form.kommentar.data,
                    user_id=current_user.id
                )
                db.session.add(neuer_artikel)
                db.session.commit()
                flash("✅ Artikel hinzugefügt!", "success")
                return redirect(url_for("home"))

    artikel = Artikel.query.all()
    return render_template("home.html", artikel=artikel, form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("E-Mail bereits registriert!", "warning")
            return redirect(url_for("register"))

        user = User(email=form.email.data, role="user")
        user.set_password(form.password.data)
        user.generate_token()
        db.session.add(user)
        db.session.commit()

        flash("Erfolgreich registriert! Bitte einloggen.", "success")
        return redirect(url_for("login"))

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{error}", "danger")

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Erfolgreich eingeloggt!", "success")
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))

        flash("❌ Login fehlgeschlagen! Falsche E-Mail oder Passwort.", "danger")

    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{error}", "danger")

    return render_template("login.html", form=form)

@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        flash("❌ Zugriff verweigert! Nur für Admins.", "danger")
        return redirect(url_for("profile"))

    return render_template("admin.html")

@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash("❌ Altes Passwort ist falsch!", "danger")
            return redirect(url_for("change_password"))

        current_user.set_password(form.new_password.data)
        db.session.commit()

        flash("✅ Passwort erfolgreich geändert!", "success")
        return redirect(url_for("profile"))

    return render_template("change_password.html", form=form)

@app.route("/delete_account", methods=["GET", "POST"])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if form.confirm.data != "LÖSCHEN":
            flash("⚠ Du musst 'LÖSCHEN' genau so eintippen, um fortzufahren!", "warning")
            return redirect(url_for("delete_account"))

        db.session.delete(current_user)
        db.session.commit()

        flash("✅ Dein Account wurde gelöscht!", "success")
        return redirect(url_for("login"))

    return render_template("delete_account.html", form=form)

@app.route("/artikel/<int:id>/loeschen", methods=["POST"])
@login_required
def artikel_loeschen(id):
    artikel = Artikel.query.get_or_404(id)
    db.session.delete(artikel)
    db.session.commit()
    flash("🗑️ Artikel wurde gelöscht.", "success")
    return redirect(url_for("home"))

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("✅ Erfolgreich ausgeloggt!", "success")
    return redirect(url_for("login"))

# ---------- API ----------

@app.route("/api/artikel", methods=["GET"])
def api_get_artikel():
    token = request.headers.get("Authorization")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    artikel = Artikel.query.all()
    daten = [
        {
            "id": a.id,
            "name": a.name,
            "menge": a.menge,
            "kommentar": a.kommentar,
            "user_id": a.user_id,
            "erstellt_am": a.erstellt_am.isoformat() if a.erstellt_am else None
        }
        for a in artikel
    ]
    return jsonify({"artikel": daten})

@app.route("/api/artikel/<int:id>", methods=["GET"])
def api_get_artikel_by_id(id):
    token = request.headers.get("Authorization")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    artikel = Artikel.query.get_or_404(id)
    return jsonify({
        "id": artikel.id,
        "name": artikel.name,
        "menge": artikel.menge,
        "kommentar": artikel.kommentar,
        "user_id": artikel.user_id,
        "erstellt_am": artikel.erstellt_am.isoformat() if artikel.erstellt_am else None
    })

@app.route("/api/artikel", methods=["POST"])
def api_create_artikel():
    token = request.headers.get("Authorization")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Kein JSON erhalten"}), 400

    name = data.get("name")
    menge = data.get("menge")
    kommentar = data.get("kommentar")

    if Artikel.query.filter_by(name=name).first():
        return jsonify({"error": "Artikelname bereits vorhanden"}), 409

    artikel = Artikel(name=name, menge=menge, kommentar=kommentar, user_id=user.id)
    db.session.add(artikel)
    db.session.commit()
    return jsonify({"message": "Artikel erstellt", "id": artikel.id}), 201

@app.route("/api/artikel/<int:id>", methods=["PUT"])
def api_update_artikel(id):
    token = request.headers.get("Authorization")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    artikel = Artikel.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Kein JSON erhalten"}), 400

    neuer_name = data.get("name")
    if neuer_name and neuer_name != artikel.name:
        if Artikel.query.filter(Artikel.name == neuer_name, Artikel.id != artikel.id).first():
            return jsonify({"error": "Artikelname bereits vergeben"}), 409

    artikel.name = neuer_name or artikel.name
    artikel.menge = data.get("menge", artikel.menge)
    artikel.kommentar = data.get("kommentar", artikel.kommentar)
    db.session.commit()
    return jsonify({"message": "Artikel aktualisiert"})

@app.route("/api/artikel/<int:id>", methods=["DELETE"])
def api_delete_artikel(id):
    token = request.headers.get("Authorization")
    user = get_user_from_token(token)
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    artikel = Artikel.query.get_or_404(id)
    db.session.delete(artikel)
    db.session.commit()
    return jsonify({"message": "Artikel gelöscht"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)