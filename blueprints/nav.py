from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator

nav = Nav()

nav.register_element("main", Navbar(
    View("Pokemon Quest資訊站", ".index"),
    View("首頁", ".index"),
    View("從精靈查食譜", ".find_recipe_index"),
    View("從食譜查精靈", ".find_pokemon_index"),
    View("提交結果", ".submit_result")))