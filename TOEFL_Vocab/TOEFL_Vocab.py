import pandas as pd
import random
import os

# ========== 配置 ==========
FILE_NAME = 'toefl_vocab.xlsx'
WRONG_BOOK_FILE = 'toefl_错题本.xlsx'
# ===========================

# 读取所有工作表
xlsx = pd.ExcelFile(FILE_NAME)
sheet_names = xlsx.sheet_names

# 让用户选择一个 worksheet
print("📘 请选择一个词库（工作表名）进行练习：")
for i, name in enumerate(sheet_names):
    print(f"{i + 1}. {name}")
sheet_index = int(input("输入编号：")) - 1
sheet_name = sheet_names[sheet_index]

# 读取选择的词库
df = pd.read_excel(FILE_NAME, sheet_name=sheet_name, engine='openpyxl')

# 记录错题
wrong_list = []

def run_quiz(quiz_df, title="练习", batch_size=50):
    print(f"\n📝 开始：{title}（输入 q 退出）")
    total = len(quiz_df)
    quiz_df = quiz_df.sample(frac=1).reset_index(drop=True)  # 打乱顺序

    for start in range(0, total, batch_size):
        batch = quiz_df.iloc[start:start + batch_size]
        for index, row in batch.iterrows():
            chinese = row['中文意思']
            english_phrases = str(row['地道搭配']).lower().split('/')
            english_phrases = [e.strip() for e in english_phrases]

            print(f"\n🔹 中文意思：{chinese}")
            user_input = input("请输入英文表达：").strip().lower()

            if user_input == 'q':
                print("👋 提前退出。")
                return False

            if user_input in english_phrases:
                print("✅ 正确！参考答案：")
                for phrase in english_phrases:
                    print(f"   - {phrase}")
            else:
                print("❌ 不正确。参考答案：")
                for phrase in english_phrases:
                    print(f"   - {phrase}")
                wrong_list.append(row)


        # 分批控制：每50个一轮
        if start + batch_size < total:
            cont = input(f"\n✅ 已完成 {start + batch_size} / {total} 个，继续？(y/n)：").strip().lower()
            if cont != 'y':
                print("⏹️ 提前退出当前练习。")
                return False
    return True

def update_wrong_book(new_wrongs):
    if os.path.exists(WRONG_BOOK_FILE):
        existing = pd.read_excel(WRONG_BOOK_FILE, engine='openpyxl')
        combined = pd.concat([existing, new_wrongs])
    else:
        combined = new_wrongs.copy()

    # 统计错题频数
    combined['出错次数'] = 1
    combined = combined.groupby(['中文意思', '地道搭配']).agg({'出错次数': 'sum'}).reset_index()

    # 保存
    combined.to_excel(WRONG_BOOK_FILE, index=False)


while True:
    wrong_list = []
    df = pd.read_excel(FILE_NAME, sheet_name=sheet_name, engine='openpyxl')

    # 第一轮练习
    completed = run_quiz(df)

    # 错题复习
    if wrong_list:
        print("\n🔁 下面是错题复习：")
        wrong_df = pd.DataFrame(wrong_list).drop_duplicates()
        run_quiz(wrong_df, title="错题复习")

        # 记录错题本（带频数）
        update_wrong_book(wrong_df)
    else:
        print("\n🎉 全部答对！没有错题。")

    # 是否继续
    choice = input("\n📚 是否继续选择其他词库？(y继续 / q退出)：").strip().lower()
    if choice == 'q':
        print("👋 已退出。")
        break
    else:
        # 重新选择词表
        print("\n📘 可选词库：")
        for i, name in enumerate(sheet_names):
            print(f"{i + 1}. {name}")
        sheet_index = int(input("输入编号：")) - 1
        sheet_name = sheet_names[sheet_index]

