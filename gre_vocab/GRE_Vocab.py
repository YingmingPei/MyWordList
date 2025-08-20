import pandas as pd
import random
import os

# ========== 配置 ==========
FILE_NAME = 'gre_vocab.xlsx'     # 词库文件
WRONG_BOOK_FILE = 'GRE_错题本.xlsx'
# ===========================

wrong_list = []

def update_wrong_book(new_wrongs):
    """更新错题本，增加出错次数"""
    if os.path.exists(WRONG_BOOK_FILE):
        existing = pd.read_excel(WRONG_BOOK_FILE, engine='openpyxl')
        combined = pd.concat([existing, new_wrongs])
    else:
        combined = new_wrongs.copy()

    # 增加出错次数
    combined['出错次数'] = 1
    combined = combined.groupby(['英文', '中文']).agg({'出错次数': 'sum'}).reset_index()

    combined.to_excel(WRONG_BOOK_FILE, index=False)


def run_quiz_en2cn(quiz_df, title="英译中练习", batch_size=50):
    """英译中测试"""
    global wrong_list
    print(f"\n📝 开始：{title}（输入 q 退出）")
    total = len(quiz_df)
    # 不再这里打乱，顺序由 main() 决定
    quiz_df = quiz_df.reset_index(drop=True)

    for start in range(0, total, batch_size):
        batch = quiz_df.iloc[start:start + batch_size]
        for index, row in batch.iterrows():
            english = row['英文']
            chinese_answers = str(row['中文']).split('/')
            chinese_answers = [c.strip() for c in chinese_answers]

            print(f"\n🔹 英文：{english}")
            user_input = input("请输入中文意思：").strip()

            if user_input == 'q':
                print("👋 提前退出。")
                return False

            if user_input in chinese_answers:
                print("✅ 正确！其他可选答案：")
                for ans in chinese_answers:
                    if ans != user_input:
                        print(f"   - {ans}")
            else:
                print("❌ 不正确。参考答案：")
                for ans in chinese_answers:
                    print(f"   - {ans}")
                wrong_list.append(row)

        # 分批控制：每50个一轮
        if start + batch_size < total:
            cont = input(f"\n✅ 已完成 {start + batch_size} / {total} 个，继续？(y/n)：").strip().lower()
            if cont != 'y':
                print("⏹️ 提前退出当前练习。")
                return False
    return True


def main():
    global wrong_list

    # 读取 Excel 所有词表
    xlsx = pd.ExcelFile(FILE_NAME)
    sheet_names = xlsx.sheet_names

    while True:
        print("\n📘 请选择一个词库（工作表）：")
        for i, name in enumerate(sheet_names):
            print(f"{i + 1}. {name}")
        sheet_index = int(input("输入编号：")) - 1
        sheet_name = sheet_names[sheet_index]

        df = pd.read_excel(FILE_NAME, sheet_name=sheet_name, engine='openpyxl')

        # 按英文排序
        df = df.sort_values(by='英文').reset_index(drop=True)

        # 🔥 写回 Excel 文件（保持原有其他 sheet 不变）
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"✅ 已将 {sheet_name} 按英文排序，并写回 {FILE_NAME}")


        # 选择顺序模式
        order_choice = input("\n📑 选择测试顺序：1. 正序 (A-Z)  2. 乱序 ：").strip()
        if order_choice == '2':
            df = df.sample(frac=1).reset_index(drop=True)  # 打乱顺序

        wrong_list = []
        run_quiz_en2cn(df)

        if wrong_list:
            print("\n🔁 错题复习：")
            wrong_df = pd.DataFrame(wrong_list).drop_duplicates()
            run_quiz_en2cn(wrong_df, title="错题复习")

            # 保存错题本
            update_wrong_book(wrong_df)
            print(f"\n📥 错题已保存到：{WRONG_BOOK_FILE}")
        else:
            print("\n🎉 全部答对！没有错题。")

        choice = input("\n📚 是否继续选择其他词库？(y继续 / q退出)：").strip().lower()
        if choice == 'q':
            print("👋 已退出 GRE 词汇练习。")
            break


if __name__ == "__main__":
    main()
