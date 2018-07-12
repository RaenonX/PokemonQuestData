import ex

class PokeType(ex.EnumWithName):
    BUG = 0, "蟲"
    DRAGON = 1, "龍"
    FAIRY = 2, "妖精"
    FIRE = 3, "火"
    GHOST = 4, "幽靈"
    GROUND = 5, "地面"
    NORMAL = 6, "一般"
    PSYCHIC = 7, "超能力"
    STEEL = 8, "鋼"
    DARK = 9, "惡"
    ELECTRIC = 10, "電"
    FIGHTING = 11, "格鬥"
    FLYING = 12, "飛行"
    GRASS = 13, "草"
    ICE = 14, "冰"
    POISON = 15, "毒"
    ROCK = 16, "岩石"
    WATER = 17, "水"

class RecipeQuality(ex.EnumWithName):
    NORMAL = 0, "普通"
    GOOD = 1, "好吃"
    VERY_GOOD = 2, "超好吃"
    SPECIAL = 3, "好吃到不行"

class RecipeItem(ex.EnumWithName):
    SMALL_RED = 1, "小紅"
    SMALL_BLUE = 2, "小藍"
    SMALL_YELLOW = 3, "小黃"
    SMALL_GRAY = 4, "小灰"
    SMALL_ALL = 5, "小(隨意)"
    LARGE_RED = 11, "大紅"
    LARGE_BLUE = 12, "大藍"
    LARGE_YELLOW = 13, "大黃"
    LARGE_GRAY = 14, "大灰"
    LARGE_ALL = 15, "大(隨意)"
    RAINBOW = 21, "彩石"
    SHELL = 22, "貝殼"

class BattleType(ex.EnumWithName):
    MELEE = 0, "近距離"
    RANGE = 1, "遠距離"

class SkillStone(ex.EnumWithName):
    STONE_CD = 0, "快快石"
    STONE_ADD = 1, "多多石"
    STONE_RANGE = 2, "展展石"
    STONE_MULTI = 3, "連連石"
    STONE_BUFF = 4, "團團石"
    STONE_TIME = 5, "恒恒石"