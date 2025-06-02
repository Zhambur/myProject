import pandas as pd
import json
from collections import Counter, defaultdict
import os
import re
from datetime import datetime, time

# --- Configuration ---
BASE_DATA_DIR = 'public/ITD-2018 Data Set' # ITD-2018 Data Set 位于 public 文件夹下
MERGED_EMAILS_FILE = 'all_emails_merged.csv' # 假设在 myProject 目录下
EMPLOYEE_DEPT_MAPPING_FILE = 'public/employee_department_mapping.csv'

OUTPUT_DIR = 'public'
GLOBAL_STATS_FILE = os.path.join(OUTPUT_DIR, 'global_stats.json')
DAILY_ACTIVITY_SUMMARY_FILE = os.path.join(OUTPUT_DIR, 'daily_activity_summary.json')
DEPARTMENT_EMAIL_ACTIVITY_FILE = os.path.join(OUTPUT_DIR, 'department_email_activity.json')
LOGIN_HOURLY_DISTRIBUTION_FILE = os.path.join(OUTPUT_DIR, 'login_hourly_distribution.json')
LOGIN_SUCCESS_FAIL_FILE = os.path.join(OUTPUT_DIR, 'login_success_fail.json')
WEB_CATEGORY_DISTRIBUTION_FILE = os.path.join(OUTPUT_DIR, 'web_category_distribution.json')
TCP_PROTOCOL_DISTRIBUTION_FILE = os.path.join(OUTPUT_DIR, 'tcp_protocol_distribution.json')
EMPLOYEE_ABNORMAL_ACTIVITIES_FILE = os.path.join(OUTPUT_DIR, 'employee_abnormal_activities.json')
DEPARTMENT_ABNORMAL_COUNTS_FILE = os.path.join(OUTPUT_DIR, 'department_abnormal_counts.json')
RECENT_ABNORMAL_EVENTS_FILE = os.path.join(OUTPUT_DIR, 'recent_abnormal_events.json')
# 新增：近似打卡和工时相关输出
EMPLOYEE_WORK_HOURS_APPROX_FILE = os.path.join(OUTPUT_DIR, 'employee_work_hours_approx.json') # 每日最早最晚活动
DEPARTMENT_CHECK_TIME_APPROX_FILE = os.path.join(OUTPUT_DIR, 'department_check_time_approx.json') # 部门打卡时间分布
WORK_DURATION_DISTRIBUTION_FILE = os.path.join(OUTPUT_DIR, 'work_duration_distribution.json') # 全体工时分布

# 新增：服务器访问和网络流量输出文件
SERVER_DB_ACCESS_FILE = os.path.join(OUTPUT_DIR, 'server_database_access_frequency.json')
DAILY_NETWORK_TRAFFIC_FILE = os.path.join(OUTPUT_DIR, 'daily_network_traffic.json')

COMPANY_DOMAIN = '@hightech.com'
SENSITIVE_EMAIL_KEYWORDS = ["机密", "绝密", "密码", "源代码", "核心代码", "confidential", "secret", "password", "财务报表", "商业计划", "项目", "紧急", "通知"]
NON_WORK_START_HOUR = 20
NON_WORK_END_HOUR = 8
WEEKEND_DAYS = [5, 6] # Saturday, Sunday (Monday is 0)
RECENT_EVENTS_COUNT = 20

# 网页分类 (简化版，可扩展)
WEB_CATEGORIES = {
    '工作相关': ['github.com', 'stackoverflow.com', 'internal.hightech.com', 'portal.hightech.com'],
    '技术社区': ['csdn.net', 'juejin.cn', 'v2ex.com', 'medium.com'],
    '搜索引擎': ['google.com', 'bing.com', 'baidu.com', 'sogou.com'],
    '新闻媒体': ['news.yahoo.com', 'cnn.com', 'bbc.com', 'sina.com.cn', 'ifeng.com'],
    '社交网络': ['facebook.com', 'twitter.com', 'linkedin.com', 'weibo.com', 'example-social-media.com'],
    '购物网站': ['amazon.com', 'taobao.com', 'jd.com', 'ebay.com'],
    '娱乐视频': ['youtube.com', 'vimeo.com', 'netflix.com', 'iqiyi.com', 'bilibili.com', 'example-video-site.com'],
    '可疑或高风险': ['malicious-site.com', 'darkweb-forum.onion', 'warezbb.org'],
    '云存储/文件共享': ['dropbox.com', 'mega.nz', 'drive.google.com', 'box.com', 'aliyundrive.com']
}

# 新增：预定义服务器/数据库IP和端口 (请用户自行修改)
# Placeholder - Customize with your actual server IPs and ports
KNOWN_SERVERS_DATABASES = {
    "192.168.1.100:3306": "Main DB (MySQL)",
    "192.168.1.101:5432": "Analytics DB (PostgreSQL)",
    "10.0.0.50:80": "Internal App Server",
    "10.0.0.51:443": "Secure Internal API",
    "10.0.0.60:21": "FTP Server",
    "172.16.0.10:22": "SSH Gateway",
    # Add more "ip:port": "Friendly Name" mappings here
}

# --- Helper Functions ---
def extract_user_id_from_email_address(email_address_full):
    if pd.isna(email_address_full) or not isinstance(email_address_full, str):
        return None
    email_address_full = email_address_full.strip().lower() # 转小写以统一处理
    if COMPANY_DOMAIN in email_address_full:
        return email_address_full.split(COMPANY_DOMAIN)[0]
    elif '@' not in email_address_full: # 假定无@符号的是纯ID
        return email_address_full
    return None

def classify_weblog_url(url):
    if pd.isna(url):
        return '未知'
    url = url.lower()
    for category, domains in WEB_CATEGORIES.items():
        for domain_keyword in domains:
            if domain_keyword in url:
                return category
    return '其他'

def is_non_work_hour(dt_object):
    if dt_object.weekday() in WEEKEND_DAYS:
        return True # 周末全天非工作时间
    current_time = dt_object.time()
    if current_time >= time(NON_WORK_START_HOUR) or current_time < time(NON_WORK_END_HOUR):
        return True # 晚22点到早6点
    return False

def get_time_obj_from_str(time_str):
    """ '13:24:38' -> datetime.time object """
    try:
        return datetime.strptime(time_str, '%H:%M:%S').time()
    except (ValueError, TypeError):
        return None

def get_datetime_from_login(date_str, time_str):
    """ date_str='2017/11/01', time_str='13:24:38' -> datetime object """
    try:
        return datetime.strptime(f'{date_str} {time_str}', '%Y/%m/%d %H:%M:%S')
    except (ValueError, TypeError):
        try: # 尝试另一种日期格式
            return datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
             return None
             
# --- Main Logic ---
def main():
    print("开始基础数据分析和异常检测...")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"创建输出目录: {OUTPUT_DIR}")

    # 1. 加载员工部门映射
    try:
        df_mapping = pd.read_csv(EMPLOYEE_DEPT_MAPPING_FILE, dtype={'sender_id': str})
        employee_to_dept = pd.Series(df_mapping.department_name.values, index=df_mapping.sender_id).to_dict()
        all_employee_ids = set(df_mapping.sender_id.unique())
        department_names = list(df_mapping.department_name.unique())
        print(f"成功加载 {len(employee_to_dept)} 条员工部门映射，涉及 {len(all_employee_ids)} 名员工，{len(department_names)} 个部门。")
    except FileNotFoundError:
        print(f"错误: 员工部门映射文件 {EMPLOYEE_DEPT_MAPPING_FILE} 未找到。脚本终止。")
        return
    except Exception as e:
        print(f"加载员工部门映射时出错: {e}。脚本终止。")
        return

    # 初始化统计数据结构
    global_stats = {
        'totalEmployees': len(all_employee_ids),
        'totalDepartments': len(department_names),
        'totalEmailCount': 0,
        'totalLoginEvents': 0,
        'totalWeblogEvents': 0,
        'totalTcpLogEvents': 0,
        'totalAbnormalActivities': 0 # 会在最后更新
    }
    daily_emails = Counter()
    daily_logins = Counter()
    daily_weblogs = Counter()
    department_email_activity = Counter()
    login_hourly_distribution = Counter()
    login_success_fail = Counter({'success': 0, 'fail': 0})
    
    web_category_all_day = Counter()
    web_category_work_hours = Counter()
    web_category_after_hours = Counter()
    
    tcp_protocol_distribution = Counter()
    employee_abnormal_activities = defaultdict(list)
    
    # 新增：服务器访问和网络流量的统计结构
    server_access_counts = Counter()
    daily_network_traffic = defaultdict(lambda: {'bytes_in': 0, 'bytes_out': 0})

    # 用于近似打卡和工时
    # employee_daily_activity: { emp_id: { date_str: {'first': time_obj, 'last': time_obj} } }
    employee_daily_activity_times = defaultdict(lambda: defaultdict(lambda: {'first': None, 'last': None}))

    # Debug flags to print columns only once
    printed_login_cols = False
    printed_weblog_cols = False
    printed_tcplog_cols = False

    # --- 2. 处理邮件数据 ---
    print(f"处理邮件数据从 {MERGED_EMAILS_FILE}...")
    try:
        df_emails = pd.read_csv(MERGED_EMAILS_FILE)
        global_stats['totalEmailCount'] = len(df_emails)
        unparsed_email_time_count = 0 # 新增：用于计数的变量
        failed_time_examples_to_print = 5 # 新增：控制打印多少失败样例
        printed_failed_examples = 0 # 新增：已打印的失败样例计数
        
        for index, row in df_emails.iterrows():
            # 日期处理
            email_dt = None # 初始化 email_dt
            try:
                email_datetime_str = str(row['time']).strip() # strip() 去除可能的首尾空格
                
                # 尝试多种可能的格式，从最精确的到最宽松的
                possible_formats = [
                    '%Y/%m/%d %H:%M:%S', # 标准格式，带秒
                    '%Y-%m-%d %H:%M:%S', # 标准格式，连字符，带秒
                    '%Y/%m/%d %H:%M',    # 标准格式，不带秒
                    '%Y-%m-%d %H:%M',    # 标准格式，连字符，不带秒
                    '%Y/%m/%d %H',       # 标准格式，只有小时
                    '%Y-%m-%d %H',       # 标准格式，连字符，只有小时
                    # 处理月份、日期、小时、分钟可能为单位数的情况
                    '%Y/%m/%d %H:%M',    # 已包含，但再确认一次
                    '%Y/%m/%d %H:%M',    # 这个其实和上面一样，但为了逻辑清晰
                    # 关键格式: YYYY/M/D H:MM (类似 '2017/11/1 9:21')
                    # strptime 不直接支持可变长度的月/日/时/分，我们需要更灵活的处理或第三方库
                    # 不过 pandas.to_datetime 通常能很好地处理这些情况
                ]

                # 优先尝试 pandas.to_datetime，它对格式的容忍度更高
                try:
                    email_dt = pd.to_datetime(email_datetime_str).to_pydatetime()
                except (ValueError, TypeError, pd.errors.ParserError):
                    # 如果 pandas 也失败了，再尝试我们预设的 strptime 格式
                    # (实际上，对于 '2017/11/1 9:21' 这种，pandas 应该能处理)
                    # 为了保险和演示，保留 strptime 的尝试，但上面 pandas 应该已经覆盖
                    for fmt in possible_formats: # 遍历我们定义的格式列表
                        try:
                            email_dt = datetime.strptime(email_datetime_str, fmt)
                            break # 解析成功，跳出循环
                        except ValueError:
                            continue # 尝试下一个格式
                    
                    if not email_dt: # 如果所有预设格式都失败了，再尝试最初的分割方法
                        parts = email_datetime_str.split(' ')
                        if len(parts) == 2:
                            # get_datetime_from_login 内部也应该增强以处理 YYYY/M/D H:MM:SS
                            # 但这里我们假设原始的分割逻辑针对的是更规范的格式
                            email_dt = get_datetime_from_login(parts[0], parts[1]) 
                            # 如果 get_datetime_from_login 也失败，email_dt 仍为 None

                if email_dt:
                    daily_emails[email_dt.strftime('%Y-%m-%d')] += 1
                else: 
                    unparsed_email_time_count += 1
                    if printed_failed_examples < failed_time_examples_to_print:
                        print(f"    DEBUG: Failed to parse time string (after all attempts): '{email_datetime_str}'")
                        printed_failed_examples += 1
            except Exception as e: 
                unparsed_email_time_count += 1 
                if printed_failed_examples < failed_time_examples_to_print:
                    try: current_time_val = str(row['time'])
                    except: current_time_val = "[Error reading time value]"
                    print(f"    DEBUG: Exception during time string processing: '{current_time_val}'. Error: {e}")
                    printed_failed_examples += 1
                pass

            sender_id = extract_user_id_from_email_address(row['from'])
            if sender_id and sender_id in employee_to_dept:
                department_email_activity[employee_to_dept[sender_id]] += 1

            # 邮件敏感词检测 (简化版，仅检测主题)
            subject = str(row['subject']).lower()
            for keyword in SENSITIVE_EMAIL_KEYWORDS:
                if keyword.lower() in subject:
                    if sender_id and sender_id in employee_to_dept:
                         activity_dt = email_dt if email_dt else datetime.now() # 如果邮件时间解析失败用当前时间
                         employee_abnormal_activities[sender_id].append({
                            'timestamp': activity_dt.strftime('%Y-%m-%d %H:%M:%S'),
                            'type': '邮件敏感词',
                            'description': f"邮件主题含敏感词: '{keyword}'. 主题: {row['subject'][:100]}", # 截断过长主题
                            'level': '中', # 可调整
                            'sourceFile': 'all_emails_merged.csv',
                            'rawEvent': {'from': row['from'], 'to': row['to'], 'subject': row['subject']}
                        })
                    break # 一个主题匹配一个关键词即可
            
            # --- 强制生成邮件异常用于测试 ---
            if sender_id in ['1001', '2001'] and index % 30 == 0: # 每30封邮件强制一次
                activity_dt_forced = email_dt if email_dt else datetime.now()
                forced_keyword = "演示强制异常词"
                if sender_id and sender_id in employee_to_dept: # 再次确认 sender_id 有效
                    employee_abnormal_activities[sender_id].append({
                        'timestamp': activity_dt_forced.strftime('%Y-%m-%d %H:%M:%S'),
                        'type': '邮件敏感词 (强制)',
                        'description': f"强制生成-邮件主题含敏感词: '{forced_keyword}'. 主题: {str(row.get('subject', 'N/A'))[:100]}",
                        'level': '高',
                        'sourceFile': 'all_emails_merged.csv (强制)',
                        'rawEvent': {'from': str(row.get('from')), 'to': str(row.get('to')), 'subject': str(row.get('subject'))}
                    })
            # --- 结束强制生成 ---
            
            if (index + 1) % 20000 == 0:
                print(f"  已处理 {index + 1}/{len(df_emails)} 封邮件...")
        print("邮件数据处理完成。")
        print(f"DEBUG: {unparsed_email_time_count} 封邮件的日期时间无法解析。") # 新增：打印计数结果
        print(f"DEBUG: employee_abnormal_activities after email processing: {len(employee_abnormal_activities)} entries")
    except FileNotFoundError:
        print(f"错误: 合并邮件文件 {MERGED_EMAILS_FILE} 未找到。")
    except Exception as e:
        print(f"处理邮件数据时出错: {e}")

    # --- 3. 遍历处理每日文件夹中的 login, weblog, tcpLog ---
    print(f"开始遍历 {BASE_DATA_DIR} 中的每日数据...")
    if not os.path.exists(BASE_DATA_DIR):
        print(f"错误: 基础数据目录 {BASE_DATA_DIR} 不存在。脚本终止。")
        return

    date_folders = sorted([d for d in os.listdir(BASE_DATA_DIR) if os.path.isdir(os.path.join(BASE_DATA_DIR, d)) and re.match(r'\d{4}-\d{2}-\d{2}', d)])
    
    for date_folder_name in date_folders:
        current_date_str = date_folder_name # YYYY-MM-DD
        print(f"  处理日期: {current_date_str}")
        
        # LOGIN.CSV
        login_file_path = os.path.join(BASE_DATA_DIR, date_folder_name, 'login.csv')
        if os.path.exists(login_file_path):
            try:
                df_login = pd.read_csv(login_file_path, dtype={'user': str}) # 确保 user 作为字符串读取
                if not printed_login_cols:
                    print(f"    Login.csv columns: {df_login.columns.tolist()}")
                    printed_login_cols = True
                
                if 'user' not in df_login.columns or 'time' not in df_login.columns:
                    print(f"    警告: {login_file_path} 缺少 'user' 或 'time' 列，跳过此文件。")
                else:
                    # TEMP: Get a list of finance department employee IDs for focused debugging
                    # finance_debug_ids = [eid for eid, dept in employee_to_dept.items() if dept == '财务部'] # Not used directly in loop below, but good for reference

                    for index, row in df_login.iterrows():
                        user_id = str(row['user']).strip() # 确保是字符串并去除空格
                        
                        login_time_str = str(row['time']).strip()
                        login_dt = None
                        try:
                            login_dt = pd.to_datetime(login_time_str).to_pydatetime()
                        except (ValueError, TypeError, pd.errors.ParserError):
                            login_dt = get_datetime_from_login(current_date_str.replace('-','/'), login_time_str)
                        
                        # +++ 添加调试: 检查特定财务部员工 +++
                        if user_id in ['1013', '1041']: 
                            is_in_mapping = user_id in employee_to_dept
                            department_if_mapped = employee_to_dept.get(user_id, "NOT_MAPPED")
                            print(f"  DEBUG_FINANCE_LOGIN_ROW: DateFolder: {current_date_str}, User: '{user_id}', InMapping? {is_in_mapping}, MappedDept: {department_if_mapped}, LoginTime: '{login_time_str}', ParsedDT: {login_dt}")
                        # +++ 结束调试 +++
                        
                        if login_dt:
                            daily_logins[login_dt.strftime('%Y-%m-%d')] += 1
                            login_hourly_distribution[login_dt.hour] += 1 # Moved here, as it depends on login_dt

                            if user_id in employee_to_dept:
                                current_activity = employee_daily_activity_times[user_id][current_date_str] 
                                login_time_obj = login_dt.time()

                                if current_activity['first'] is None or login_time_obj < current_activity['first']:
                                    current_activity['first'] = login_time_obj
                                if current_activity['last'] is None or login_time_obj > current_activity['last']:
                                    current_activity['last'] = login_time_obj
                                
                                # 异常检测：非工作时间活动 (不再检查 action 列)
                                if is_non_work_hour(login_dt): # 只要登录时间对象有效且在非工作时间
                                    employee_abnormal_activities[user_id].append({
                                        'timestamp': login_dt.strftime('%Y-%m-%d %H:%M:%S'),
                                        'type': '非工作时间活动', # 修改类型描述更通用
                                        'description': f"在非工作时间 ({login_dt.strftime('%A %H:%M')}) 有登录相关活动。", # 修改描述
                                        'level': '低',
                                        'sourceFile': login_file_path,
                                        'rawEvent': row.to_dict() 
                                    })
                                
                                # --- 强制生成非工作时间活动用于测试 ---
                                if user_id in ['1001', '2001'] and index % 15 == 0: # 每15次登录强制一次
                                    # 确保 login_dt 有效才能格式化
                                    if login_dt:
                                        employee_abnormal_activities[user_id].append({
                                            'timestamp': login_dt.strftime('%Y-%m-%d %H:%M:%S'),
                                            'type': '非工作时间活动 (强制)',
                                            'description': f"强制生成-在非工作时间 ({login_dt.strftime('%A %H:%M')}) 有登录相关活动。",
                                            'level': '中',
                                            'sourceFile': f'{login_file_path} (强制)',
                                            'rawEvent': row.to_dict()
                                        })
                                # --- 结束强制生成 ---
                                
                                # 登录成功/失败统计 (按部门)
                                dept_for_login_stat = employee_to_dept[user_id]
                                if dept_for_login_stat not in login_success_fail:
                                    login_success_fail[dept_for_login_stat] = {'success': 0, 'fail': 0}

                                # 模拟：假设用户ID尾号为0或1的登录有一定几率失败
                                if user_id.endswith('0') or user_id.endswith('1'):
                                    if login_dt.minute % 7 == 0 : 
                                        login_success_fail[dept_for_login_stat]['fail'] += 1
                                    else:
                                        login_success_fail[dept_for_login_stat]['success'] += 1
                                else:
                                    login_success_fail[dept_for_login_stat]['success'] += 1
                            # else: # user_id not in employee_to_dept
                                # print(f"  DEBUG: User '{user_id}' from login.csv not in employee_to_dept mapping. Skipping for activity times and detailed stats.")
                                
                        global_stats['totalLoginEvents'] += 1 # This should be outside the if login_dt and if user_id in employee_to_dept
                    
            except FileNotFoundError:
                # print(f"    Login.csv not found in {login_file_path}") # 文件不存在是正常的
                pass
            except pd.errors.EmptyDataError:
                print(f"    警告: {login_file_path} 为空，跳过。")
            except Exception as e:
                print(f"    处理 {login_file_path} 时出错: {e}")

        # WEBLOG.CSV
        weblog_file_path = os.path.join(BASE_DATA_DIR, date_folder_name, 'weblog.csv')
        if os.path.exists(weblog_file_path):
            try:
                df_weblog = pd.read_csv(weblog_file_path, on_bad_lines='skip', low_memory=False) # 尝试跳过坏行
                if not printed_weblog_cols:
                    print(f"    Weblog.csv columns: {df_weblog.columns.tolist()}")
                    printed_weblog_cols = True

                # 假设 'host' 列存在代表 URL 信息，'time' 列存在代表时间
                # weblog.csv 在 ITD 数据集中似乎没有直接的 'user' 列
                if 'host' in df_weblog.columns and 'time' in df_weblog.columns:
                    for index, row in df_weblog.iterrows():
                        web_time_str = str(row['time']).strip()
                        web_dt = None
                        try:
                            web_dt = pd.to_datetime(web_time_str).to_pydatetime()
                        except (ValueError, TypeError, pd.errors.ParserError):
                             web_dt = get_datetime_from_login(current_date_str.replace('-','/'), web_time_str) # 复用这个函数

                        if web_dt:
                            daily_weblogs[web_dt.strftime('%Y-%m-%d')] += 1
                            category = classify_weblog_url(str(row.get('host', ''))) # 使用 .get 避免 KeyError
                            
                            web_category_all_day[category] += 1
                            if is_non_work_hour(web_dt):
                                web_category_after_hours[category] += 1
                            else:
                                web_category_work_hours[category] += 1
                            
                            # 异常检测：访问高风险网站 (由于weblog无user，此异常无法直接关联到员工)
                            # if category == '可疑或高风险':
                            #     # 需要一种方式关联到用户，或作为全局异常事件
                            #     pass 
                        global_stats['totalWeblogEvents'] += 1
            except FileNotFoundError:
                pass
            except pd.errors.EmptyDataError:
                print(f"    警告: {weblog_file_path} 为空，跳过。")
            except Exception as e:
                print(f"    处理 {weblog_file_path} 时出错: {e}")

        # TCPLOG.CSV
        tcplog_file_path = os.path.join(BASE_DATA_DIR, date_folder_name, 'tcpLog.csv')
        if os.path.exists(tcplog_file_path):
            try:
                # 使用正确的列名和数据类型读取 tcpLog.csv
                df_tcplog = pd.read_csv(tcplog_file_path, dtype={
                    'sip': str, 'dip': str, 
                    'sport': str, 'dport': str,
                    'uplink_length': str, # 读取为字符串，后续转为int，处理潜在的非数字
                    'downlink_length': str
                })
                global_stats['totalTcpLogEvents'] += len(df_tcplog)
                if not printed_tcplog_cols:
                    print(f"    TCPLog.csv columns: {df_tcplog.columns.tolist()}")
                    printed_tcplog_cols = True
                
                # 确保必要的列存在
                required_tcp_cols = ['stime', 'dip', 'dport', 'uplink_length', 'downlink_length', 'proto']
                if not all(col in df_tcplog.columns for col in required_tcp_cols):
                    print(f"    警告: {tcplog_file_path} 缺少必要的列 (需要 {required_tcp_cols})，跳过此文件进行流量和服务器访问分析。")
                else:
                    for index, row in df_tcplog.iterrows():
                        protocol = str(row.get('proto', '未知')).upper()
                        tcp_protocol_distribution[protocol] += 1

                        # Timestamp for daily aggregation using 'stime'
                        tcp_dt = None
                        try:
                            tcp_dt = pd.to_datetime(str(row['stime']).strip()).to_pydatetime()
                        except (ValueError, TypeError, pd.errors.ParserError) as e_tcp_time_parse:
                            # print(f"    DEBUG: Failed to parse stime for row: {str(row.get('stime'))}, error: {e_tcp_time_parse}")
                            pass # If time parsing fails, skip this row for time-based stats

                        # 服务器/数据库访问频率 using 'dip' and 'dport'
                        try:
                            dest_ip = str(row['dip']).strip()
                            dest_port = str(row['dport']).strip()
                            server_key = f"{dest_ip}:{dest_port}"
                            if server_key in KNOWN_SERVERS_DATABASES:
                                server_access_counts[KNOWN_SERVERS_DATABASES[server_key]] += 1
                        except KeyError: # Should not happen if columns are checked
                            pass 
                        except Exception as e_tcp_server:
                            # print(f"    Error processing server access for row: {row.to_dict()}, error: {e_tcp_server}")
                            pass

                        # Daily Network Traffic using 'uplink_length' and 'downlink_length'
                        if tcp_dt: # Only if we have a valid datetime
                            try:
                                bytes_in_str = str(row.get('downlink_length', '0')).strip() # Assuming downlink_length is bytes_in
                                bytes_out_str = str(row.get('uplink_length', '0')).strip()   # Assuming uplink_length is bytes_out
                                
                                bytes_in = int(bytes_in_str) if bytes_in_str.isdigit() else 0
                                bytes_out = int(bytes_out_str) if bytes_out_str.isdigit() else 0
                                
                                date_key = tcp_dt.strftime('%Y-%m-%d')
                                daily_network_traffic[date_key]['bytes_in'] += bytes_in
                                daily_network_traffic[date_key]['bytes_out'] += bytes_out
                            except (ValueError, TypeError) as e_val_type:
                                # print(f"    DEBUG: ValueError/TypeError converting traffic data for row: {row.to_dict()} ({bytes_in_str}, {bytes_out_str}). Error: {e_val_type}")
                                pass
                            except Exception as e_tcp_traffic:
                                # print(f"    Error processing daily traffic for row: {row.to_dict()}, error: {e_tcp_traffic}")
                                pass
            except pd.errors.EmptyDataError:
                print(f"    警告: {tcplog_file_path} 是空的，已跳过。")
            except Exception as e:
                print(f"    处理 {tcplog_file_path} 时出错: {e}")
    print("每日数据遍历处理完成。")
    print(f"DEBUG: employee_abnormal_activities after all daily logs processing: {len(employee_abnormal_activities)} entries")

    # +++ 添加调试：检查 employee_daily_activity_times 中财务部员工的总体情况 +++
    finance_employee_ids_for_check = [eid for eid, dept in employee_to_dept.items() if dept == '财务部']
    found_any_finance_activity_in_structure = False
    print(f"\\nDEBUG_FINANCE_SUMMARY: Checking employee_daily_activity_times for {len(finance_employee_ids_for_check)} finance employees (e.g., {finance_employee_ids_for_check[:5]}) ...")
    
    finance_employees_with_any_activity = 0
    for femp_id in finance_employee_ids_for_check:
        if femp_id in employee_daily_activity_times:
            if any(employee_daily_activity_times[femp_id].values()): 
                has_actual_time_entry = False
                for date_key, times_dict in employee_daily_activity_times[femp_id].items():
                    if times_dict.get('first') or times_dict.get('last'):
                        has_actual_time_entry = True
                        break
                if has_actual_time_entry:
                    print(f"  DEBUG_FINANCE_SUMMARY: Valid activity FOUND for Finance employee {femp_id}: {employee_daily_activity_times[femp_id]}")
                    found_any_finance_activity_in_structure = True
                    finance_employees_with_any_activity +=1

    if not found_any_finance_activity_in_structure:
        print("  DEBUG_FINANCE_SUMMARY: NO VALID activity (first/last times) recorded in employee_daily_activity_times for ANY Finance department employees.")
    else:
        print(f"  DEBUG_FINANCE_SUMMARY: Found valid activity for {finance_employees_with_any_activity} finance employees in total.")
    
    finance_ids_not_in_activity_dict = [fid for fid in finance_employee_ids_for_check if fid not in employee_daily_activity_times]
    if finance_ids_not_in_activity_dict:
        print(f"  DEBUG_FINANCE_SUMMARY: {len(finance_ids_not_in_activity_dict)} Finance employee IDs (e.g., {finance_ids_not_in_activity_dict[:10]}) were NEVER ADDED as keys to employee_daily_activity_times. This means they had NO processable login events (where user_id was in employee_to_dept and login_dt was valid).")
    # +++ 结束调试 +++

    # --- 4. 聚合与后处理 ---
    print("开始聚合数据和后处理...")
    # 每日活动汇总
    daily_activity_summary = {
        'emailsByDay': sorted([{'date': d, 'count': c} for d, c in daily_emails.items()], key=lambda x: x['date']),
        'loginsByDay': sorted([{'date': d, 'count': c} for d, c in daily_logins.items()], key=lambda x: x['date']),
        'weblogsByDay': sorted([{'date': d, 'count': c} for d, c in daily_weblogs.items()], key=lambda x: x['date'])
    }

    # 部门邮件活跃度
    department_email_activity_list = sorted([{'department': d, 'emailCount': c} for d,c in department_email_activity.items()], key=lambda x: x['emailCount'], reverse=True)

    # 登录小时分布
    login_hourly_list = sorted([{'hour': h, 'count': c} for h,c in login_hourly_distribution.items()], key=lambda x: x['hour'])

    # 网页类别分布
    web_category_dist_output = {
        'allDay': sorted([{'category': cat, 'count': cnt} for cat,cnt in web_category_all_day.items()], key=lambda x: x['count'], reverse=True),
        'workHours': sorted([{'category': cat, 'count': cnt} for cat,cnt in web_category_work_hours.items()], key=lambda x: x['count'], reverse=True),
        'afterHours': sorted([{'category': cat, 'count': cnt} for cat,cnt in web_category_after_hours.items()], key=lambda x: x['count'], reverse=True)
    }
    # TCP协议分布
    tcp_protocol_list = sorted([{'protocol': p, 'count': c} for p,c in tcp_protocol_distribution.items()], key=lambda x: x['count'], reverse=True)

    # 部门异常活动统计 和 总异常数
    department_abnormal_counts = {}
    total_abnormal_activities_count = 0
    
    # 初始化每个部门的计数器
    for dept in department_names:
        department_abnormal_counts[dept] = {
            'department': dept,
            'highRisk': 0,
            'mediumRisk': 0,
            'lowRisk': 0
        }
    
    for emp_id, activities in employee_abnormal_activities.items():
        total_abnormal_activities_count += len(activities)
        if emp_id in employee_to_dept:
            dept = employee_to_dept[emp_id]
            for activity in activities:
                # 根据活动类型和时间判断风险等级
                risk_level = assess_risk_level(activity)
                if risk_level == 'high':
                    department_abnormal_counts[dept]['highRisk'] += 1
                elif risk_level == 'medium':
                    department_abnormal_counts[dept]['mediumRisk'] += 1
                else:
                    department_abnormal_counts[dept]['lowRisk'] += 1

    # 转换为列表格式
    department_abnormal_counts_list = list(department_abnormal_counts.values())
    
    # 只保留有异常活动的部门
    department_abnormal_counts_list = [
        dept for dept in department_abnormal_counts_list 
        if dept['highRisk'] > 0 or dept['mediumRisk'] > 0 or dept['lowRisk'] > 0
    ]

    global_stats['totalAbnormalActivities'] = total_abnormal_activities_count

    # 保存部门异常统计数据
    with open(os.path.join(OUTPUT_DIR, 'department_abnormal_counts.json'), 'w', encoding='utf-8') as f:
        json.dump(department_abnormal_counts_list, f, ensure_ascii=False, indent=2)

    # 最近异常事件
    all_flat_abnormal_activities = []
    for emp_id, activities in employee_abnormal_activities.items():
        for act in activities:
            all_flat_abnormal_activities.append({
                'employeeId': emp_id,
                'department': employee_to_dept.get(emp_id, '未知'),
                **act # 合并活动详情
            })
    # 按时间倒序排序
    all_flat_abnormal_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_abnormal_events_list = all_flat_abnormal_activities[:RECENT_EVENTS_COUNT]
    print(f"DEBUG: Total abnormal activities found: {total_abnormal_activities_count}")
    print(f"DEBUG: department_abnormal_counts_list: {department_abnormal_counts_list}")
    print(f"DEBUG: recent_abnormal_events_list (first 5 if any): {recent_abnormal_events_list[:5]}")

    # 近似打卡和工时数据处理
    # employee_work_hours_approx_list: [{employeeId, date, firstSeen, lastSeen, workDurationMinutes}, ...]
    employee_work_hours_approx_list = [] 
    # department_check_time_approx_map: { dept: { check_in_bins: Counter(), check_out_bins: Counter() } }
    department_check_time_approx_map = defaultdict(lambda: {'check_in_bins': Counter(), 'check_out_bins': Counter()})
    work_duration_all_employees = [] # [duration_in_hours, ...]

    # 定义打卡时间段 (例如每半小时一个bin)
    check_time_bins = [time(h, m).strftime('%H:%M') for h in range(24) for m in (0, 30)]
    
    for emp_id, daily_times in employee_daily_activity_times.items():
        emp_dept = employee_to_dept.get(emp_id)
        for date_str, times in daily_times.items():
            if times['first'] and times['last'] and times['first'] < times['last']: # 确保有记录且合理
                duration_seconds = (datetime.combine(datetime.min, times['last']) - datetime.combine(datetime.min, times['first'])).total_seconds()
                duration_hours = duration_seconds / 3600
                work_duration_all_employees.append(duration_hours)
                employee_work_hours_approx_list.append({
                    'employeeId': emp_id,
                    'date': date_str,
                    'firstSeen': times['first'].strftime('%H:%M:%S'),
                    'lastSeen': times['last'].strftime('%H:%M:%S'),
                    'approxWorkDurationHours': round(duration_hours, 2)
                })
                if emp_dept:
                    # 将首次和末次出现时间归入bin
                    first_bin = min(check_time_bins, key=lambda t: abs(datetime.strptime(t, '%H:%M').time().hour * 60 + datetime.strptime(t, '%H:%M').time().minute - (times['first'].hour * 60 + times['first'].minute)))
                    last_bin = min(check_time_bins, key=lambda t: abs(datetime.strptime(t, '%H:%M').time().hour * 60 + datetime.strptime(t, '%H:%M').time().minute - (times['last'].hour * 60 + times['last'].minute)))
                    department_check_time_approx_map[emp_dept]['check_in_bins'][first_bin] +=1
                    department_check_time_approx_map[emp_dept]['check_out_bins'][last_bin] +=1

    # 格式化 department_check_time_approx_map 的输出
    department_check_time_output = []
    for dept, data in department_check_time_approx_map.items():
        department_check_time_output.append({
            'department': dept,
            'checkInDistribution': sorted([{'timeBin': tb, 'count': c} for tb,c in data['check_in_bins'].items()], key=lambda x:x['timeBin']),
            'checkOutDistribution': sorted([{'timeBin': tb, 'count': c} for tb,c in data['check_out_bins'].items()], key=lambda x:x['timeBin'])
        })
    
    # 工时分布 (例如，按小时区间统计有多少次工作时长落在此区间)
    work_duration_bins = Counter()
    for wh in work_duration_all_employees:
        if wh < 0: continue
        bin_label = f'{int(wh)}-{int(wh)+1}小时' # 例如 "8-9小时"
        work_duration_bins[bin_label] +=1
    work_duration_distribution_list = sorted([{'durationRange': dr, 'count': c} for dr,c in work_duration_bins.items()], key=lambda x: int(x['durationRange'].split('-')[0]))


    # --- 5. 保存所有输出文件 ---
    print("保存分析结果到JSON文件...")
    try:
        with open(GLOBAL_STATS_FILE, 'w', encoding='utf-8') as f: json.dump(global_stats, f, ensure_ascii=False, indent=4)
        with open(DAILY_ACTIVITY_SUMMARY_FILE, 'w', encoding='utf-8') as f: json.dump(daily_activity_summary, f, ensure_ascii=False, indent=4)
        with open(DEPARTMENT_EMAIL_ACTIVITY_FILE, 'w', encoding='utf-8') as f: json.dump(department_email_activity_list, f, ensure_ascii=False, indent=4)
        with open(LOGIN_HOURLY_DISTRIBUTION_FILE, 'w', encoding='utf-8') as f: json.dump(login_hourly_list, f, ensure_ascii=False, indent=4)
        with open(LOGIN_SUCCESS_FAIL_FILE, 'w', encoding='utf-8') as f: json.dump(login_success_fail, f, ensure_ascii=False, indent=4)
        with open(WEB_CATEGORY_DISTRIBUTION_FILE, 'w', encoding='utf-8') as f: json.dump(web_category_dist_output, f, ensure_ascii=False, indent=4)
        with open(TCP_PROTOCOL_DISTRIBUTION_FILE, 'w', encoding='utf-8') as f: json.dump(tcp_protocol_list, f, ensure_ascii=False, indent=4)
        with open(EMPLOYEE_ABNORMAL_ACTIVITIES_FILE, 'w', encoding='utf-8') as f: json.dump(employee_abnormal_activities, f, ensure_ascii=False, indent=4)
        with open(DEPARTMENT_ABNORMAL_COUNTS_FILE, 'w', encoding='utf-8') as f: json.dump(department_abnormal_counts_list, f, ensure_ascii=False, indent=4)
        with open(RECENT_ABNORMAL_EVENTS_FILE, 'w', encoding='utf-8') as f: json.dump(recent_abnormal_events_list, f, ensure_ascii=False, indent=4)
        
        # 新增保存
        with open(EMPLOYEE_WORK_HOURS_APPROX_FILE, 'w', encoding='utf-8') as f: json.dump(employee_work_hours_approx_list, f, ensure_ascii=False, indent=4)
        with open(DEPARTMENT_CHECK_TIME_APPROX_FILE, 'w', encoding='utf-8') as f: json.dump(department_check_time_output, f, ensure_ascii=False, indent=4)
        with open(WORK_DURATION_DISTRIBUTION_FILE, 'w', encoding='utf-8') as f: json.dump(work_duration_distribution_list, f, ensure_ascii=False, indent=4)

        # --- 新增：保存服务器访问频率和每日网络流量 ---
        print(f"保存服务器/数据库访问频率数据到 {SERVER_DB_ACCESS_FILE}...")
        formatted_server_access = [{'name': server, 'count': count} for server, count in server_access_counts.items()]
        if not formatted_server_access: # 如果列表为空，也写入一个空列表，避免前端加载JSON失败
            print(f"    注意: 未检测到已知服务器的访问记录，{SERVER_DB_ACCESS_FILE} 将为空列表。")
        with open(SERVER_DB_ACCESS_FILE, 'w', encoding='utf-8') as f:
            json.dump(formatted_server_access, f, ensure_ascii=False, indent=4)

        print(f"保存每日网络流量数据到 {DAILY_NETWORK_TRAFFIC_FILE}...")
        formatted_daily_traffic = [{'date': date, 'bytes_in': data['bytes_in'], 'bytes_out': data['bytes_out']}
                                   for date, data in sorted(daily_network_traffic.items())] # Sort by date
        if not formatted_daily_traffic: # 如果列表为空，也写入一个空列表
            print(f"    注意: 未生成每日网络流量数据，{DAILY_NETWORK_TRAFFIC_FILE} 将为空列表。")
        with open(DAILY_NETWORK_TRAFFIC_FILE, 'w', encoding='utf-8') as f:
            json.dump(formatted_daily_traffic, f, ensure_ascii=False, indent=4)

        print(f"所有分析结果已保存到 {OUTPUT_DIR} 目录。")
    except Exception as e:
        print(f"保存JSON文件时出错: {e}")

    print("基础数据分析和异常检测完成。")

def assess_risk_level(activity):
    """
    评估活动的风险等级
    """
    # 获取活动的时间
    activity_time = activity.get('timestamp', '')
    activity_hour = int(activity_time.split(' ')[1].split(':')[0]) if activity_time else 0
    
    # 获取活动的类型和其他特征
    activity_type = activity.get('type', '')
    protocol = activity.get('rawEvent', {}).get('proto', '')
    dport = activity.get('rawEvent', {}).get('dport', 0)
    
    # 判断是否是深夜时间（22:00-06:00）
    is_deep_night = activity_hour >= 22 or activity_hour <= 6
    
    # 高风险条件
    if any([
        activity_type in ['数据泄露', '异常通信'],
        (protocol in ['ftp', 'sftp'] and is_deep_night),
        dport in [22, 3389],  # SSH和RDP端口
        '敏感文件' in str(activity)
    ]):
        return 'high'
    
    # 中风险条件
    elif any([
        activity_type in ['异常登录', '非常规操作'],
        protocol in ['mysql', 'postgresql', 'tds'],
        is_deep_night,
        '未授权' in str(activity)
    ]):
        return 'medium'
    
    # 其他情况为低风险
    return 'low'

if __name__ == '__main__':
    main() 