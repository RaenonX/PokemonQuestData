from flask import session, render_template, url_for, request
from flask_nav import Nav
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator, RawTag

from data.thirdparty import identity_entry_uid_key

nav = Nav()

nav_items = [View("探險尋寶攻略情報站", "frontend.index"),
    View("首頁", "frontend.index"),
    Subgroup("資料查詢",
             View("查詢精靈資料", "frontend.pokemon_profile_index"),
             Separator(),
             View("從精靈查食譜", "frontend.find_recipe_index"),
             View("從食譜查精靈", "frontend.find_pokemon_index"),
             View("從技能查精靈", "frontend.poke_skill_index")),
    View("提交結果", "frontend_user.submit_result"),
    View("關於", "frontend.about")]

def append_dynamic(navitems):
    to_append = []

    if identity_entry_uid_key in session:
        to_append.append(
            Subgroup("我的資料",
                     View("我的開鍋紀錄", "frontend.recent_new_data_by_user", uid=session[identity_entry_uid_key]),
                     Separator(),
                     Text("精靈管理"),
                     View("我的精靈一覽", "frontend_user.view_owned_pokemon"),
                     View("新增我的精靈", "frontend_user.submit_owned_pokemon")))
    else:
        to_append.append(View("登記身分", "frontend_user.user_verify", prev=url_for("frontend.index")))

    return navitems + to_append

def register_element(nav, navitems):
    navitems = append_dynamic(navitems)
    return nav.register_element('main', Navbar(*navitems))

_render_template = render_template

def render_template(*args, **kwargs):
    register_element(nav, nav_items)

    return _render_template(*args, nav=nav.elems, **kwargs)