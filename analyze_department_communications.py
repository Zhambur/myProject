import pandas as pd
import json
from collections import Counter, defaultdict
import os

# --- Configuration ---
MERGED_EMAILS_FILE = 'all_emails_merged.csv'
EMPLOYEE_DEPT_MAPPING_FILE = 'public/employee_department_mapping.csv' # 已移至public
OUTPUT_NODES_FILE = 'public/department_relation_nodes.json'
OUTPUT_LINKS_FILE = 'public/department_relation_links.json'

# 邮件地址域名
COMPANY_DOMAIN = '@hightech.com'

def extract_user_id_from_email_address(email_address_full):
    """从 \'user_id@domain\' 或 \'user_id\' 提取 user_id"""
    if pd.isna(email_address_full) or not isinstance(email_address_full, str):
        return None
    email_address_full = email_address_full.strip()
    if COMPANY_DOMAIN in email_address_full:
        return email_address_full.split(COMPANY_DOMAIN)[0]
    # 如果没有 @hightech.com，但也没有其他@符号，则认为它就是用户ID
    # （例如，login.csv中的user字段可能就是纯ID）
    elif '@' not in email_address_full:
        return email_address_full
    return None # 其他域名或格式不符的

def main():
    print("开始分析部门间邮件通讯...")

    # 1. 加载员工部门映射
    try:
        df_mapping = pd.read_csv(EMPLOYEE_DEPT_MAPPING_FILE, dtype={'sender_id': str})
        # 创建 employee_id -> department_name 的映射
        employee_to_dept = pd.Series(df_mapping.department_name.values, index=df_mapping.sender_id).to_dict()
        print(f"成功加载 {len(employee_to_dept)} 条员工部门映射。")
        
        # 统计各部门人数
        department_member_counts = df_mapping.groupby('department_name').size().to_dict()

    except FileNotFoundError:
        print(f"错误: 员工部门映射文件 {EMPLOYEE_DEPT_MAPPING_FILE} 未找到。")
        return
    except Exception as e:
        print(f"加载员工部门映射时出错: {e}")
        return

    # 2. 加载合并后的邮件数据
    try:
        df_emails = pd.read_csv(MERGED_EMAILS_FILE)
        print(f"成功加载 {len(df_emails)} 条邮件记录。")
    except FileNotFoundError:
        print(f"错误: 合并邮件文件 {MERGED_EMAILS_FILE} 未找到。请先运行 merge_emails.py。")
        return
    except Exception as e:
        print(f"加载邮件数据时出错: {e}")
        return

    department_email_counts = defaultdict(int) # 每个部门参与的邮件总数（发送或接收）
    inter_department_links = defaultdict(int)  # {('DeptA', 'DeptB'): count}

    print("处理邮件，分析部门间通讯...")
    for index, row in df_emails.iterrows():
        sender_full = row['from']
        recipients_full = row['to']

        sender_id = extract_user_id_from_email_address(sender_full)
        
        if not sender_id or sender_id not in employee_to_dept:
            continue # 发件人非公司员工或不在映射中

        sender_dept = employee_to_dept[sender_id]
        department_email_counts[sender_dept] += 1 # 发件部门邮件计数

        if pd.isna(recipients_full):
            continue

        recipient_list = str(recipients_full).split(';')
        processed_recipient_depts_for_this_email = set() # 避免同一封邮件内部同一部门多次计数

        for recip_full in recipient_list:
            recip_id = extract_user_id_from_email_address(recip_full.strip())
            if recip_id and recip_id in employee_to_dept:
                recip_dept = employee_to_dept[recip_id]
                
                if recip_dept not in processed_recipient_depts_for_this_email:
                    department_email_counts[recip_dept] += 1 # 收件部门邮件计数
                    processed_recipient_depts_for_this_email.add(recip_dept)

                if sender_dept != recip_dept:
                    # 为了避免方向性导致重复链接 (DeptA-DeptB vs DeptB-DeptA)，对部门名称排序
                    dept_pair = tuple(sorted((sender_dept, recip_dept)))
                    inter_department_links[dept_pair] += 1
        
        if (index + 1) % 10000 == 0:
            print(f"已处理 {index + 1}/{len(df_emails)} 封邮件...")

    # 3. 准备节点数据
    nodes_output = []
    for dept_name, total_emails in department_email_counts.items():
        nodes_output.append({
            "id": dept_name, # Echarts graph的data项通常用name，但id也可以
            "name": dept_name,
            "value": total_emails, # 代表邮件活跃度
            "memberCount": department_member_counts.get(dept_name, 0),
            # 'category' 可以根据部门类型设定，这里简化
        })
    
    # 4. 准备链接数据
    links_output = []
    for (dept_a, dept_b), count in inter_department_links.items():
        links_output.append({
            "source": dept_a,
            "target": dept_b,
            "value": count # 代表通讯强度
        })

    # 5. 保存到JSON文件
    try:
        with open(OUTPUT_NODES_FILE, 'w', encoding='utf-8') as f:
            json.dump(nodes_output, f, ensure_ascii=False, indent=4)
        print(f"部门节点数据已保存到: {OUTPUT_NODES_FILE}")

        with open(OUTPUT_LINKS_FILE, 'w', encoding='utf-8') as f:
            json.dump(links_output, f, ensure_ascii=False, indent=4)
        print(f"部门连接数据已保存到: {OUTPUT_LINKS_FILE}")
    except Exception as e:
        print(f"保存JSON文件时出错: {e}")

    print("部门间邮件通讯分析完成。")

if __name__ == '__main__':
    main() 