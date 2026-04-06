import json
import sys
import random
from datetime import datetime, timedelta

DB_FILE = "review_db.json"

# 状态权重
WEIGHTS = {
    "star": 3,     # 完全不会 ⭐
    "mid": 2,      # 有思路 ⚠️
    "ok": 1        # 会做 ✅
}

# 复习间隔（天）
INTERVALS = [3, 7, 15]


def load_db():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []


def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def today():
    return datetime.now().date()


def add_question(title, status):
    data = load_db()

    q = {
        "title": title,
        "status": status,
        "stage": 0,  # 当前在第几轮复习
        "next_review": str(today() + timedelta(days=INTERVALS[0]))
    }

    data.append(q)
    save_db(data)
    print(f"✅ 已添加: {title}")


def list_questions():
    data = load_db()
    for q in data:
        print(q)


def get_due_questions():
    data = load_db()
    due = []

    for q in data:
        if datetime.strptime(q["next_review"], "%Y-%m-%d").date() <= today():
            due.append(q)

    return due


def weighted_sample(questions, k=2):
    if not questions:
        return []
    
    k = min(k, len(questions))
    selected = []
    candidates = list(questions)
    
    for _ in range(k):
        weights = [WEIGHTS.get(q["status"], 1) for q in candidates]
        chosen = random.choices(candidates, weights=weights, k=1)[0]
        selected.append(chosen)
        candidates.remove(chosen)
        
    return selected


def review_today():
    due = get_due_questions()

    if not due:
        print("🎉 今天没有需要复习的题")
        return

    selected = weighted_sample(due, 2)

    print("📚 今日复习题：")
    for q in selected:
        print("-", q["title"], f"[{q['status']}]")

def update_question(title, new_status):
    data = load_db()

    for q in data:
        if q["title"] == title:
            q["status"] = new_status

            # 推进复习阶段
            if q["stage"] < len(INTERVALS) - 1:
                q["stage"] += 1

            interval = INTERVALS[q["stage"]]
            q["next_review"] = str(today() + timedelta(days=interval))

            save_db(data)
            print(f"🔄 已更新: {title}")
            return

    print("❌ 未找到该题")


# ================= CLI =================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("================= 艾宾浩斯复习助手 =================\n")
        print("用法: python review.py <指令> [参数...]\n")
        print("可用指令:")
        print("  add <标题> <状态>    - 添加新题目到复习计划中。")
        print("                         状态可选值: star(重点/难点), mid(一般), ok(已掌握)")
        print("                         示例: python review.py add \"二叉树遍历\" star\n")
        print("  review               - 查看今天需要复习的所有题目。")
        print("                         示例: python review.py review\n")
        print("  update <标题> <状态> - 用于复习完毕后更新题目的掌握状态，并自动计算下一次复习时间。")
        print("                         状态可选值: star, mid, ok")
        print("                         示例: python review.py update \"二叉树遍历\" ok\n")
        print("  list                 - 列出题库中的所有题目及其当前状态和下次复习时间。")
        print("                         示例: python review.py list\n")
        print("====================================================")
        sys.exit()

    cmd = sys.argv[1]

    if cmd == "add":
        title = sys.argv[2]
        status = sys.argv[3]
        add_question(title, status)

    elif cmd == "review":
        review_today()

    elif cmd == "update":
        title = sys.argv[2]
        status = sys.argv[3]
        update_question(title, status)

    elif cmd == "list":
        list_questions()