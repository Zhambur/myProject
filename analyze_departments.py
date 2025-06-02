# analyze_departments.py

import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'
os.environ['VECLIB_MAXIMUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'

import pandas as pd
import re
from collections import Counter
import jieba  # For Chinese word segmentation
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import numpy as np
import json # 新增：用于保存JSON

# --- Configuration ---
# 包含所有邮件数据的CSV文件路径 (由 merge_emails.py 生成)
MERGED_EMAILS_FILE = 'all_emails_merged.csv'
# 输出员工部门映射的文件名
OUTPUT_MAPPING_FILE = 'public/employee_department_mapping.csv'
OUTPUT_WORD_FREQUENCIES_FILE = 'public/employee_word_frequencies.json' # 新增：词频输出文件名

# 部门数量 (根据题目设定为3)
NUM_DEPARTMENTS = 3
TOP_N_WORDS_FOR_CLOUD = 30 # 新增：为每个用户保留的词云词数量

# 中文停用词列表 (您可以根据需要添加更多)
# 简单示例，实际应用中可能需要更完善的列表
STOPWORDS = set([
    '的', '了', '我', '你', '他', '她', '它', '们', '这', '那', '之', '与', '和', '或', '也',
    '中', '人', '在', '有', '是', '为', '就', '都', '说', '上', '下', '左', '右', '前', '后',
    '请', '谢谢', '关于', '问题', '通知', '回复', '转发', '答复', '您好', '你好', '嗨', 'hello',
    're', 'fw', 'fwd', '邮件', '主题', '发送', '收到', '抄送', '密送', '日期', '时间',
    '有限公司', '公司', '部门', '内部', '外部', '各位', '同事', '领导',
    '附件', '查看', '下载', '链接', '点击', '详情', '处理', '安排', '确认', '提交',
    '1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月',
    '周一', '周二', '周三', '周四', '周五', '周六', '周日',
    'nbsp', 'amp', 'quot', 'lt', 'gt', # HTML转义字符
    '此', '致', '此致', '敬礼', '一个', '一些', '什么', '哪个', '怎么', '如何', '何时', '何地',
    '年度', '季度', '月份', '工作', '报告', '计划', '总结', '分析', '测试', '系统', '平台', '项目'
])

# 需要排除的系统或通用发件人账号 (只取@符号前的部分)
SYSTEM_ACCOUNTS_PREFIXES = ['kaoqin', 'fuli', 'work', 'smail', 'ti', 'meeting', 'hr', 'allstaff', 'noreply']

def extract_user_id_from_email(email_address):
    """从邮件地址中提取用户ID (例如 '1234@hightech.com' -> '1234')"""
    if pd.isna(email_address) or not isinstance(email_address, str):
        return None
    # 首先检查是否是纯数字ID（没有@符号），这种认为是员工ID
    if '@' not in email_address:
        # 进一步验证是否是已知的系统账号，如果不是，则认为是员工ID
        if email_address.lower() not in SYSTEM_ACCOUNTS_PREFIXES:
            return email_address # 直接返回这个ID
        else:
            return None # 是系统账号前缀，排除

    # 如果包含@符号，尝试提取hightech.com域名的前缀
    match = re.match(r'^([^@]+)@hightech\.com$', email_address, re.IGNORECASE)
    if match:
        user_prefix = match.group(1)
        # 检查提取的前缀是否是系统账号
        if user_prefix.lower() not in SYSTEM_ACCOUNTS_PREFIXES:
            return user_prefix # 不是系统账号，返回提取的ID
        else:
            return None # 是系统账号，排除
    return None # 其他域名或格式不符的，排除

def preprocess_subject(subject):
    """预处理邮件主题：去除非中文字符、分词、去停用词"""
    if not isinstance(subject, str):
        return ""
    
    # 1. 移除非中文字符和常见标点 (保留字母和数字，因为某些项目名或术语可能包含)
    subject = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', '', subject)
    subject = subject.lower() # 转小写

    # 2. 使用jieba进行分词
    words = jieba.cut(subject)
    
    # 3. 去除停用词 和 单个字符的词 (除非是重要单个字母/数字，但这里简化处理)
    processed_words = [word for word in words if word not in STOPWORDS and len(word) > 1]
    
    return " ".join(processed_words)

def analyze_and_map_departments(emails_file, dept_mapping_file, word_freq_file):
    """加载邮件数据，进行聚类分析，并输出部门映射"""
    print(f"开始从 {emails_file} 加载邮件数据...")
    try:
        df_emails = pd.read_csv(emails_file, encoding='utf-8')
    except UnicodeDecodeError:
        print("UTF-8解码失败，尝试GBK...")
        try:
            df_emails = pd.read_csv(emails_file, encoding='gbk')
        except Exception as e:
            print(f"使用GBK解码也失败: {e}")
            return
    except FileNotFoundError:
        print(f"错误: 邮件数据文件 {emails_file} 未找到。请先运行 merge_emails.py。")
        return
    
    print(f"成功加载 {len(df_emails)} 条邮件记录。")

    # 提取发件人ID并筛选
    df_emails['extracted_sender_id'] = df_emails['from'].apply(extract_user_id_from_email)
    
    # 保留包含有效提取ID和主题的行
    df_filtered = df_emails.dropna(subset=['extracted_sender_id', 'subject']).copy()
    df_filtered.rename(columns={'extracted_sender_id': 'sender_id'}, inplace=True)
    # 确保 sender_id 是字符串类型，以便后续的 groupby 和可能的进一步处理
    df_filtered.loc[:, 'sender_id'] = df_filtered['sender_id'].astype(str)

    if df_filtered.empty:
        print("从邮件中未能提取到有效的员工发件人ID进行分析。")
        return
    
    print(f"筛选后剩余 {len(df_filtered)} 条有效发件人的邮件记录。")

    print("开始预处理邮件主题...")
    df_filtered.loc[:, 'processed_subject'] = df_filtered['subject'].apply(preprocess_subject)
    
    user_subjects_for_clustering = df_filtered.groupby('sender_id')['processed_subject'].apply(lambda x: ' '.join(x)).reset_index()
    user_subjects_for_clustering = user_subjects_for_clustering[user_subjects_for_clustering['processed_subject'].str.strip() != '']

    if user_subjects_for_clustering.empty:
        print("预处理后没有有效的用户主题数据进行聚类。")
        return
        
    print(f"共有 {len(user_subjects_for_clustering)} 名独立发件人参与聚类分析。")

    print("进行TF-IDF向量化...")
    vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, stop_words=list(STOPWORDS))
    tfidf_matrix = vectorizer.fit_transform(user_subjects_for_clustering['processed_subject'])

    if tfidf_matrix.shape[0] < NUM_DEPARTMENTS:
        print(f"错误：独立发件人数 ({tfidf_matrix.shape[0]}) 少于指定的聚类数 ({NUM_DEPARTMENTS})。无法进行聚类。")
        print("请检查SYSTEM_ACCOUNTS_PREFIXES或数据预处理步骤。")
        return

    print(f"进行K-Means聚类 (K={NUM_DEPARTMENTS})...")
    kmeans = KMeans(n_clusters=NUM_DEPARTMENTS, random_state=42, n_init=10)
    user_subjects_for_clustering['cluster'] = kmeans.fit_predict(tfidf_matrix)

    department_map = {
        0: '财务部',
        1: '研发部',
        2: '人力资源部'
    }
    user_subjects_for_clustering['department_name'] = user_subjects_for_clustering['cluster'].apply(lambda x: department_map.get(x, f'未知部门_{x}'))

    print("\n--- 各聚类代表性词语 ---")
    order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
    terms = vectorizer.get_feature_names_out()
    for i in range(NUM_DEPARTMENTS):
        print(f"Cluster {i} ({department_map.get(i, f'未知部门_{i}')}):")
        for ind in order_centroids[i, :20]:
            print(f"  {terms[ind]}", end='')
        print("\n")

    user_department_mapping = user_subjects_for_clustering[['sender_id', 'department_name', 'cluster']]
    print("\n--- 用户及其推断的部门（聚类标签和名称） ---")
    print(user_department_mapping)

    try:
        user_department_mapping.to_csv(dept_mapping_file, index=False, encoding='utf-8')
        print(f"\n员工部门映射已成功保存到: {dept_mapping_file}")
    except Exception as e:
        print(f"保存映射文件 {dept_mapping_file} 时发生错误: {e}")

    # --- 新增：为每个用户生成词频统计 ---
    print("\n正在为每个用户生成邮件主题词频统计...")
    employee_word_frequencies = {}
    # 我们需要原始的、每个员工的所有分词后的主题文本，而不是用于聚类的聚合文本
    # 所以重新 groupby `df_filtered` 来获取每个用户的 `processed_subject` 列表
    
    # 确保 processed_subject 列中的每个元素都是字符串
    df_filtered.loc[:, 'processed_subject'] = df_filtered['processed_subject'].astype(str)

    for sender_id, group in df_filtered.groupby('sender_id'):
        all_words_for_sender = []
        for subject_text in group['processed_subject']:
            all_words_for_sender.extend(subject_text.split()) # 按空格分割已处理的词语
        
        if all_words_for_sender:
            word_counts = Counter(all_words_for_sender)
            # 获取最高频的 TOP_N_WORDS_FOR_CLOUD 个词
            top_words = word_counts.most_common(TOP_N_WORDS_FOR_CLOUD)
            employee_word_frequencies[sender_id] = [{'name': word, 'value': count} for word, count in top_words]
        else:
            employee_word_frequencies[sender_id] = [] # 如果用户没有有效词语

    try:
        with open(word_freq_file, 'w', encoding='utf-8') as f:
            json.dump(employee_word_frequencies, f, ensure_ascii=False, indent=4)
        print(f"员工邮件主题词频已成功保存到: {word_freq_file}")
    except Exception as e:
        print(f"保存词频文件 {word_freq_file} 时发生错误: {e}")

    print("\n分析完成。")

if __name__ == "__main__":
    # 初始化jieba，避免首次运行时打印加载信息 (如果jieba版本支持)
    try:
        jieba.setLogLevel(20) # 对应 WARNING，减少不必要的INFO输出
    except AttributeError:
        pass # 老版本jieba可能没有setLogLevel
    analyze_and_map_departments(MERGED_EMAILS_FILE, OUTPUT_MAPPING_FILE, OUTPUT_WORD_FREQUENCIES_FILE)