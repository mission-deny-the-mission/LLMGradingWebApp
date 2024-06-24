from flask_nav3 import Nav
from flask_nav3.elements import Navbar, View

nav = Nav()

nav.register_element('top', Navbar(
    View("Home", ".index"),
    View("Work list", ".work_list"),
    View("Upload work", ".upload_work"),
))
