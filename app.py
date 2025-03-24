from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from models import db, User, Artikel
from forms import RegistrationForm, LoginForm, ChangePasswordForm, DeleteAccountForm, ArtikelForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("home"))  # Eingeloggte Benutzer gehen direkt auf /home
    return redirect(url_for("login"))  # Nicht eingeloggte Benutzer landen auf /login

@app.route("/home")
@login_required
def home():
    artikel = Artikel.query.all()
    form = ArtikelForm()
    return render_template("home.html", artikel=artikel, form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("E-Mail bereits registriert!", "warning")
            return redirect(url_for("register"))

        # Setzt automatisch die Rolle "user"
        user = User(email=form.email.data, role="user")  
        user.set_password(form.password.data)

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

            # Nach erfolgreichem Login zum Home-Screen weiterleiten
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

@app.route('/artikel')
@login_required
def artikel_liste():
    artikel = Artikel.query.all()
    return render_template('artikel_liste.html', artikel=artikel)

@app.route('/artikel/neu', methods=['POST'])
@login_required
def artikel_neu():
    form = ArtikelForm()
    if form.validate_on_submit():
        neuer_artikel = Artikel(
            name=form.name.data,
            menge=form.menge.data,
            kommentar=form.kommentar.data,
            user_id=current_user.id
        )
        db.session.add(neuer_artikel)
        db.session.commit()
        flash('Artikel hinzugefügt!', 'success')
        return redirect(url_for('artikel_liste'))
    return render_template('artikel_form.html', form=form)

@app.route('/artikel/<int:id>/bearbeiten', methods=['GET', 'POST'])
@login_required
def artikel_bearbeiten(id):
    artikel = Artikel.query.get_or_404(id)
    if artikel.user_id != current_user.id:
        flash('Keine Berechtigung.', 'danger')
        return redirect(url_for('artikel_liste'))
    
    form = ArtikelForm(obj=artikel)
    if form.validate_on_submit():
        artikel.name = form.name.data
        artikel.menge = form.menge.data
        artikel.kommentar = form.kommentar.data
        db.session.commit()
        flash('Artikel aktualisiert!', 'success')
        return redirect(url_for('artikel_liste'))
    return render_template('artikel_form.html', form=form)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")  # Nutzt jetzt die `profile.html`-Vorlage


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("✅ Erfolgreich ausgeloggt!", "success")
    return redirect(url_for("login"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # ➜ erstellt alle Tabellen, falls sie noch nicht existieren
    app.run(debug=True)