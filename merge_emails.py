# merge_emails.py
import os
import pandas as pd
import glob

# --- Configuration ---
# 数据集根目录 (包含日期子文件夹的目录)
DATASET_ROOT_DIR = 'E:\\200_StudyArea\\210_curricularStudy\\216_junior_down\\02_vis_tech\\exp\\myProject\\public\\ITD-2018 Data Set'
# 合并后输出的文件名
MERGED_FILE_NAME = 'all_emails_merged.csv'
# 合并后的文件将保存在脚本运行的目录下，或者您可以指定一个完整路径

# 尝试的编码列表
encodings_to_try = ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']

def merge_email_data(root_path, output_file):
    all_email_dfs = []
    date_folders = [f for f in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, f))]
    
    print(f"找到 {len(date_folders)} 个日期子文件夹。开始查找并合并 email.csv 文件...")

    successful_reads = 0
    failed_reads = 0

    for date_folder in sorted(date_folders): # 按日期排序确保顺序
        email_file_path = os.path.join(root_path, date_folder, 'email.csv')
        if os.path.exists(email_file_path):
            df_email = None
            for encoding in encodings_to_try:
                try:
                    df_email = pd.read_csv(email_file_path, encoding=encoding)
                    print(f"成功读取: {email_file_path} (使用 {encoding} 编码, 包含 {len(df_email)} 行)")
                    all_email_dfs.append(df_email)
                    successful_reads += 1
                    break  # 成功读取后跳出编码尝试循环
                except UnicodeDecodeError:
                    # print(f"{encoding} 解码失败: {email_file_path}")
                    continue # 尝试下一个编码
                except Exception as e:
                    print(f"读取文件 {email_file_path} 时发生其他错误 (使用 {encoding}): {e}")
                    break # 发生其他错误，停止尝试此文件

            if df_email is None: # 如果所有编码都尝试失败
                print(f"警告: 文件 {email_file_path} 无法使用任何指定编码成功读取。")
                failed_reads +=1
        else:
            print(f"警告: 在文件夹 {date_folder} 中未找到 email.csv 文件。")

    if not all_email_dfs:
        print("没有找到任何 email.csv 文件或读取失败，无法合并。")
        return

    print(f"\n成功读取 {successful_reads} 个 email.csv 文件，失败 {failed_reads} 个。开始合并数据...")
    
    merged_df = pd.concat(all_email_dfs, ignore_index=True)
    
    # 可选：去重（基于所有列都相同才算重复）
    initial_rows = len(merged_df)
    merged_df.drop_duplicates(inplace=True)
    rows_removed = initial_rows - len(merged_df)
    if rows_removed > 0:
        print(f"移除了 {rows_removed} 行重复数据。")

    merged_df.to_csv(output_file, index=False, encoding='utf-8') # 统一用UTF-8保存
    print(f"\n所有 email 数据已成功合并到: {output_file} (总共 {len(merged_df)} 行)")

if __name__ == "__main__":
    merge_email_data(DATASET_ROOT_DIR, MERGED_FILE_NAME)